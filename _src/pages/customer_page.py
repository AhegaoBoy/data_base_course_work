import asyncio
from contextlib import asynccontextmanager
import streamlit as st
import asyncpg

@asynccontextmanager
async def get_connection():
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


async def get_user_data(user_id):
    async with get_connection() as conn:
        query = '''SELECT * 
                              FROM customers 
                              JOIN roles ON customers.ROLE = roles.id
                              WHERE customers.id = $1'''
        user_data = await conn.fetchrow(query, user_id)
        return user_data


async def update_balance(user_id, new_balance):
    """Функция для изменения баланса пользователя."""
    async with get_connection() as conn:
        await conn.execute(
            "UPDATE customers SET balance = $1 WHERE id = $2",
            new_balance, user_id
        )
        st.success("Баланс успешно обновлен!")
        await asyncio.sleep(5)
        st.rerun()

async def get_last_order(user_id):
    """Возвращает последний оплаченный заказ пользователя."""
    async with get_connection() as conn:
        query = """SELECT id 
                    FROM orders 
                    WHERE customer_id = $1 AND order_state = 'оплачен' 
                    ORDER BY order_date DESC 
                    LIMIT 1"""
        last_order = await conn.fetchrow(query, user_id)
        return last_order


async def get_order_items(order_id):
    """Возвращает товары из указанного заказа."""
    async with get_connection() as conn:
        query = """SELECT product_id, quantity, unitprice, name
                   FROM order_items oi
                   JOIN products p ON oi.product_id = p.id
                   WHERE order_id = $1"""
        items = await conn.fetch(query, order_id)
        return items



async def check_if_review_exists(customer_id, product_id):
    """Проверяет, был ли оставлен отзыв на конкретный товар."""
    async with get_connection() as conn:
        query = "SELECT id FROM reviews WHERE customer_id = $1 AND product_id = $2"
        review = await conn.fetchrow(query, customer_id, product_id)
        return review is not None


async def add_review(customer_id, product_id, rate, review_text):
    """Добавление отзыва в базу данных."""
    async with get_connection() as conn:
        query = """
                            INSERT INTO reviews (product_id, customer_id, rate, comment, date) 
                            VALUES ($1, $2, $3, $4, DATE_TRUNC('minute', NOW()))
                        """

        await conn.execute(query, product_id, customer_id, rate, review_text)

        st.success("Ваш отзыв успешно добавлен!")
        await asyncio.sleep(10)
        st.rerun()


def profile_page():
    st.title("Страница вашего профиля")
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username')
    role = st.session_state.get('role')

    if role == 'customer':
        role = 'Пользователь'
    elif role == 'manager':
        role = 'менеджер'
    else:
        role = 'администратор'

    st.subheader("Информация")
    st.write(f"{role} ID: {user_id}")
    st.write(f"Имя профиля: {username}")


    st.subheader("Ваш баланс")
    current_balance = asyncio.run(get_user_data(user_id))[4]

    st.write(f"Текущий баланс: {current_balance}")
    new_balance = st.number_input("Введите новый баланс:", min_value=0.0, value=float(current_balance), step=1.0)

    if st.button("Обновить баланс"):
        asyncio.run(update_balance(user_id, new_balance))

    st.subheader("Ваши товары из последнего заказа")
    last_order = asyncio.run(get_last_order(user_id))

    if last_order:
        order_id = last_order['id']
        purchased_items = asyncio.run(get_order_items(order_id))

        if purchased_items:
            for item in purchased_items:
                product_id, quantity, unitprice, product_name = item['product_id'], item['quantity'], item['unitprice'], item['name']
                st.write(f"Название товара: {product_name}\nКоличество: {quantity}\nЦена за единицу: {unitprice}$")

                if not asyncio.run(check_if_review_exists(user_id, product_id)):

                    with st.form(key=f"review_form_{product_id}_{order_id}"):
                        rate = st.slider("Оценка (1-5 звезд):", 1, 5, 5)
                        review_text = st.text_area("Оставьте отзыв:")

                        if st.form_submit_button("Отправить отзыв"):
                            asyncio.run(add_review(user_id, product_id, rate, review_text))
                else:
                    st.write("Вы уже оставили отзыв на этот товар.")
    else:
        st.write("У вас нет оплаченных заказов.")