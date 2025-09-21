import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 400
    page.window_height = 600
    
    db_conn = init_db()
    def search_pattern(e):
        display_contacts(page, contacts_list_view, db_conn, search_input.value)

    search_input = ft.TextField(label="Search", on_change=search_pattern, width=350)
    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)

    inputs = (name_input, phone_input, email_input)

    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)
    
    add_button = ft.ElevatedButton(
    text="Add Contact",
    on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )

    page.add(
            ft.Column(
            [
                ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD),
                search_input,
                name_input,
                phone_input,
                email_input,
                add_button,
                ft.Divider(),
                ft.Text("Contacts:", size=20, weight=ft.FontWeight.BOLD),
                contacts_list_view,
            ]
        )
    )
    
    display_contacts(page, contacts_list_view, db_conn, search_input.value)

if __name__ == "__main__":
    ft.app(target=main)
