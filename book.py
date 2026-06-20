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

def levelSelectionDialog(formula_book,setter):

    def handle_level_select(e):
        formula_book.set_level(e.control.key)



    return ft.AlertDialog(
        on_dismiss=lambda: setter(False),
        content_padding=0,
        actions_padding=0,
        title_padding=0,
        shape=ft.RoundedRectangleBorder(radius=2),
        content=ft.Container(

            padding=10,
            content= ft.Column(
                tight =True,
                controls = [
                    ft.Row(
                        controls=[
                            ft.Button(
                                ft.Text(f"Level {5*r+c}"),
                                key = 5*r+c,
                                expand=True,
                                on_click=handle_level_select,
                                style=ft.ButtonStyle(
                                    shape = ft.RoundedRectangleBorder(radius=2),
                                    padding = ft.Padding(top = 10, left = 10, right = 10, bottom = 12),
                                    alignment=ft.Alignment.CENTER,
                                    bgcolor = ft.Colors.ON_SECONDARY if 5*r+c ==formula_book.level else ft.Colors.SURFACE_CONTAINER,
                                ),
                            ) for c in range(1,6)
                        ]
                    ) for r in range(0,4)
                ]
            )
        ),
        actions=[
            ft.Row( 
                controls=[
                    ft.TextButton(
                        expand=True,
                        content="Ok",
                        icon=ft.Icons.STAR_BORDER,
                        icon_color=ft.Colors.BLUE_300,
                        #on_click = handle_new,
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
                        #on_click = handle_close,
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

def formulaBookDialog(formula_book,handle_new,handle_delete,setter,data) -> ft.AlertDialog:
    def handle_dialog_select(e):
        formula_book.update(data[e.control.key],e.control.key)

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
    
    return ft.AlertDialog(
        on_dismiss=lambda: setter(False),
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
                        on_click = handle_new,
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
                        on_click = handle_delete,
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
                        on_click = lambda e: setter(False),
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


@ ft.component
def formulaDisplay(formula_book):
    @ft.component
    def itemCard(item: Dict[str, Any],formula_book) -> ft.Control:
        db = ft.use_context(AppContext).db
        trait_descriptions = ft.use_context(AppContext).trait_descriptions
        expanded, expand = ft.use_state(False)

        def on_card_press(e):
            expand(not expanded)

        trait_list  = ft. Row(
            spacing = 5,
            controls = [
                ft.Card(
                    bgcolor = ft.Colors.ON_SECONDARY_FIXED,
                    variant =ft.CardVariant.FILLED,
                    shape = ft.RoundedRectangleBorder(radius=2),
                    margin=0,
                    elevation = 3,
                    content=ft.Container(
                        border=ft.Border.all(0, ft.Colors.ON_SECONDARY_FIXED),
                        tooltip = trait_descriptions.get(trait), 
                        content=ft.Text(trait,size=13),       
                        padding = ft.Padding(left=3,right=3,bottom=1,top=1),             
                    ),
                )
                for trait in item.get('trait')
            ],
        )
        price = aon.formula_price(item.get("level", ""))
    
        def format_actions(text):
            match text.group(1).strip():
                case "Single Action":
                    return '`a` '
                case "Two Actions":
                    return '`d` '
                case "Three Actions":
                    return '`d` '
                case "Free Action":
                    return '`.` '
                case "Reaction":
                    return '`r` '
                
        def find_descriptions(text):
            matches = [re.sub(r'\[(.*?)]\((\/.*?)\)', lambda t: f"[{t.group(1)}](https://2e.aonprd.com/{t.group(2)})", m.group(1).strip()) for m in re.finditer(r'<title.*?<\/column>.*?.(?:\s*?---\s*)?(.*?)(?=<c|<t|$)', text,flags=re.DOTALL)]
            matches = [re.sub(r'<actions.*?"(.*?)".+?>(?: Interact)?(?:[; ]+)?',  format_actions, m) for m in matches]
            matches = [re.sub(r'<br \/>', r'\n', m) for m in matches]
            return matches
        description_text = find_descriptions(item.get('markdown'))

        @ft.component
        def childDescription(child_num,child):
            return ft.Row(
                expand =True,
                controls=[
                    ft.Card(
                        bgcolor = ft.Colors.ON_SECONDARY_FIXED,
                        variant =ft.CardVariant.FILLED,
                        expand=True,
                        elevation = 3,
                        content=ft.Container(
                            content=ft.Column(
                                controls=[
                                ft.Text(f'{child.get('name')} Level {child.get('level')}', weight=ft.FontWeight.BOLD),
                                *([ft.Text(description_text[child_num+1])] if description_text[child_num+1] else [])
                                ],
                                expand=True
                            ),
                            padding =12,
                        )
                    )
                ])

        async def handle_link_click(e):
            if e.data:
                await ft.context.page.launch_url(e.data)

        children = item.get('item_child_id')
        if children:
            children = [db.filter_items(id = child, hide_excluded=False, is_outer_item=False,remaster_only=False)[0] for child in children]
        description_card = ft.Row(
            controls=ft.Column(
                expand=True,
                spacing = 0,
                controls = [
                    ft.Container(
                        content=ft.Markdown(
                            description_text[0],
                            selectable=True,
                            on_tap_link =handle_link_click,
                            md_style_sheet=ft.MarkdownStyleSheet(
                                code_text_style=ft.TextStyle(
                                    font_family="PF2e Icons",
                                    size = 25,
                                )
                            )
                        ),
                    padding =12,
                    )

                ] + ([
                    childDescription(child_num,child)
                    for child_num,child in enumerate(children)
                ] if children else []),
            )
        )
            
        title_panel = ft.Container(
            on_click=on_card_press,
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row(controls=[
                                ft.Text(f"{item.get('name')}", weight=ft.FontWeight.BOLD, size=16),
                            ]),
                            trait_list,
                            ft.Text(
                                f"Level {item.get('level')} | {item.get('item_subcategory', 'Item')}"
                            )
                        ],
                        expand=True,
                        spacing =5
                    ),
                    ft.Text(f"{price[1]}", italic=True)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ), 
            padding=12
        )

        return ft.Column(
            controls=[
                ft.Card(
                    bgcolor = ft.Colors.ON_SECONDARY,
                    content=ft.Column(
                    spacing=2,
                        controls=[
                            title_panel,
                            *([description_card] if expanded else [])
                        ]
                    )
                )
            ]
        )
    db = ft.use_context(AppContext).db

    item_list = [itemCard(db.filter_items(id = id, hide_excluded=False, is_outer_item=False,remaster_only=False)[0],formula_book) for id in formula_book.formulas]

    return ft.ListView(
        controls=item_list,
        expand=True,
        spacing=5,
        padding=10,
        item_extent=120,
    )



@ft.component
def bookTopBar(formula_book):

    db = ft.use_context(AppContext).db
    data = open_save()
    show_formula_dialog, set_show_formula_dialog = ft.use_state(False)
    show_level_dialog, set_show_level_dialog = ft.use_state(False)
    free_only, set_free_only = ft.use_state(False)
    reset_val,reset = ft.use_state(True)

    def handle_formula_dialog_close(e):
        set_show_formula_dialog(False)

    def handle_formula_dialog_new(e):
        ...

    def handle_formula_dialog_delete(e):
        ...

    ft.use_dialog(
        formulaBookDialog(
            formula_book=formula_book,
            handle_new=handle_formula_dialog_new,
            handle_delete=handle_formula_dialog_delete,
            setter = set_show_formula_dialog,
            data=data,
        ) if show_formula_dialog else None
    )

    ft.use_dialog(
        levelSelectionDialog(
            formula_book, set_show_level_dialog
        )
        if show_level_dialog else None
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
                    on_click=lambda e: set_show_formula_dialog(True)
                ),
                ft.TextField(
                    label = 'Name',
                    value = formula_book.name,
                    on_submit = handle_rename, 
                    on_blur = handle_blur,
                ),
                ft.Container(expand=True),
                ft.Button(
                    style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=5),
                            padding=10,
                        ),
                    content = ft.Row(
                        [ft.Text(f"Free formulas"),ft.Icon(ft.Icons.CHECK_BOX_ROUNDED if free_only else ft.Icons.CHECK_BOX_OUTLINE_BLANK_ROUNDED, color=ft.Colors.PRIMARY)]
                    ),
                    on_click=lambda e: print("checkbox!") # set_free_only(not free_only)
                ),
                ft.Button(
                    style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=5),
                            padding=10,
                        ),
                    content = ft.Text(f"{formula_book.level}"),
                    on_click=lambda e: set_show_level_dialog(True)
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

 

    return ft.Column( controls =[
        bookTopBar(formula_book),
        #freeFormulas(formula_book),
        formulaDisplay(formula_book),
    ], expand=True)