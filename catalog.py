import flet as ft
from appstate import AppState, AppContext
import aon_database as aon
import re
from typing import Dict, Any

################################################################################################################################
# //////////////////////////////////////////// TRAITS ///////////////////////////////////////////////////////////////////////////
################################################################################################################################

def traitPlate(text: str, tooltip: str, on_delete) -> ft.Control:
    return ft.Container(
        ft.Button(
            content=text,
            on_click=on_delete,
            tooltip=tooltip,  
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=0),
                side=ft.BorderSide(width=2, color=ft.Colors.ON_PRIMARY)
            ) 
        )
    )

@ft.component 
def traitContainer():
    context = ft.use_context(AppContext)
    search_options = context.search_options
    trait_descriptions = context.trait_descriptions

    def handle_trait_plate_click(trait: str):
        search_options.remove_trait(trait)
    
    container = ft.Row(
        wrap=True,          
        spacing=10,           
        run_spacing=10,
        alignment=ft.MainAxisAlignment.START,
        controls=[
            traitPlate(trait, trait_descriptions.get(trait, ""), lambda e, t=trait: handle_trait_plate_click(t))
            for trait in search_options.traits
        ]
    )
    return container

################################################################################################################################
# /////////////////////////////////////////// SEARCH ////////////////////////////////////////////////////////////////////////////
################################################################################################################################

@ft.component 
def searchHeader(search_options: SearchOptions):
    entries = ft.Row(controls=[
        nameSearch(search_options),
        traitSearch(search_options)
    ])
    total = ft.Column(
        controls=[
            levelSlider(search_options),
            entries,
            traitContainer()
        ]
    )
    return total

@ft.component
def nameSearch(search_options: SearchOptions):
    def handle_name_search_update(e):
        search_options.set_name(e.control.value)

    return ft.TextField(
        label="Item name", value=search_options.name, expand=True, prefix_icon=ft.Icons.SEARCH, on_submit=handle_name_search_update
    )

@ft.component
def levelSlider(search_options: SearchOptions):
    def handle_level_change(e: ft.Event[ft.RangeSlider]): 
        search_options.set_levels(e.control.start_value, e.control.end_value)

    return ft.Column(
        controls=[
            ft.Container(height=20),
            ft.RangeSlider(
                divisions=20,
                min=0,
                max=20,
                start_value=search_options.min_level,
                end_value=search_options.max_level,
                on_change_end=handle_level_change,
                label="Level {value}",
            )
        ]
    )

@ft.component
def traitSearch(search_options: SearchOptions) -> ft.Control:
    trait_list = ft.use_context(AppContext).trait_descriptions
    trait_field, set_trait_field = ft.use_state("")
    
    def handle_change(e: ft.Event[ft.AutoComplete]):
        pass

    def handle_select(e: ft.AutoCompleteSelectEvent):
        search_options.add_trait(e.selection.value)
        set_trait_field("")

    content = ft.Row(
        controls=[
            ft.Container(
                content=ft.AutoComplete(
                    value="",
                    width=150,
                    on_change=handle_change,
                    on_select=handle_select,
                    suggestions=[
                        ft.AutoCompleteSuggestion(key=value, value=value)
                        for value in (set(trait_list) - set(search_options.traits))
                    ],
                ),
                border=ft.Border.all(1),
                border_radius=4,
                padding=ft.Padding.only(left=15, right=15, bottom=5),
                alignment=ft.Alignment.CENTER,
                height=48,
                clip_behavior=ft.ClipBehavior.NONE
            )
        ]
    )
    return content

################################################################################################################################
# //////////////////////////////////////////// CATALOG LIST ////////////////////////////////////////////////////////////////////
################################################################################################################################

def format_actions(match_obj):
    match match_obj.group(1).strip():
        case "Single Action": return '`a` '
        case "Two Actions": return '`d` '
        case "Three Actions": return '`d` '
        case "Free Action": return '`.` '
        case "Reaction": return '`r` '
        case _: return ''

@ft.component
def ItemExpandedDetails(item: Dict[str, Any], db, trait_descriptions) -> ft.Control:
    descriptions = item.get('markdown', '')
    parsed_descriptions = [
        re.sub(r'\[(.*?)]\((\/.*?)\)',
               lambda t: f"[{t.group(1)}](https://2e.aonprd.com/{t.group(2)})",
               text.group(1).strip()) for text in re.finditer(
            r'<title.*?<\/column>.*?.(?:\s*?---\s*)?(.*?)(?=<c|<t|$)',
            descriptions,
            flags=re.DOTALL
        )
    ]

    parsed_descriptions = [re.sub(r'<actions.*?"(.*?)".+?>(?: Interact)?(?:[; ]+)?', format_actions, text) for text in parsed_descriptions]
    parsed_descriptions = [re.sub(r'<br \/>', r'\n', text) for text in parsed_descriptions]

    async def handle_link_click(e):
        if e.data:
            await ft.context.page.launch_url(e.data)

    children_ids = item.get('item_child_id')
    child_controls = []
    
    if children_ids:
        resolved_children = [db.filter_items(id=child, hide_excluded=False, is_outer_item=False, remaster_only=False)[0] for child in children_ids]
        
        for child_num, child in enumerate(resolved_children):
            desc_idx = child_num + 1
            has_desc = desc_idx < len(parsed_descriptions) and parsed_descriptions[desc_idx]
            child_controls.append(
                ft.Row(
                    expand=True,
                    controls=[
                        ft.Card(
                            bgcolor=ft.Colors.ON_SECONDARY_FIXED,
                            variant=ft.CardVariant.FILLED,
                            expand=True,
                            elevation=3,
                            content=ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(f"{child.get('name')} Level {child.get('level')}", weight=ft.FontWeight.BOLD),
                                        *([ft.Markdown(parsed_descriptions[desc_idx])] if has_desc else [])
                                    ],
                                    expand=True
                                ),
                                padding=12,
                            )
                        )
                    ]
                )
            )

    main_desc = parsed_descriptions[0] if parsed_descriptions else ""

    return ft.Row(
        controls=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    content=ft.Markdown(
                        main_desc,
                        selectable=True,
                        on_tap_link=handle_link_click,
                        md_style_sheet=ft.MarkdownStyleSheet(
                            code_text_style=ft.TextStyle(font_family="PF2e Icons", size=25)
                        )
                    ),
                    padding=12,
                )
            ] + child_controls,
        )
    )

