import flet as ft
from db_connection import connect_db
import mysql.connector

def main(page: ft.Page):
    # window settings
    page.window.frameless = True
    page.window.title = "User Login"
    page.window.alignment = ft.alignment.center
    page.window.height = 350
    page.window.width = 400
    page.bgcolor = ft.Colors.AMBER_ACCENT
    page.theme_mode = ft.ThemeMode.LIGHT

    login_title = ft.Text(
        "User Login",
        size=20,
        weight=ft.FontWeight.BOLD,
        font_family="Arial",
        text_align=ft.TextAlign.CENTER,
    )

    username_field = ft.TextField(
        label="User name",
        hint_text="Enter your user name",
        helper_text="This is your unique identifier",
        width=300,
        autofocus=True,
        prefix_icon=ft.Icons.PERSON,
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )

    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        helper_text="This is your secret key",
        width=300,
        password=True,                # Obscure text (password mode)
        can_reveal_password=True,     # Allow revealing password
        prefix_icon=ft.Icons.PASSWORD, # Password icon
        bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
    )

    async def login_click(e):
      
        # dialogs
        success_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Login Successful"),
            content=ft.Text(f"Welcome! {username_field.value}"),
            alignment=ft.alignment.center,
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(success_dialog))
            ], icon=ft.Icon(name=ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN)
        )

        failure_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Login Failed"),
            content=ft.Text("Invalid username or password"),
            alignment= ft.alignment.center,
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(failure_dialog))
            ],icon=ft.Icon(name=ft.Icons.ERROR, color=ft.Colors.RED),
        )

        invalid_input_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Input Error"),
            content=ft.Text("Please enter username and password"),
            alignment=ft.alignment.center,
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(invalid_input_dialog))
            ], icon=ft.Icon(name=ft.Icons.INFO, color=ft.Colors.BLUE)
        )

        database_error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Database Error"),
            content=ft.Text("An error occurred while connecting to the database"),
            alignment=ft.alignment.center,
            actions=[
                ft.TextButton("OK", on_click=lambda e: page.close(database_error_dialog))
            ],
        )
        # validation
        if not username_field.value or not password_field.value:
            page.open(invalid_input_dialog)
            page.update()
            return


        try:
            # establish DB connection
            connection = connect_db()
            if not connection:
                page.open(database_error_dialog)
                page.update()
                return

            cursor = connection.cursor(dictionary=True)

            # execute parameterized query
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username_field.value, password_field.value)
            )

            result = cursor.fetchone()

            # close DB connection
            cursor.close()
            connection.close()

            # check result
            if result:
                page.open(success_dialog)
            else:
                page.open(failure_dialog)

        except mysql.connector.Error as e:
            page.open = database_error_dialog
        
        page.update()
    
    login_button =ft.ElevatedButton(
            text="Login",
            width=100,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLUE_500,
            icon=ft.Icons.LOGIN,
            on_click=login_click
        )

    # Add everything to page
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.add(
       ft.SafeArea(
            ft.Container(
                ft.Column([login_title, username_field, password_field,
                ft.Container(content=login_button, alignment=ft.alignment.top_right, margin=ft.margin.Margin(0, 20, 40, 0))],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,), 
                alignment=ft.alignment.center,
            ), expand=True
       )
    )
# run app
ft.app(target=main)
