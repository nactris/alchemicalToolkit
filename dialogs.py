import flet as ft
from appstate import AppContext, write_save

def levelSelection(setter) -> ft.AlertDialog:
    
    @ft.component
    def LevelGrid():
        formula_book = ft.use_context(AppContext).current_formula_book
        
        def handle_level_select(e):
            formula_book.set_level(e.control.key)
            setter(False)

        return ft.Column(
            tight=True,
            controls=[
                ft.Row(
                    controls=[
                        ft.Button(
                            ft.Text(f"Level {5*r+c}"),
                            key=5*r+c,
                            expand=True,
                            on_click=handle_level_select,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=2),
                                padding=ft.Padding(top=10, left=10, right=10, bottom=12),
                                alignment=ft.Alignment.CENTER,
                                bgcolor=ft.Colors.ON_SECONDARY if 5*r+c == formula_book.level else ft.Colors.SURFACE_CONTAINER,
                            ),
                        ) for c in range(1, 6)
                    ]
                ) for r in range(0, 4)
            ]
        )

    return ft.AlertDialog(
        on_dismiss=lambda e: setter(False),
        content_padding=0,
        actions_padding=0,
        title_padding=0,
        shape=ft.RoundedRectangleBorder(radius=2),
        content=ft.Container(
            padding=10,
            content=LevelGrid(), # Insert component here
        ),
    )

def formulaBookSelection(handle_new, handle_delete, setter) -> ft.AlertDialog:
    
    @ft.component
    def FormulaBookList():
        save_data = ft.use_context(AppContext).save_data
        formula_book = ft.use_context(AppContext).current_formula_book
       
        def handle_dialog_select(e):
            formula_book.update(save_data[e.control.key], e.control.key)
            setter(False)

        return ft.Column( 
            scroll=ft.ScrollMode.AUTO, 
            spacing=2,
            controls=[
                ft.Row(
                    controls=[
                        ft.Button(
                            key=bookID,
                            expand=True,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=2),
                                padding=ft.Padding(top=10, left=10, right=10, bottom=12),
                                alignment=ft.Alignment.CENTER_LEFT,
                                bgcolor=ft.Colors.ON_SECONDARY if bookID == formula_book.id else ft.Colors.SURFACE_CONTAINER,
                            ),
                            on_click=handle_dialog_select,
                            content=ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text(f"{save_data.get(bookID).get('name')} ", size=16),
                                    ft.Text(f"level: {save_data.get(bookID).get('level')}", size=14)
                                ],
                            )
                        ),
                    ],
                    expand=True,
                ) for bookID in save_data
            ]
        )
   
    return ft.AlertDialog(
        on_dismiss=lambda e: setter(False),
        content_padding=0,
        expand=True,
        actions_padding=0,
        title_padding=0,
        shape=ft.RoundedRectangleBorder(radius=2),
        content=ft.Container(
            width=800,   
            height=600, 
            expand=True,
            padding=2,
            content=FormulaBookList(), # Insert component here
        ),
        actions=[
            ft.Row( 
                controls=[
                    ft.TextButton(expand=True, content="New Book", icon=ft.Icons.STAR_BORDER, icon_color=ft.Colors.BLUE_300, on_click=handle_new, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2), padding=10)),
                    ft.TextButton(expand=True, content="Delete", icon=ft.Icons.STAR_BORDER, icon_color=ft.Colors.BLUE_300, on_click=handle_delete, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2), padding=10)),
                    ft.TextButton(expand=True, content="Close", icon=ft.Icons.STAR_BORDER, icon_color=ft.Colors.BLUE_300, on_click=lambda e: setter(False), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2), padding=10)),
                ]
            )
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    )

@ft.component
def refreshLayer(level: int, key, setter):
    save_data = ft.use_context(AppContext).save_data
    formula_book = ft.use_context(AppContext).current_formula_book
    db = ft.use_context(AppContext).db

    def handle_select(e, t):
        formula_book.mark_free(key.current, t)
        write_save(formula_book, save_data)
        setter(False)

    items_per_page = 20
    items = [db.filter_items(id=id, hide_excluded=False, is_outer_item=True, remaster_only=False)[0] for id in formula_book.formulae]
    items = sorted([el for el in items if el.get("id") not in formula_book.get_free() and el.get('level') <= level], key=lambda x: x['level'])

    current_page = ft.use_ref(1)
    def handle_page_shift(s):
        current_page.current = s

    total_pages = max(1, (len(items) + items_per_page - 1) // items_per_page)
    start_idx = (current_page.current - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    current_items = items[start_idx:end_idx]
    
    page_nav = ft.Container(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
            controls=[
                ft.IconButton(icon=ft.Icons.FIRST_PAGE, disabled=current_page.current == 1, on_click=lambda e: handle_page_shift(1)),
                ft.IconButton(icon=ft.Icons.NAVIGATE_BEFORE, disabled=current_page.current == 1, on_click=lambda e: handle_page_shift(current_page.current - 1)),
                ft.Text(f"{current_page.current} / {total_pages}", weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.Icons.NAVIGATE_NEXT, disabled=current_page.current == total_pages, on_click=lambda e: handle_page_shift(current_page.current + 1)),
                ft.IconButton(icon=ft.Icons.LAST_PAGE, disabled=current_page.current == total_pages, on_click=lambda e: handle_page_shift(total_pages))
            ]
        ), padding=-5
    )

    content = [
        ft.Row(
            controls=[
                ft.Button(
                    content=ft.Row([ft.Text(f"{formula.get('name')}"), ft.Container(expand=True), ft.Text(f"Level {formula.get('level')}")]),
                    key=formula.get("id"),
                    expand=True,
                    on_click=lambda e, t=formula.get('id'): handle_select(e, t),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=2),
                        padding=ft.Padding(top=10, left=10, right=10, bottom=12),
                        alignment=ft.Alignment.CENTER,
                        bgcolor=ft.Colors.SURFACE_CONTAINER,
                    ),
                ) 
            ]
        ) for formula in current_items
    ]

    return ft.Column(
        scroll=ft.ScrollMode.AUTO if len(content) >= 14 else None, 
        controls=content if len(content) else [
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text("No matching content..."),
                        expand=True,
                        shape=ft.RoundedRectangleBorder(radius=2),
                        padding=ft.Padding(top=10, left=10, right=10, bottom=12),
                        alignment=ft.Alignment.CENTER,
                    ) 
                ]
            )
        ]
    )

