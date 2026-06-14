import flet as ft
from appstate import FormulaBook, AppContext
import aon_database as aon
import re
import json

FILE_PATH = "formula_books.json"

#Tabs for bought/free formulas?
def open_save():
    with open(FILE_PATH, 'a+') as save_file:
        save_file.seek(0)
        content = save_file.read()
        
        if not content:
            #print(f"File was empty or newly created. Writing content...")
            data = [FormulaBook()]
            save_file.write(json.dumps(data,cls=FormulaBook.Encoder, indent=4))
        else:
            data = json.loads(content)
            #print(f"File already has data. Leaving it alone.")

        return data

def write_save(formula_book): 
    data = open_save()
    if formula_book.id >= 0:
        data[formula_book.id] = formula_book
    else:
        data.append(formula_book)

    with open(FILE_PATH, "w") as save:
        json.dump(data, save,cls=FormulaBook.Encoder, indent=4)

def showFormulaBookSelection(formula_book):
       
    data = open_save()

    def handle_select(e):
        formula_book.update(data[e.control.key],e.control.key)
        ft.context.page.pop_dialog()
        print(e.control.key)
        print(formula_book.name)


    ft.component
    def formulaBookOption(option):
        return ft.Button(
            key=option,
            style=ft.ButtonStyle(
            shape = ft.RoundedRectangleBorder(radius=2),
            padding = ft.Padding(top = 10, left = 10, right = 10, bottom = 12),
            ),
            on_click = handle_select,
            content=ft.Column(
                spacing = 0,
                controls=[
                    ft.Text(f"{data[option].get('name')} ", size = 16),
                    ft.Text(f"level: {data[option].get('level')} <space> price?)", size = 14)
                ]
            )
        )

    ft.context.page.show_dialog(
        ft.AlertDialog(
            content_padding=0,
            expand=True,
            actions_padding=0,
            title_padding=0,
            shape=ft.RoundedRectangleBorder(radius=2),
            content=ft.Container(
                padding=2,
                alignment=ft.Alignment.CENTER, 
                content=ft.Column( 
                    scroll=ft.ScrollMode.AUTO, 
                    expand=False,
                    tight=True,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Column(
                                    [formulaBookOption(i) for i in range(0,len(data))],
                                    spacing=5,
                                    expand=True 
                                )
                            ],
                            expand=True
                        )
                    ],
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
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=2),
                                padding=10,
                            ),
                        ),
                        ft.TextButton(
                            expand=True,
                            content="Cancel",
                            icon=ft.Icons.STAR_BORDER,
                            icon_color=ft.Colors.BLUE_300,
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
    )

@ft.component
def bookSelection(formula_book):



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
                    on_click=lambda e: showFormulaBookSelection(formula_book)
                ),
                ft.TextField(
                    label = 'Name',
                    value = formula_book.name,
                    on_submit = handle_rename, 
                    #on_blur = (lambda e: e.control.value = data[select_book]['name']),
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