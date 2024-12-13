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


async def fetch_products(search_query=None, brand_filter=None, category_filter=None):
    """Получение информации о продуктах из базы данных с учетом фильтров."""
    async with get_db_connection() as conn:
        # Базовый SQL-запрос
        query = """
            SELECT p.id, p.name, p.description, p.price, p.stock_quantity, b.brand_name AS brand, c.name AS category
            FROM products p
            LEFT JOIN brands b ON p.brand_id = b.id
            LEFT JOIN categories c ON p.category_id = c.id
        """
        # Условия поиска и фильтрации
        conditions = []
        params = []


        if search_query and search_query != "":
            conditions.append(f"p.name LIKE ${len(params) + 1}")
            params.append(f"%{search_query}%")

        if brand_filter and brand_filter.strip():
            # Обратите внимание на порядок $N: если нет search_query, это $1
            conditions.append(f"b.brand_name = ${len(params) + 1}")
            params.append(brand_filter)

            # Фильтр по категории
        if category_filter and category_filter.strip():
            conditions.append(f"c.name = ${len(params) + 1}")
            params.append(category_filter)

        # Добавляем условия, если они существуют
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        result = await conn.fetch(query, *params)
        return result

async def fetch_brands():
    """Получение списка брендов из базы данных."""
    async with get_db_connection() as conn:
        query = "SELECT DISTINCT brand_name FROM brands"
        result = await conn.fetch(query)
        return [record['brand_name'] for record in result]


async def fetch_categories():
    """Получение списка категорий из базы данных."""
    async with get_db_connection() as conn:
        query = "SELECT DISTINCT name FROM categories"
        result = await conn.fetch(query)
        return [record['name'] for record in result]

async def update_product_stock_quantity(product_id, stock_diff):
    async with get_db_connection() as conn:
        query = '''UPDATE products
                          SET stock_quantity = stock_quantity + $1
                          WHERE id = $2'''
        conn.execute(query, stock_diff, product_id)
        conn.commit()


async def fetch_reviews(product_id):
    """Получение отзывов о конкретном товаре из базы данных."""
    async with get_db_connection() as conn:
        query = '''SELECT c.name, r.comment, r.rate
                   FROM reviews r
                   JOIN customers c 
                   ON r.customer_id = c.id
                   WHERE r.product_id = $1'''
        result = await conn.fetch(query, product_id)
        return result


# Инициализация корзины в session_state
if 'cart' not in st.session_state:
    st.session_state.cart = {}


async def add_to_cart(product_id, name, price, quantity):
    """Добавление товара в корзину и в order_items."""
    order_id = st.session_state.order_id
    if product_id in st.session_state.cart:
        st.info("Товар уже у вас в корзине")
        return
    else:
        # Добавляем новый товар в корзину и базу
        st.session_state.cart[product_id] = {
            'name': name,
            'price': price,
            'quantity': quantity
        }

        await add_item_to_order(order_id, product_id, quantity, price)

    await update_order_summary(order_id)  # Обновляем стоимость заказа в таблице orders
    st.success(f"Товар '{name}' ({quantity} шт.) успешно добавлен в корзину!")


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


async def add_item_to_order(order_id, product_id, quantity, unitprice):
    """Добавление товара в таблицу order_items."""
    async with get_db_connection() as conn:
        query = """
            INSERT INTO order_items (order_id, product_id, quantity, unitprice)
            VALUES ($1, $2, $3, $4)
        """
        await conn.execute(query, order_id, product_id, quantity, unitprice)



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



def purchase_page(customer_id):
    """Страница просмотра товаров и добавления в корзину."""
    st.title("Покупка товаров")
    st.sidebar.info("🔵 Используйте эту страницу для оформления покупок.")

    if 'order_id' not in st.session_state:
        st.session_state.order_id = asyncio.run(create_new_order(customer_id))


    all_brands = ["Все"] + asyncio.run(fetch_brands())
    all_categories = ["Все"] + asyncio.run(fetch_categories())

    st.sidebar.header("Фильтры")
    search_query = st.sidebar.text_input("Поиск по названию товара")

    # Выпадающие списки для фильтрации
    selected_brand = st.sidebar.selectbox("Фильтр по бренду", all_brands)
    selected_category = st.sidebar.selectbox("Фильтр по категории", all_categories)

    # Преобразуем выбор пользователя
    brand_filter = None if selected_brand == "Все" else selected_brand
    category_filter = None if selected_category == "Все" else selected_category

    # Получение продуктов с учетом фильтров
    products = asyncio.run(fetch_products(search_query, brand_filter, category_filter))

    if products is not None:
        if int(len(products)) == 0:
            st.warning("К сожалению, по вашему запросу ничего не найдено...")
        else:
            st.write("##### Список доступных товаров:")

        rerun_button = st.button("Перезагрузить страницу")
        if rerun_button:
            st.rerun()

        for product in products:
            if product['stock_quantity'] > 0:
                with st.expander(f"{product['name']} - ${product['price']}"):
                    st.write(f"**Описание:** {product['description']}")
                    st.write(f"**Цена:** ${product['price']}")
                    st.write(f"**Остаток на складе:** {product['stock_quantity']}")

                    # Просмотр отзывов
                    st.subheader("Отзывы о товаре")
                    reviews = asyncio.run(fetch_reviews(product['id']))
                    if reviews:
                        for review in reviews:
                            st.write(f"📜 {review['name']}: {review['comment']} (Оценка: {review['rate']}/5)")
                    else:
                        st.write("Пока отзывов нет.")

                    # Добавление товара в корзину
                    with st.form(key=f"form_{product['id']}"):
                        quantity = st.number_input(
                            "Укажите количество:",
                            min_value=1,
                            max_value=product['stock_quantity'],
                            value=1,
                            key=f"quantity_{product['id']}"
                        )
                        add_button = st.form_submit_button("Добавить в корзину")
                        if add_button:
                            if product['stock_quantity'] >= quantity:
                                asyncio.run(add_to_cart(product['id'], product['name'], product['price'], quantity))
                            else:
                                st.error("Недостаточно товара на складе для добавления в корзину.")
            else:
                st.warning(f"Товара {product['name']} пока нет в наличии")

    elif products is None:
        st.warning("Список товаров временно недоступен.")
    else:
        st.warning("К сожалению, по вашему запросу ничего не найдено...")