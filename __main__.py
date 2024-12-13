import asyncio
import streamlit as st
from _src.pages import buy_products
from _src.pages import log_user
from _src.pages import edit_products
from _src.pages import edit_managers
from _src.pages import cart_page
from _src.pages import customer_page
from _src.pages import main_window


async def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'cart' not in st.session_state:
        st.session_state.cart = {}
    if 'role' not in st.session_state:
        st.session_state.role = None

    if not st.session_state.logged_in:
        # Показать меню для входа/регистрации
        page = st.sidebar.selectbox("Выберите действие", ["Вход", "Регистрация"])

        if page == "Вход":
            # Вызов асинхронной формы для входа
            log_user.login_form()
        elif page == "Регистрация":
            # Вызов асинхронной формы для регистрации
            log_user.registration_form()
    else:
        # Авторизованный пользователь
        if st.session_state.role == 'customer':
            page = st.sidebar.radio(
                "Меню",
                ["Главная", "Купить товары", "Корзина", "Профиль"]
            )

            if page == "Главная":
                main_window.main_window()
            elif page == "Купить товары":
                buy_products.purchase_page(st.session_state['user_id'])  # Вызов страницы покупки товаров
            elif page == "Корзина":
                cart_page.cart_page(st.session_state['user_id'])  # Отображение корзины
            elif page == "Профиль":
                customer_page.profile_page()  # Профиль и отзывы

            # Добавление кнопки выхода из аккаунта
            if st.sidebar.button("Выйти"):
                log_user.log_out()

        elif st.session_state.role == 'manager':
            page = st.sidebar.radio(
                "Меню",
                ["Главная", "Купить товары", "Корзина", "Профиль", "Редактировать товары"]
            )

            if page == "Главная":
                main_window.main_window()
            elif page == "Купить товары":
                buy_products.purchase_page(st.session_state['user_id'])  # Вызов страницы покупки товаров
            elif page == "Корзина":
                cart_page.cart_page(st.session_state['user_id'])  # Отображение корзины
            elif page == "Профиль":
                customer_page.profile_page()  # Профиль и отзывы
            elif page == "Редактировать товары":
                edit_products.products_management_page()

            # Добавление кнопки выхода из аккаунта
            if st.sidebar.button("Выйти"):
                log_user.log_out()

        elif st.session_state.role == 'admin':
            page = st.sidebar.radio(
                "Меню",
                ["Главная", "Купить товары", "Корзина", "Профиль", "Редактировать товары", "Управление менеджерами"]
            )

            if page == "Главная":
                main_window.main_window()

            elif page == "Купить товары":
                buy_products.purchase_page(st.session_state['user_id'])  # Вызов страницы покупки товаров
            elif page == "Корзина":
                cart_page.cart_page(st.session_state['user_id'])  # Отображение корзины
            elif page == "Профиль":
                customer_page.profile_page()  # Профиль и отзывы
            elif page == "Редактировать товары":
                edit_products.products_management_page()
            elif page == "Управление менеджерами":
                edit_managers.manager_page()

            # Добавление кнопки выхода из аккаунта
            if st.sidebar.button("Выйти"):
                log_user.log_out()


if __name__ == "__main__":
    asyncio.run(main())