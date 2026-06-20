import flet as ft
from appstate import FormulaBook, AppContext
import aon_database as aon

def formulaSelectionDialog(formula_book,db,key,setter):

    items = [db.filter_items(id = id, hide_excluded=False, is_outer_item=False,remaster_only=False)[0] for id in formula_book.formulas]
    def handle_select(e,t):
        formula_book.mark_free(key,t)



    return ft.AlertDialog(
        on_dismiss=lambda: setter(False),
        content_padding=0,
        actions_padding=0,
        title_padding=0,
        shape=ft.RoundedRectangleBorder(radius=2),
        content=ft.Container(

            padding=10,
            content= ft.Column(
                #tight =True,
                controls = [
                    ft.Row(
                        
                        controls=[
                            ft.Button(
                                content = ft.Row([ft.Text(f"{formula.get("name")}"),ft.Container(expand=True),ft.Text(f"Level {formula.get("level")}")]),
                                key = formula.get("id"),
                                expand=True,
                                on_click=lambda e,t=formula.get('id'): handle_select(e,t),
                                style=ft.ButtonStyle(
                                    shape = ft.RoundedRectangleBorder(radius=2),
                                    padding = ft.Padding(top = 10, left = 10, right = 10, bottom = 12),
                                    alignment=ft.Alignment.CENTER,
                                    bgcolor = ft.Colors.ON_SECONDARY if False else ft.Colors.SURFACE_CONTAINER,
                                ),
                            ) 
                        ]
                    ) for formula in sorted([el for el in items if el.get("id") not in formula_book.get_free()], key=lambda x: x['level'])
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


@ ft.component
def freeFormulas(formula_book):


    items = [ft.Text(i) for i in range(0,10)]

    db = ft.use_context(AppContext).db
    
    show_formula_selection_dialog, set_show_formula_selection_dialog = ft.use_state(False)
    target_selection, set_target_selection = ft.use_state("AC")

    ft.use_dialog(
        formulaSelectionDialog(
            formula_book,db,target_selection, set_show_formula_selection_dialog
        )
        if show_formula_selection_dialog else None
    )



    @ft.component
    def itemSlot(key,order,no_item):
        
        def handle_click(e,select):
            if select:
                set_target_selection(key)
                set_show_formula_selection_dialog(True)
                print("add!")
            else:
                formula_book.remove_free(key,order)
                print("rem!")

        items = formula_book.free_selection.get(key,[])
        item = None

        if items and len(items) >order:
            item = db.filter_items(id = items[order], hide_excluded=False, is_outer_item=False,remaster_only=False)[0]
        

        return ft.Card(
                bgcolor=ft.Colors.ON_SECONDARY_FIXED,
                variant=ft.CardVariant.FILLED,
                shape=ft.RoundedRectangleBorder(radius=2),
                margin=0,
                elevation=3,
                content= ft.Container(
                    expand=True,
                    on_click=lambda e: handle_click(e,item is None),
                    content=ft.Row(
                        expand=True,
                        controls=[
                                ft.Text(f"{item.get('name')}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"Level {item.get('level')} | {item.get('item_subcategory', 'Item')}")
                                ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ) if item else ft.Row([ft.Text(no_item)],expand=True,alignment=ft.MainAxisAlignment.CENTER,),
                    padding=12
                )
            )


    return ft.Column(
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO, 
        controls=[
            ft.Container(
                bgcolor=ft.Colors.ON_SECONDARY,  
                padding=10,                  
                margin=0,    
                content=ft.Row(
                    controls=[
                        ft.Text("Alchemical Crafting",weight=ft.FontWeight.BOLD,size = 16),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ),
            ft.Container(
                content=ft.Column(controls=[itemSlot("AC",i,"A common first level item") for i in range(0,4)], expand=True, spacing=5),
                border=ft.Border.all(1),
                padding=0,
            ),
             ft.Container(
                bgcolor=ft.Colors.ON_SECONDARY,  
                padding=10,                  
                margin=0,    
                content=ft.Row(
                    controls=[
                        ft.Text("Research Field",weight=ft.FontWeight.BOLD,size = 16),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ),
            ft.Container(
                content=ft.Column(controls=items, spacing=0),
                border=ft.Border.all(1),
                padding=0,
            ),

            ft.Container(
                bgcolor=ft.Colors.ON_SECONDARY,  
                padding=10,                  
                margin=0,    
                content=ft.Row(
                    controls=[
                        ft.Text("Formula Book Feature",weight=ft.FontWeight.BOLD,size = 16),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ),
             ft.Container(
                content=ft.Column(controls=[itemSlot(1,i,"A common level 1 item") for i in range(0,2)], expand=True, spacing=5),
                border=ft.Border.all(1),
                padding=0,
            ),
            *[ft.Container(
                content=ft.Column(controls=[itemSlot(level,i,f"A common level {level} item") for i in range(3,4)], expand=True, spacing=5),
                border=ft.Border.all(1),
                padding=0,
            ) for level in range(1,formula_book.level+1) ]
          
        ]
    )

@ft.component
def AlchemistFreeFormulas():
    formula_book = ft.use_context(AppContext).current_formula_book
    
    free_only, set_free_only = ft.use_state(False)
    
    #app = ft.use_context(AppContext).app


    return ft.Column( controls =[
    freeFormulas(formula_book),
    ], expand=True)