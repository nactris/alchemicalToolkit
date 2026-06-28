import flet as ft
from appstate import FormulaBook, AppContext
import aon_database as aon


def levelSelection(formula_book,setter):
    def handle_level_select(e):
        formula_book.set_level(e.control.key)
        setter(False)

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
            # ft.Row( 
            #     controls=[
            #         ft.TextButton(
            #             expand=True,
            #             content="Ok",
            #             icon=ft.Icons.STAR_BORDER,
            #             icon_color=ft.Colors.BLUE_300,
            #             on_click = handle_new,
            #             style=ft.ButtonStyle(
            #                 shape=ft.RoundedRectangleBorder(radius=2),
            #                 padding=10,
            #             ),
            #         ),
            #         ft.TextButton(
            #             expand=True,
            #             content="Cancel",
            #             icon=ft.Icons.STAR_BORDER,
            #             icon_color=ft.Colors.BLUE_300,
            #             on_click = handle_close,
            #             style=ft.ButtonStyle(
            #                 shape=ft.RoundedRectangleBorder(radius=2),
            #                 padding=10,
            #             ),
            #         ),
            #     ]
            # )
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    )

def formulaBook(formula_book,handle_new,handle_delete,setter,save_data) -> ft.AlertDialog:
    def handle_dialog_select(e):
        formula_book.update(save_data.current[e.control.key],e.control.key)
        setter(False)

    @ft.component
    def formulaBookOption(formulaID:str,selected:bool):
        return ft.Row(
            controls=[
                    ft.Button(
                    key=formulaID,
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
                            ft.Text(f"{save_data.current.get(formulaID).get('name')} ", size = 16),
                            ft.Text(f"level: {save_data.current.get(formulaID).get('level')} <space> price?", size = 14)
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
                controls=[formulaBookOption(bookID,bookID==formula_book.id) for bookID in save_data.current],
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

def formulaSelection(formula_book,db,key,setter,save):

    items = [db.filter_items(id = id, hide_excluded=False, is_outer_item=False,remaster_only=False)[0] for id in formula_book.formulas]
    def handle_select(e,t):
        formula_book.mark_free(key.current,t)
        save()



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

def freeSelection(formula_book,db,key,setter,sub_dialog,save):


    items = [ft.Text(i) for i in range(0,10)]

    @ft.component
    def itemSlot(key,order):
        
        def handle_click(e):
            formula_book.remove_free(key,order)
            print(key,order)
            save()

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
                    on_click=handle_click,
                    content=ft.Row(
                        expand=True,
                        controls=[
                                ft.Text(f"{item.get('name')}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(f"Level {item.get('level')} | {item.get('item_subcategory', 'Item')}")
                                ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ) if item else ft.Row([ft.Text("Invalid Item!")],expand=True,alignment=ft.MainAxisAlignment.CENTER,),
                    padding=12
                )
            )
    
    def handle_free_slot_click(e,k):
        key.current = k
        sub_dialog(True)


    def itemSlotList(key,slots):

        outputList = [itemSlot(key,i) for i,_ in enumerate(formula_book.free_selection.get(key,[]))]
        remaining = slots-len(formula_book.free_selection.get(key,[]))
        if remaining:
            outputList.append(
                ft.Card(
                    bgcolor=ft.Colors.ON_SECONDARY_FIXED,
                    variant=ft.CardVariant.FILLED,
                    shape=ft.RoundedRectangleBorder(radius=2),
                    margin=0,
                    elevation=3,
                    content= ft.Container(
                        expand=True,
                        on_click=lambda e,k=key: handle_free_slot_click(e,k) ,
                        content=ft.Row([ft.Text(f"{remaining} slots remaining")],expand=True,alignment=ft.MainAxisAlignment.CENTER,),
                        padding=12
                    )
                )
            )
        return outputList


    ACselection = itemSlotList("AC",4)
    RFselection = itemSlotList("RF",2)


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
                        content=ft.Column(controls=ACselection, expand=True, spacing=5),
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
                        content=ft.Column(controls=RFselection, spacing=0),
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
                   
                
                ]
            ),
        ),
        # actions=[
        #     ft.Row( 
        #         controls=[
        #             ft.TextButton(
        #                 expand=True,
        #                 content="New Book",
        #                 icon=ft.Icons.STAR_BORDER,
        #                 icon_color=ft.Colors.BLUE_300,
        #                 on_click = handle_new,
        #                 style=ft.ButtonStyle(
        #                     shape=ft.RoundedRectangleBorder(radius=2),
        #                     padding=10,
        #                 ),
        #             ),
        #             ft.TextButton(
        #                 expand=True,
        #                 content="Delete",
        #                 icon=ft.Icons.STAR_BORDER,
        #                 icon_color=ft.Colors.BLUE_300,
        #                 on_click = handle_delete,
        #                 style=ft.ButtonStyle(
        #                     shape=ft.RoundedRectangleBorder(radius=2),
        #                     padding=10,
        #                 ),
        #             ),
        #             ft.TextButton(
        #                 expand=True,
        #                 content="Close",
        #                 icon=ft.Icons.STAR_BORDER,
        #                 icon_color=ft.Colors.BLUE_300,
        #                 on_click = lambda e: setter(False),
        #                 style=ft.ButtonStyle(
        #                     shape=ft.RoundedRectangleBorder(radius=2),
        #                     padding=10,
        #                 ),
        #             ),
        #         ]
        #     )
        # ],
        # actions_alignment=ft.MainAxisAlignment.SPACE_EVENLY,
    )

@ft.component
def AlchemistFreeFormulas():
    formula_book = ft.use_context(AppContext).current_formula_book
    
    free_only, set_free_only = ft.use_state(False)
    
    #app = ft.use_context(AppContext).app


    return ft.Column( controls =[
    freeFormulas(formula_book),
    ], expand=True)