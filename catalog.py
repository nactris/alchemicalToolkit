import flet as ft
from appstate import AppState, AppContext, FormulaBook, write_save
from search import *
import aon_database as aon
import re
from typing import Dict, Any

def format_actions(match_obj):
    match match_obj.group(1).strip():
        case "Single Action": return '`a` '
        case "Two Actions": return '`d` '
        case "Three Actions": return '`d` '
        case "Free Action": return '`.` '
        case "Reaction": return '`r` '
        case _: return ''

@ft.component
def ItemExpandedDetails(item: Dict[str, Any], trait_descriptions) -> ft.Control:
    db = ft.use_context(AppContext).db
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
    save_data = ft.use_context(AppContext).save_data

    def handle_click(e):
        # FormulaBook is @ft.observable, modifying it automatically triggers Flet to re-render
        formula_book.switchItem(item_id)
        write_save(formula_book, save_data)

    return ft.Container(
        border_radius=5,
        padding=25,
        content=ft.Icon(
            ft.Icons.BOOKMARK_ROUNDED if item_id in formula_book.formulae else ft.Icons.BOOKMARK_BORDER_ROUNDED,
            size=30,
            color=ft.Colors.PRIMARY
        ),
        on_click=handle_click
    )

@ft.component
def itemCard(item: Dict[str, Any]) -> ft.Control:
    formula_book = ft.use_context(AppContext).current_formula_book
    trait_descriptions = ft.use_context(AppContext).trait_descriptions

    expanded, expand = ft.use_state(False)

    def on_card_press(e):
        expand(not expanded)

    trait_list = ft.Row(
        spacing=5,
        wrap=True,        
        run_spacing=5,   
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

    price = aon.formula_price(item.get("level", "")) if not item.get("id","") in formula_book.get_free() else [0, "Free"]

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
                        *([ItemExpandedDetails(item, trait_descriptions)] if expanded else [])
                    ]
                )
            )
        ]
    )

@ft.component
def savedFormulaBar():
    save_data = ft.use_context(AppContext).save_data
    db = ft.use_context(AppContext).db
    formula_book = ft.use_context(AppContext).current_formula_book
    
    import dialogs
    show_formula_dialog, set_show_formula_dialog = ft.use_state(False)
    show_level_dialog, set_show_level_dialog = ft.use_state(False)
    show_free_selection, set_show_free_selection = ft.use_state(False)
    show_formula_selection_dialog, set_show_formula_selection_dialog = ft.use_state(False)

    def get_total_formulabook_price():
        return divmod(
            sum(
                map(
                    lambda e: aon.formula_price(e.get("level", ""))[0],
                    filter(
                        lambda i: not i.get('id') in formula_book.get_free(),
                        [db.filter_items(id=item, hide_excluded=False, is_outer_item=False, remaster_only=False)[0] for item in formula_book.formulae]
                    )
                )
            ),
            1
        )
             
    target_selection = ft.use_ref("AC")

    reset_val, reset = ft.use_state(True)

    def handle_formula_dialog_new(e):
        pass # Implement later

    def handle_formula_dialog_delete(e):
        pass # Implement later

    ft.use_dialog(
        dialogs.formulaBookSelection(
            handle_new=handle_formula_dialog_new,
            handle_delete=handle_formula_dialog_delete,
            setter=set_show_formula_dialog,
        ) if show_formula_dialog else None
    )

    ft.use_dialog(
        dialogs.levelSelection(
            setter=set_show_level_dialog
        )
        if show_level_dialog else None
    )

    ft.use_dialog(
        dialogs.freeSelection(
            level=formula_book.level,
            key=target_selection,
            setter=set_show_free_selection,
            sub_dialog=set_show_formula_selection_dialog,
        )
        if show_free_selection else None
    )

    ft.use_dialog(
        dialogs.formulaSelection(
            key=target_selection,
            setter=set_show_formula_selection_dialog,
        )
        if show_formula_selection_dialog else None
    )
  
    def handle_blur(e):
        reset(not reset_val)

    def handle_rename(e):
        formula_book.set_name(e.control.value)
        write_save(formula_book, save_data)

    total_gp, total_sp = get_total_formulabook_price()
    total_gp = int(total_gp)
    total_sp = int(total_sp * 10)
    total = "Price: " + (f"{total_gp} gp" if total_gp else "") + (f"{' ' if total_gp else ''}{total_sp} sp" if total_sp else "" + "Free" if not total_gp and not total_sp else "")
    
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    border_radius=4,
                    padding=5,
                    border=ft.Border.all(color=ft.Colors.PRIMARY, width=2),
                    content=ft.Text("Formula Book"),
                    on_click=lambda e: set_show_formula_dialog(True)
                ),
                ft.TextField(
                    label='Name',
                    value=formula_book.name,
                    on_submit=handle_rename, 
                    on_blur=handle_blur,
                ),
                ft.Container(expand=True),
                ft.Text(total),
                ft.TextButton(
                    "Free formulas",
                    style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=5),
                            padding=10,
                            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW
                        ),
                    on_click=lambda e: set_show_free_selection(True)
                ),
                ft.Button(
                    style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=5),
                            padding=10,
                        ),
                    content=ft.Text(f"Level {formula_book.level}"),
                    on_click=lambda e: set_show_level_dialog(True)
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        ),
        bgcolor=ft.Colors.ON_SECONDARY,  
        padding=10,                  
        margin=0,               
    )


@ft.component
def catalogList(search_options: SearchOptions):
    db = ft.use_context(AppContext).db
    formula_book = ft.use_context(AppContext).current_formula_book
    
    # Memoize the database query so it only runs when search filters actually change
    def fetch_items():
        return db.filter_items(
            name=search_options.name if len(search_options.name) else None,
            traits={"and": search_options.traits} if len(search_options.traits) else None,
            max_level=search_options.max_level,
            min_level=search_options.min_level
        )
    
    raw_items = ft.use_memo(fetch_items, [search_options.name, str(search_options.traits), search_options.max_level, search_options.min_level])

    items = sorted(
        filter(lambda i: (not search_options.known_only or i.get('id') in formula_book.formulae), raw_items), 
        key=lambda x: x[search_options.sort], 
        reverse=not search_options.sort_asc
    )
    
    if not items:
        return ft.Column(
            expand=True,
            controls=[
                ft.ListView(
                    controls=[
                        ft.Container(
                            content=ft.Text("No items match your criteria.", size=16), 
                            padding=20, 
                            alignment=ft.Alignment.CENTER
                        )
                    ],
                )
            ]
        )

    items_per_page = 20
    total_pages = max(1, (len(items) + items_per_page - 1) // items_per_page)
    start_idx = (search_options.catalog_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    current_items = items[start_idx:end_idx]
    
    page_nav = ft.Container(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=0,
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
        ), 
        padding=-5
    )

    item_controls = [itemCard(item) for item in current_items]

    return ft.Column(
        expand=True,
        controls=[
            ft.ListView(controls=item_controls, expand=True, spacing=5, padding=0),
            page_nav
        ]
    )


@ft.component
def AlchemicalCatalogPage():
    search_options = ft.use_context(AppContext).search_options
    
    return ft.Container(
        padding=10,
        expand=True,
        content=ft.Row(spacing=5, controls=[
            ft.Container(width=300, content=searchTab(search_options), bgcolor=ft.Colors.SURFACE_CONTAINER, border_radius=8, padding=10),
            ft.Container(
                expand=True, 
                content=ft.Column(spacing=15, controls=[savedFormulaBar(), catalogList(search_options)]), 
                padding=0
            ),
        ], expand=True),
    )