def formulaSelection(key, setter) -> ft.AlertDialog:
    level = 1
    if not isinstance(key.current, str):
        level = int(key.current)

    return ft.AlertDialog(
        on_dismiss=lambda e: setter(False),
        content_padding=0,
        actions_padding=0,
        title_padding=0,
        shape=ft.RoundedRectangleBorder(radius=2),
        content=ft.Container(
            padding=10,
            content=refreshLayer(level, key, setter), # Insert component here
        ),
        actions=[
            ft.Row( 
                controls=[
                    ft.TextButton(expand=True, content="Ok", icon=ft.Icons.STAR_BORDER, icon_color=ft.Colors.BLUE_300, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2), padding=10)),
                    ft.TextButton(expand=True, content="Cancel", icon=ft.Icons.STAR_BORDER, icon_color=ft.Colors.BLUE_300, on_click=lambda e: setter(False), style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=2), padding=10)),
                ]
            )
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    )


@ft.component
def itemSlot(key_val, order):
    db = ft.use_context(AppContext).db
    save_data = ft.use_context(AppContext).save_data
    formula_book = ft.use_context(AppContext).current_formula_book

    def handle_click(e):
        formula_book.remove_free(key_val, order)
        write_save(formula_book, save_data)

    items = formula_book.free_selection.get(key_val, [])
    item = None

    if items and len(items) > order:
        item = db.filter_items(id=items[order], hide_excluded=False, is_outer_item=False, remaster_only=False)[0]
    
    return ft.Card(
        bgcolor=ft.Colors.ON_SECONDARY_FIXED,
        variant=ft.CardVariant.FILLED,
        shape=ft.RoundedRectangleBorder(radius=2),
        margin=0,
        elevation=3,
        content=ft.Container(
            on_click=handle_click,
            content=ft.Row(
                expand=True,
                expand_loose=True,
                controls=[
                    ft.Text(f"{item.get('name')}", weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(f"Level {item.get('level')} | {item.get('item_subcategory', 'Item')}")
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ) if item else ft.Row([ft.Text("Invalid Item!")], expand=True, alignment=ft.MainAxisAlignment.CENTER,),
            padding=12
        )
    )

@ft.component
def formulaCategory(sub_dialog, title, key_ref, value, slots):
    formula_book = ft.use_context(AppContext).current_formula_book

    def handle_free_slot_click(e):
        key_ref.current = value
        sub_dialog(True)    

    outputList = [itemSlot(value, i) for i, _ in enumerate(formula_book.free_selection.get(value, []))]
    remaining = slots - len(formula_book.free_selection.get(value, []))
    
    if remaining:
        outputList.append(
            ft.Card(
                bgcolor=ft.Colors.ON_SECONDARY_FIXED,
                variant=ft.CardVariant.FILLED,
                shape=ft.RoundedRectangleBorder(radius=4),
                margin=0,
                elevation=3,
                content=ft.Container(
                    on_click=handle_free_slot_click,
                    content=ft.Row([ft.Text(f"{remaining} slots remaining")], expand=True, alignment=ft.MainAxisAlignment.CENTER,),
                    padding=12
                )
            )
        )
        
    return ft.Container(
        padding=10,
        border_radius=4,
        bgcolor=ft.Colors.ON_SECONDARY,
        content=ft.Column(
            spacing=5,
            controls=[
                ft.Row(controls=[ft.Text(title, weight=ft.FontWeight.BOLD, size=16)], alignment=ft.MainAxisAlignment.CENTER),
                *outputList,
            ]
        )
    )

def freeSelection(level: int, key, setter, sub_dialog) -> ft.AlertDialog:
    return ft.AlertDialog(
        on_dismiss=lambda e: setter(False),
        content_padding=0,
        actions_padding=0,
        title_padding=0,
        shape=ft.RoundedRectangleBorder(radius=2),
        content=ft.Container(
            padding=7,
            content=ft.Column(
                spacing=5,
                scroll=ft.ScrollMode.AUTO, 
                controls=[
                    formulaCategory(sub_dialog, "Alchemical Crafting", key, "AC", 4),
                    formulaCategory(sub_dialog, "Research field", key, "RF", 2),
                    *[formulaCategory(sub_dialog, f"Level {i}", key, i, 4 if i == 1 else 2) for i in range(1, level + 1)],
                ]
            ),
        )
    )