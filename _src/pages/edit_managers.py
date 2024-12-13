import streamlit as st
import asyncpg
import asyncio
from contextlib import asynccontextmanager


# Функция для подключения к БД
@asynccontextmanager
async def get_db_connection():
    conn = None
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="password"
        )
        yield conn
    finally:
        if conn:
            await conn.close()


# Функция для получения текущих пользователей
async def fetch_users():
    async with get_db_connection() as conn:
        query = '''SELECT *
                        FROM (
        		              SELECT c.id AS user_id, r.role AS _role, c.name AS name
        		              FROM customers c
        		              JOIN roles r
        		              ON c.role = r.id)'''
        result = await conn.fetch(query)
        return result



# Функция для обновления роли пользователя
async def update_user_role(user_id, new_role):
    async with get_db_connection() as conn:
        query = "UPDATE customers SET role = $1 WHERE id = $2"
        await conn.execute(
            query, new_role, user_id
        )


# Определение страницы Streamlit
def manager_page():
    st.title("Управление менеджерами")

    # Загружаем всех пользователей из базы
    users = asyncio.run(fetch_users())

    # Интерфейс таблицы с пользователями
    if users:
        st.subheader("Список сотрудников:")
        for user in users:
            col1, col2, col3 = st.columns([1, 4, 2])

            with col1:
                st.write(f"ID: {user['user_id']}")
            with col2:
                st.write(f"{user['name']} (Role: {user['_role']})")
            with col3:
                if user["_role"] == 'customer':  # Обычный сотрудник
                    if st.button(f"Назначить менеджером", key=f"make_manager_{user['user_id']}"):
                        asyncio.run(update_user_role(user["user_id"], 2))
                        st.rerun()
                elif user["_role"] == 'manager':  # Менеджер
                    if st.button(f"Снять права менеджера", key=f"remove_manager_{user['user_id']}"):
                        asyncio.run(update_user_role(user["user_id"], 1))
                        st.rerun()
    else:
        st.warning("Нет доступных сотрудников в базе данных.")