@ft.component
def ItemCardCheckbox(item_id: str):
    formula_book = ft.use_context(AppContext).current_formula_book
    r,reset = ft.use_state(False)



    def handle_click(e):
        reset(not r)
        formula_book.switchItem(item_id)

    return ft.Container(
        #bgcolor = ft.Colors.PRIMARY,
        border_radius=5,
        padding=25,
        content=ft.Icon(
            ft.Icons.BOOKMARK_ROUNDED if item_id in formula_book.formulas else ft.Icons.BOOKMARK_BORDER_ROUNDED,
            size = 30,
            color=ft.Colors.PRIMARY
        ),
        on_click=handle_click
    )

@ft.component
def itemCard(item: Dict[str, Any]) -> ft.Control:
    formula_book = ft.use_context(AppContext).current_formula_book
    db = ft.use_context(AppContext).db
    trait_descriptions = ft.use_context(AppContext).trait_descriptions

    expanded, expand = ft.use_state(False)

    def on_card_press(e):
        expand(not expanded)

    trait_list = ft.Row(
        spacing=5,
        controls=[
            ft.Card(
                bgcolor=ft.Colors.ON_SECONDARY_FIXED,
                variant=ft.CardVariant.FILLED,
                shape=ft.RoundedRectangleBorder(radius=2),
                margin=0,
                elevation=3,
                content=ft.Container(
                    border=ft.Border.all(0, ft.Colors.ON_SECONDARY_FIXED),
                    tooltip=trait_descriptions.get(trait), 
                    content=ft.Text(trait, size=13),       
                    padding=ft.Padding(left=3, right=3, bottom=1, top=1),              
                ),
            )
            for trait in item.get('trait', [])
        ],
    )
    price = aon.formula_price(item.get("level", ""))

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
                        ft.Text(f"Level {item.get('level')} | {item.get('item_subcategory', 'Item')}")
                    ],
                    expand=True,
                    spacing=5
                ),
                ft.Text(f"{price[1] if len(price) > 1 else price}", italic=True),
                ItemCardCheckbox(item_id=item.get("id")),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ), 
        padding=12
    )

    return ft.Column(
        controls=[
            ft.Card(
                bgcolor=ft.Colors.ON_SECONDARY,
                content=ft.Column(
                    spacing=2,
                    controls=[
                        title_panel,
                        *([ItemExpandedDetails(item, db, trait_descriptions)] if expanded else [])
                    ]
                )
            )
        ]
    )

@ft.component
def catalogList(search_options: SearchOptions):
    db = ft.use_context(AppContext).db
    
    items = sorted(db.filter_items(
       name=search_options.name if len(search_options.name) else None,
       traits={"and": search_options.traits} if len(search_options.traits) else None,
       max_level=search_options.max_level,
       min_level=search_options.min_level
    ), key=lambda x: x['level'])
    
    if not items:
        return ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Text("No items match your criteria.", size=16), 
                    padding=20, 
                    alignment=ft.Alignment.CENTER
                )
            ],
        )

    items_per_page = 30
    total_pages = max(1, (len(items) + items_per_page - 1) // items_per_page)
    start_idx = (search_options.catalog_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    
    current_items = items[start_idx:end_idx]
    

    page_nav = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        controls=[
            ft.IconButton(
                icon=ft.Icons.FIRST_PAGE,
                disabled=search_options.catalog_page == 1,
                on_click=lambda e: search_options.set_catalog_page(1)
            ),
            ft.IconButton(
                icon=ft.Icons.NAVIGATE_BEFORE,
                disabled=search_options.catalog_page == 1,
                on_click=lambda e: search_options.set_catalog_page(search_options.catalog_page - 1)
            ),
            ft.Text(f"{search_options.catalog_page} / {total_pages}", weight=ft.FontWeight.BOLD),
            ft.IconButton( 
                icon=ft.Icons.NAVIGATE_NEXT,
                disabled=search_options.catalog_page == total_pages,
                on_click=lambda e: search_options.set_catalog_page(search_options.catalog_page + 1)
            ),
            ft.IconButton(
                icon=ft.Icons.LAST_PAGE,
                disabled=search_options.catalog_page == total_pages,
                on_click=lambda e: search_options.set_catalog_page(total_pages)
            )
        ]
    )

    item_controls = [page_nav]
    item_controls+=[itemCard(item) for item in current_items]
    item_controls.append(page_nav)



    return ft.Column(
        expand=True,
        controls=[
            ft.ListView(controls=item_controls, expand=True, spacing=5, padding=10)
        ]
    )
################################################################################################################################
# //////////////////////////////////////////// CATALOG //////////////////////////////////////////////////////////////////////////
################################################################################################################################

@ft.component
def AlchemicalCatalogPage():
    search_options = ft.use_context(AppContext).search_options
    return ft.Container(
        padding=10,
        expand=True,
        content=ft.Column(controls=[
            searchHeader(search_options),
            ft.Divider(),
            catalogList(search_options),
        ], expand=True),
    )