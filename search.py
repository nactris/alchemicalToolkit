import flet as ft
from appstate import AppState, AppContext,FormulaBook

def traitPlate(text: str, on_delete, on_negate, negated: bool) -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    value=text,
                    size=14,
                ),
                ft.IconButton(
                    icon=ft.Icons.BLOCK,
                    icon_color=ft.Colors.ERROR_CONTAINER if negated else ft.Colors.PRIMARY_CONTAINER,
                    on_click=on_negate,
                    icon_size=16,
                    padding=0,
                    visual_density=ft.VisualDensity.COMPACT,
                    tooltip="Exclude trait?",
                ),

            ],
            spacing=8,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(vertical=4, horizontal=5),
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,  
        border=ft.Border.all(1, ft.Colors.PRIMARY), 
        border_radius=6,
        
        on_click=on_delete, 
    )


@ft.component 
def searchTab(search_options: SearchOptions):
    return ft.Column(
        alignment = ft.MainAxisAlignment.START,
        controls=[
            #select added 
            #filter by some other stuff descriptions?
            nameSearch(search_options),
            traitSearch(search_options),
            levelSearch(search_options)
            
        ]
    )

@ft.component
def nameSearch(search_options: SearchOptions):
    def handle_name_search_update(e):
        search_options.set_name(e.control.value)

    def handle_sort_update(e):
        search_options.sort = e.control.value

    def handle_reset(e):
        search_options.min_level=0
        search_options.max_level=20
        search_options.traits={}
        search_options.name =""


    return ft.Container(
        padding=15,
        border_radius=8,
        border=ft.Border.all(1.5, ft.Colors.PRIMARY_CONTAINER),
        content=ft.Column(
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.TextField(
                    value=search_options.name,
                    prefix_icon=ft.Icon(ft.Icons.SEARCH, color=ft.Colors.PRIMARY),
                    label="Search Name",
                    hint_style=ft.TextStyle(color=ft.Colors.PRIMARY),
                    #color=ft.Colors.ON_PRIMARY,
                    border_color=ft.Colors.PRIMARY,
                    #cursor_color=ft.Colors.ON_PRIMARY,
                    text_size=14,
                    content_padding=10,
                    on_submit=handle_name_search_update,
                ),
                ft.Row(
                    #tight=True,
                    spacing=5,
                    controls=[
                        ft.Dropdown(
                            value=search_options.sort,
                            height=40,
                            expand=True,
                            # color=ft.Colors.ON_PRIMARY,
                            on_select = handle_sort_update,
                            border_color=ft.Colors.PRIMARY,
                            content_padding=ft.Padding.only(left=10, right=5),
                            options=[
                                ft.DropdownOption(text="Level",key="level"),
                                ft.DropdownOption(text="Name",key="name"),
                            ],
                        ),
                        ft.IconButton(
                            icon=ft.CupertinoIcons.SORT_UP if search_options.sort_asc else ft.CupertinoIcons.SORT_DOWN,
                            # icon_color=ft.Colors.ON_PRIMARY,
                            on_click = lambda e: search_options.check_sort(),
                            icon_size=22,
                            tooltip="Toggle Direction",
                        ),
                            
                    ],
                ),
                ft.TextButton(
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1, ft.Colors.PRIMARY),
                        shape=ft.RoundedRectangleBorder(radius=6),
                        bgcolor = ft.Colors.SURFACE_CONTAINER_LOW,
                    ),
                    content="Known only",
                    icon=ft.Icon(ft.Icons.BOOKMARKS_ROUNDED if search_options.known_only else ft.Icons.BOOKMARKS_OUTLINED, color=ft.Colors.PRIMARY),
                    on_click=lambda e: search_options.check_known() # set_free_only(not free_only)
                ),
                ft.Button(
                    content="Clear All Filters",
                    on_click = handle_reset, 
                    style=ft.ButtonStyle(
                        #color=ft.Colors.ON_PRIMARY,
                        side=ft.BorderSide(1, ft.Colors.PRIMARY),
                        shape=ft.RoundedRectangleBorder(radius=6),
                    ),
                ),
            ],
        ),
    )

@ft.component
def levelSearch(search_options: SearchOptions):
    def handle_level_change(e: ft.Event[ft.RangeSlider]): 
        search_options.set_levels(e.control.start_value, e.control.end_value)

    def handle_level_change(e,is_max):
        if is_max:
            search_options.max_level=int(e.control.value)
        else:
            search_options.min_level=int(e.control.value)


    return ft.Container(
        padding=15,
        border_radius=8,
        border=ft.Border.all(1.5, ft.Colors.PRIMARY_CONTAINER),
        content=ft.Row(
                spacing=5,
                controls=[
                    ft.Dropdown(
                        label="Min level",
                        value=str(search_options.min_level),
                        expand=True,
                        border_color=ft.Colors.PRIMARY,
                        content_padding=ft.Padding.only(left=10, right=5, top=0, bottom=0),
                        options=[ft.DropdownOption(text=str(i),key=i) for i in range(21)],
                        on_select=lambda e: handle_level_change(e,False),
                    ),
                    ft.Text("-"),
                    ft.Dropdown(
                        label="Max level",
                        value=str(search_options.max_level),
                        expand=True,
                        border_color=ft.Colors.PRIMARY,
                        content_padding=ft.Padding.only(left=10, right=5, top=0, bottom=0),
                        options=[ft.DropdownOption(text=str(i),key=i) for i in range(21)],
                        on_select=lambda e: handle_level_change(e,True),
                    ),
                ],
            ),
        )
    

@ft.component
def traitSearch(search_options: SearchOptions) -> ft.Control:
    trait_field, set_trait_field = ft.use_state("")
    trait_list = ft.use_context(AppContext).trait_descriptions

    def handle_change(e):
        pass

    def handle_select(e):
        search_options.add_trait(e.control.value)
        set_trait_field("")



    content = ft.Container(
        padding=15,
        border_radius=8,
        border=ft.Border.all(1.5, ft.Colors.PRIMARY_CONTAINER),
        content=ft.Row(
                    spacing=10,  
                    wrap=True,         
                    run_spacing=10,
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    controls=([
                    ft.Container(
                        padding=0,
                        border_radius=8,
                        border=ft.Border.all(1.5, ft.Colors.PRIMARY),
                        content=ft.Dropdown(
                            text_size=16,
                            margin=0,
                            enable_filter = True,
                            enable_search = True,
                            dense=True,
                            expand=True,
                            leading_icon = ft.Icons.SEARCH,
                            content_padding = ft.Padding.symmetric(vertical = 5, horizontal = 0),
                            value=trait_field,
                            editable=True,
                            menu_height=280,
                            label="Traits",
                            border=ft.InputBorder.NONE,
                            on_text_change=handle_change,
                            on_select=handle_select,
                                options=[
                                ft.DropdownOption(key=value, text=value)
                                for value in (set(trait_list) - set(search_options.traits.keys()))
                            ],
                        )
                    ),
                          
                    *[
                        traitPlate(
                            trait,
                            lambda e, t=trait: search_options.remove_trait(t),
                            lambda e, t=trait: search_options.negate(t),
                            not state
                        )
                        for trait,state in search_options.traits.items()
                    ]])
                )
            
        
    )
    return content