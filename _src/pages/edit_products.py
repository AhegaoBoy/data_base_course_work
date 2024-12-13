import asyncio
import asyncpg
import streamlit as st
from contextlib import asynccontextmanager
import pandas as pd
import time

# Асинхронный контекст для подключения к базе данных
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

async def check_customer(id):
    async with get_connection() as conn:
        query = '''SELECT * 
                   FROM customers 
                   JOIN roles ON customers.ROLE = roles.id
                   WHERE customers.id = $1'''
        user = await conn.fetchrow(query, id)
        return user


# Асинхронная функция для получения продуктов в формате DataFrame
async def get_products_dataframe():
    async with get_connection() as conn:
        query = '''
            SELECT p.id AS product_id,
                   p.name AS product_name,
                   description,
                   price,
                   stock_quantity,
                   b.brand_name AS brand_name,
                   c.name AS category_name
            FROM products p
            JOIN brands b ON p.brand_id = b.id
            JOIN categories c ON p.category_id = c.id
            ORDER BY product_name
        '''
        rows = await conn.fetch(query)
        df = pd.DataFrame([dict(row) for row in rows])
        return df


# Асинхронная операция добавления, удаления или изменения через DataFrame
async def sync_dataframe_changes(df: pd.DataFrame, original_ids: list):
    async with get_connection() as conn:
        for index, row in df.iterrows():
            product_id = row['product_id']

            # Если запись существует в базе данных, обновляем ее, иначе добавляем
            if product_id in original_ids:
                query = '''
                    UPDATE products
                    SET name = $1, description = $2, price = $3, stock_quantity = $4
                    WHERE id = $5
                '''
                await conn.execute(query, row['product_name'], row['description'], row['price'], row['stock_quantity'],
                                   product_id)
            else:
                category_id = await find_category_id(conn, row['category_name'])
                brand_id = await find_brand_id(conn, row['brand_name'])
                query = '''
                    INSERT INTO products (name, description, price, stock_quantity, category_id, brand_id)
                    VALUES ($1, $2, $3, $4, $5, $6)
                '''
                await conn.execute(query, row['product_name'], row['description'], row['price'], row['stock_quantity'],
                                   category_id, brand_id)

        # Удаление записей, которые отсутствуют в текущей версии DataFrame
        ids_to_delete = list(set(original_ids) - set(df['product_id']))
        if ids_to_delete:
            await conn.execute("DELETE FROM order_items WHERE product_id = ANY($1)", ids_to_delete)
            await conn.execute("DELETE FROM products WHERE id = ANY($1)", ids_to_delete)


async def find_category_id(conn, category_name):
    query = "SELECT id FROM categories WHERE name = $1"
    category_id = await conn.fetchval(query, category_name)

    if not category_id:
        query_insert = "INSERT INTO categories (name) VALUES ($1) RETURNING id"
        category_id = await conn.fetchval(query_insert, category_name)

    return category_id


async def find_brand_id(conn, brand_name):
    query = "SELECT id FROM brands WHERE brand_name = $1"
    brand_id = await conn.fetchval(query, brand_name)

    if not brand_id:
        query_insert = "INSERT INTO brands (brand_name) VALUES ($1) RETURNING id"
        brand_id = await conn.fetchval(query_insert, brand_name)

    return brand_id


def products_management_page():
    st.title('Управление товарами в базе данных')

    # Функция для работы с DataFrame
    st.subheader("Интерактивный список товаров")

    user_role = asyncio.run(check_customer(st.session_state.user_id))['role']

    if user_role == 'customer':
        st.error("Так, хулиган, что тут забыл?) БАН")
        st.session_state.role = 'customer'
        time.sleep(3)
        st.rerun()

    # Загружаем исходные данные
    with st.spinner("Загружаем данные..."):
        products_df = asyncio.run(get_products_dataframe())

    if not products_df.empty:
        original_ids = products_df['product_id'].tolist()

        edited_df = st.data_editor(
            products_df,
            use_container_width=True,
            num_rows="dynamic",
            key="products_editor"
        )

        if st.button("Сохранить изменения"):
            if sum(edited_df[edited_df.columns[1:]].isna().any(axis=1)) > 0:
                st.error("Заполните все поля в датасете")
                time.sleep(3)
                st.rerun()

            asyncio.run(sync_dataframe_changes(edited_df, original_ids))
            st.success("Изменения успешно сохранены!")
    else:
        st.write("📦 В базе данных пока нет товаров. Добавьте их через таблицу выше.")