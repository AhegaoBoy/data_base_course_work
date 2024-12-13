import time
import asyncio
import asyncpg
import streamlit as st
from contextlib import asynccontextmanager

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

async def get_user_balance(user_id):
    async with get_db_connection() as conn:
        query = '''SELECT balance
                   FROM customers
                   WHERE id =$1'''
        result = await conn.fetch(query, user_id)

        return result[0]['balance']


async def update_user_balance(user_id, balance):
    async with get_db_connection() as conn:
        query = '''UPDATE customers
                   SET balance = $1
                   WHERE id = $2'''
        await conn.execute(query, balance, user_id)


async def fetch_product_by_id(product_id):
    async with get_db_connection() as conn:
        query = '''SELECT id, name, description, price, stock_quantity FROM products WHERE id = $1'''

        rows = await conn.fetch(query, product_id)
        result = [dict(row) for row in rows]
        return result


async def load_cart_from_database(order_id):
    """Загрузка содержимого корзины из таблицы order_items в st.session_state.cart."""
    async with get_db_connection() as conn:
        query = """
            SELECT product_id, quantity, unitprice
            FROM order_items
            WHERE order_id = $1
        """

        rows = await conn.fetch(query, (order_id,))

    cart = {}
    for row in rows:
        product = await fetch_product_by_id(row['product_id'])  # Реализуйте эту функцию, если её нет
        cart[row['product_id']] = {
            'name': product['name'],
            'price': row['unitprice'],
            'quantity': row['quantity']
        }

    st.session_state.cart = cart  # Сохраняем корзину в session_state

async def create_new_order(customer_id):
    """Создание новой строки в таблице orders."""
    async with get_db_connection() as conn:
        query = """
            INSERT INTO orders (customer_id, order_date, order_summ, order_state)
            VALUES ($1, DATE_TRUNC('minute', NOW()), $2, $3)
            RETURNING id
        """
        # await conn.execute(query, (customer_id, 0, 'в обработке'))  # Сумма заказа пока нулевая
        results = await conn.fetch(query, customer_id, 0, 'в обработке')

        # Вытаскиваем id из первой строки результата
        return results[0]['id'] if results else None


async def remove_item_from_order(order_id, product_id):
    """Удаление строки товара из order_items."""
    async with get_db_connection() as conn:
        query = """
            DELETE FROM order_items
            WHERE order_id = $1 AND product_id = $2
        """
        await conn.execute(query, order_id, product_id)

async def update_item_quantity(order_id, product_id, new_quantity):
    """Обновление количества товара в order_items."""
    async with get_db_connection() as conn:
        query = """
            UPDATE order_items
            SET quantity = $1
            WHERE order_id = $2 AND product_id = $3
        """
        await conn.execute(query, new_quantity, order_id, product_id)


async def update_order_summary(order_id):
    """Обновление общей суммы в таблице orders."""
    async with get_db_connection() as conn:
        query = """
            UPDATE orders
            SET order_summ = (
                SELECT SUM(quantity * unitprice)
                FROM order_items
                WHERE order_id = $1
            )
            WHERE id = $1
        """
        await conn.execute(query, order_id)


async def update_product_quantity(product_id, quantity_purchased):
    """Обновление количества товара на складе после покупки."""
    async with get_db_connection() as conn:
        query = """     UPDATE products
                        SET stock_quantity = stock_quantity - $1
                        WHERE id = $2 AND stock_quantity >= $1
                        """
        await conn.execute(query, quantity_purchased, product_id)


async def update_item_quantity_in_cart(product_id, new_quantity):
    """Обновление количества товара в order_items и корзине."""
    order_id = st.session_state.order_id
    st.session_state.cart[product_id]['quantity'] = new_quantity
    await update_item_quantity(order_id, product_id, new_quantity)
    await update_order_summary(order_id)

async def payed_order(order_id):
    async with get_db_connection() as conn:
        query = """
                    UPDATE orders
                    SET order_state = 'оплачен'
                    WHERE id = $1
                    """
        await conn.execute(query, order_id)


