import flet as ft
from appstate import FormulaBook, AppContext
import aon_database as aon
import re
import json
import uuid

FILE_PATH = "formula_books.json"

def open_save():
    with open(FILE_PATH, 'a+') as save_file:
        save_file.seek(0)
        content = save_file.read()
        
        if not content:
            book = FormulaBook()
            data = {book.id:book}
            content = json.dumps(data,cls=FormulaBook.Encoder, indent=4)
            save_file.write(content)

        data = json.loads(content)
        return data

def write_save(formula_book): 
    data = open_save()
    data[formula_book.id] = formula_book

    with open(FILE_PATH, "w") as save:
        json.dump(data, save,cls=FormulaBook.Encoder, indent=4)






@ft.component
def bookSelection(formula_book):

    data = open_save()

    show_dialog, set_show_dialog = ft.use_state(False)
    reset_val,reset = ft.use_state(True)


    def handle_dialog_select(e):
        formula_book.update(data[e.control.key],e.control.key)
        #ft.context.page.pop_dialog()
        #lambda: set_show_dialog(False)
        #ft.context.page.dialog
        print(e.control.key)
        print(formula_book.name)

    ft.component
    def formulaBookOption(id:str,selected:bool):
        return ft.Row(
            controls=[
                    ft.Button(
                    key=id,
                    expand=True,
                    style=ft.ButtonStyle(
                        shape = ft.RoundedRectangleBorder(radius=2),
                        padding = ft.Padding(top = 10, left = 10, right = 10, bottom = 12),
                        alignment=ft.Alignment.CENTER_LEFT,
                        bgcolor = ft.Colors.ON_SECONDARY if selected else ft.Colors.SURFACE_CONTAINER,
                    ),
                    on_click = handle_dialog_select,
                    content=ft.Column(
                        spacing = 0,
                        controls=[
                            ft.Text(f"{data.get(id).get('name')} ", size = 16),
                            ft.Text(f"level: {data.get(id).get('level')} <space> price?", size = 14)
                        ],
                    )
                ),
                
            ],
            expand= True,
        )

    def handle_dialog_close(e):
        set_show_dialog(False)

    def handle_dialog_new(e):
        ...

    def handle_dialog_delete(e):
        ...


    ft.use_dialog(
        ft.AlertDialog(
            content_padding=0,
            expand=True,
            actions_padding=0,
            title_padding=0,
            shape=ft.RoundedRectangleBorder(radius=2),
            content=ft.Container(
                width=100000,   
                height=100000, 
                #padding=25,
                expand=True,
                padding=2,
                content=ft.Column( 
                  
                    scroll=ft.ScrollMode.AUTO, 
                    #tight=True,
                    controls=[formulaBookOption(id,id==formula_book.id) for id in data],
                    spacing=2,
                ),
            ),
            actions=[
                ft.Row( 
                    controls=[
                        ft.TextButton(
                            expand=True,
                            content="New Book",
                            icon=ft.Icons.STAR_BORDER,
                            icon_color=ft.Colors.BLUE_300,
                            on_click = handle_dialog_new,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=2),
                                padding=10,
                            ),
                        ),
                        ft.TextButton(
                            expand=True,
                            content="Delete",
                            icon=ft.Icons.STAR_BORDER,
                            icon_color=ft.Colors.BLUE_300,
                            on_click = handle_dialog_delete,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=2),
                                padding=10,
                            ),
                        ),
                        ft.TextButton(
                            expand=True,
                            content="Close",
                            icon=ft.Icons.STAR_BORDER,
                            icon_color=ft.Colors.BLUE_300,
                            on_click = handle_dialog_close,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=2),
                                padding=10,
                            ),
                        ),
                    ]
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )
        if show_dialog else None
    )


    def handle_blur(e):
        reset(not reset_val)


    def handle_rename(e):
        formula_book.set_name(e.control.value)
        write_save(formula_book)
        print(f"Renamed to {formula_book.name}")

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    border_radius=4,
                    padding= 5,
                    border=ft.Border.all(color=ft.Colors.PRIMARY,width=2),
                    content=ft.Text("Formula Book"),
                    on_click=lambda e: set_show_dialog(True)
                ),
                ft.TextField(
                    label = 'Name',
                    value = formula_book.name,
                    on_submit = handle_rename, 
                    on_blur = handle_blur,
                ),
                ft.Container(expand=True),
                ft.IconButton(
                    icon = ft.Icons.REMOVE,
                )
            ],
            #alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
        bgcolor=ft.Colors.ON_SECONDARY,  
        padding=10,                  
        margin=0,                  
        #border_radius=5,             
    )




@ft.component
def AlchemicalFormulaBookPage():
    formula_book = ft.use_context(AppContext).current_formula_book

  


    #app = ft.use_context(AppContext).app

    return ft.Column( controls =[
        bookSelection(formula_book),
    ], expand=True)