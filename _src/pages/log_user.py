import asyncio
import streamlit as st
import bcrypt
import asyncpg
import nest_asyncio
from contextlib import asynccontextmanager
import time
nest_asyncio.apply()

# ----- Асинхронное подключение к базе данных -----
@asynccontextmanager
async def connect_to_db():
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


async def add_customer(username, role, password):
    async with connect_to_db() as conn:
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO customers (name, role, password, balance) VALUES ($1, $2, $3, $4)",
                username, role, password, 0
            )
            st.success("Пользователь добавлен успешно.")



def hashed_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def check_customer(username):
    async with connect_to_db() as conn:
        query = '''SELECT * 
                   FROM customers 
                   JOIN roles ON customers.ROLE = roles.id
                   WHERE name = $1'''
        user = await conn.fetchrow(query, username)
        return user


# ----- Интерфейс приложения -----
def login_form():
    st.title("Вход в приложение")

    with st.form(key='login'):
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        login_button = st.form_submit_button("Войти")

        if login_button:
            user_data = asyncio.run(check_customer(username))
            if user_data:
                stored_password = user_data[3]
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user_data[2]
                    st.session_state['role'] = user_data[6]
                    st.session_state['username'] = username
                    st.success("Вы успешно вошли!")
                    st.rerun()
                else:
                    st.error("Неверный пароль.")
            else:
                st.error("Пользователь не найден.")

def registration_form():
    st.title("Регистрация пользователя")

    ban_chars = [' ', '\t', '\n']
    with st.form(key='register'):
        new_username = st.text_input("Новое Имя Пользователя")
        new_password = st.text_input("Новый Пароль", type="password")
        enter_password_again = st.text_input("Повторите пароль", type="password")
        register_button = st.form_submit_button("Зарегистрироваться")

        if register_button:
            for c in new_username:
                if c in ban_chars:
                    st.error("Не используйте в имени пользователя пробелы и знаки табуляции")
                    time.sleep(3)
                    st.rerun()
            for c in new_password:
                if c in ban_chars:
                    st.error("Не используйте в пароле пользователя пробелы и знаки табуляции")
                    time.sleep(3)
                    st.rerun()
            if new_password != enter_password_again:
                st.error("Пароли не совпадают, попробуйте снова.")
            else:
                hash_pw = hashed_password(new_password)
                asyncio.run(add_customer(new_username, 1, hash_pw))


def log_out():
    st.session_state['logged_in'] = False
    st.rerun()