def get_cart_total():
    """Вычисление итоговой суммы корзины."""
    return sum(item['price'] * item['quantity'] for item in st.session_state.cart.values())

def clear_cart():
    """Очистка корзины."""
    st.session_state.cart = {}


def cart_page(customer_id):
    """Страница корзины."""
    st.title("Корзина")

    # Инициализация текущего заказа
    if 'order_id' not in st.session_state:
        st.session_state.order_id = asyncio.run(create_new_order(customer_id=customer_id))

    order_id = st.session_state.order_id

    # Грузим корзину из базы в session_state
    if 'cart' not in st.session_state:
        asyncio.run(load_cart_from_database(order_id))

    cart_items = st.session_state.cart

    if cart_items:
        st.write("##### Содержимое корзины:")

        for product_id, item in list(cart_items.items()):

            product_info = asyncio.run(fetch_product_by_id(product_id))


            st.subheader(f"🛍️ {item['name']}")
            st.write(f"**Цена за единицу:** ${item['price']}")
            col1, col2, col3 = st.columns([2, 2, 1])


            if product_info[0]['stock_quantity'] == 0:
                st.warning("Товара временно нет в наличии")

                with st.spinner("Подождите, обновляем корзину..."):
                    asyncio.run(remove_item_from_order(order_id, product_id))
                    st.session_state.cart = {}
                    time.sleep(3)
                st.rerun()

            if st.session_state.cart[product_id]['quantity'] > product_info[0]['stock_quantity']:
                st.error("Такого количества товара нет в наличии, количество автоматически сейчс изменится")
                st.session_state.cart[product_id]['quantity'] = product_info[0]['stock_quantity']
                asyncio.run(update_item_quantity_in_cart(product_id, product_info[0]['stock_quantity']))
                time.sleep(3)
                st.rerun()

            with col1:


                new_quantity = st.number_input(
                    f"Изменить количество для {item['name']}:",
                    value=item['quantity'], min_value=1, max_value=product_info[0]['stock_quantity'], step=1, key=f"edit_quantity_{product_id}"
                )
                if new_quantity != item['quantity']:
                    asyncio.run(update_item_quantity_in_cart(product_id, new_quantity))
                    st.success(f"Количество для '{item['name']}' обновлено до {new_quantity} шт.")
                    time.sleep(2)
                    st.rerun()

            with col2:
                if st.button(f"❌ Удалить {item['name']}", key=f"remove_{product_id}"):
                    asyncio.run(remove_item_from_order(order_id, product_id))
                    del st.session_state.cart[product_id]
                    st.warning(f"Товар '{item['name']}' удален из корзины.")
                    st.rerun()

        update_order_summary(order_id)
        total_summ = get_cart_total()
        st.write(f"### Общая сумма заказа: ${total_summ}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Очистить корзину"):
                for product_id in list(cart_items.keys()):
                    asyncio.run(remove_item_from_order(order_id, product_id))
                clear_cart()
                st.success("Корзина очищена.")
                time.sleep(2)
                st.rerun()

        with col2:
            if st.button("Оформить заказ"):
                user_balance = asyncio.run(get_user_balance(customer_id))
                if user_balance >= total_summ:
                    for product_id, item in list(cart_items.items()):
                        asyncio.run(update_product_quantity(product_id, item['quantity']))

                    with st.spinner("Выполняется покупка, зачильтесь и полюбуйтесь на спиннер :)"):
                        asyncio.run(payed_order(order_id))
                        asyncio.run(update_user_balance(customer_id, user_balance - total_summ))

                        clear_cart()
                        del st.session_state.order_id
                        st.success("Ваш заказ успешно оформлен!")
                        time.sleep(3)
                else:
                    st.error(f"""💵 На счете недостаточно средств (баланс: {user_balance}, не хватает {total_summ - user_balance}) для оформления заказа, пожалуйста, пополните баланс или удалите лишние товары""")
                    time.sleep(5)
                st.rerun()
    else:
        st.write("Ваша корзина пуста.")