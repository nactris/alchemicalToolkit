import flet as ft


def main(page: ft.Page):
    tags = []
    chat = ft.Column()
    new_message = ft.TextField()

    def handle_chip_click(arg):
        print(arg)

    def add_tag(name):
        return ft.Chip(
            label=ft.Text(name),
            #leading=ft.Icon(ft.Icons.FAVORITE_BORDER_OUTLINED),
            bgcolor=ft.Colors.GREEN_800,
            disabled_color=ft.Colors.GREEN_800,
            autofocus=True,
            on_click= lambda: handle_chip_click("arg"),
        )


    def send_click(e):
        chat.controls.append(add_tag(new_message.value))
        new_message.value = ""

    page.add(
        chat,
        ft.Row(controls=[new_message, ft.Button("Send", on_click=send_click)]),
    )
    page.scroll = "always"
    page.update()


ft.run(main)