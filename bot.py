import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatMemberUpdated
from aiogram.utils import executor

API_TOKEN = '7517914722:AAHb8ITQyfd_anlG3yQNKWlI071loV9fdKM'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Подключаемся к SQLite и создаём таблицу, если нет
conn = sqlite3.connect('banned_users.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS banned_users (
    user_id INTEGER PRIMARY KEY
)
''')
conn.commit()

def add_user_to_db(user_id: int):
    cursor.execute('INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)', (user_id,))
    conn.commit()

def is_user_in_db(user_id: int) -> bool:
    cursor.execute('SELECT 1 FROM banned_users WHERE user_id = ?', (user_id,))
    return cursor.fetchone() is not None

@dp.chat_member_handler()
async def on_chat_member_update(chat_member_update: ChatMemberUpdated):
    user_id = chat_member_update.from_user.id
    new_status = chat_member_update.new_chat_member.status
    old_status = chat_member_update.old_chat_member.status
    chat_id = chat_member_update.chat.id

    # Пользователь вышел из канала
    if old_status in ['member', 'administrator'] and new_status in ['left', 'kicked']:
        add_user_to_db(user_id)
        print(f"Пользователь {user_id} добавлен в базу запрета.")

    # Пользователь зашёл в канал
    if old_status in ['left', 'kicked'] and new_status == 'member':
        if is_user_in_db(user_id):
            try:
                await bot.ban_chat_member(chat_id, user_id)
                print(f"Пользователь {user_id} удалён из канала, так как он есть в базе.")
            except Exception as e:
                print(f"Ошибка при удалении пользователя {user_id}: {e}")

if __name__ == '__main__':
    print("Бот запущен")
    executor.start_polling(dp)
