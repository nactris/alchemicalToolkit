import flet as ft
from typing import Dict, List, Any, Set
from aon_database import AlchemicalDatabase

# Initialize Backend Dependency
db = AlchemicalDatabase("alchemical_items.db")

class AppState:
    """Holds the raw data state of the application."""
    def __init__(self):
        self.search_name: str = ""
        self.min_level: int = 0
        self.max_level: int = 20
        self.sort_by: str = "name_asc"
        self.selected_ids: Set[str] = set()

    def get_filtered_items(self) -> List[Dict[str, Any]]:
        """Queries the database based strictly on the current state attributes."""
        items = db.filter_items(
            name=self.search_name, 
            min_level=self.min_level, 
            max_level=self.max_level
        )
        
        # Declarative functional sorting transformations
        sort_maps = {
            "name_asc": lambda x: x.get("name", "").lower(),
            "name_desc": lambda x: x.get("name", "").lower(),
            "level_asc": lambda x: x.get("level", 0),
            "level_desc": lambda x: x.get("level", 0),
        }
        
        reverse_sort = self.sort_by in ("name_desc", "level_desc")
        items.sort(key=sort_maps.get(self.sort_by, sort_maps["name_asc"]), reverse=reverse_sort)
        return items


# =====================================================================
# DECLARATIVE UI COMPONENT GENERATORS
# =====================================================================

def ItemTile(item: Dict[str, Any], is_selected: bool, on_toggle) -> ft.Card:
    """A pure functional component representing a single item card view."""
    return ft.Card(
        content=ft.Container(
            content=ft.Row(
                controls=[
                    ft.Checkbox(
                        value=is_selected, 
                        data=item.get("id"), 
                        on_change=on_toggle
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(item.get("name"), weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(
                                f"Level {item.get('level')} | {item.get('item_subcategory', 'Item')}"
                               
                            ),
                        ],
                        expand=True
                    ),
                    ft.Text(item.get("price_raw", ""), italic=True)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=12
        )
    )


def CatalogListView(items: List[Dict[str, Any]], selected_ids: Set[str], on_toggle) -> ft.ListView:
    """Maps a list of data objects into a scrollable list of ItemTiles."""
    if not items:
        return ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Text("No items match your criteria.", size=16), 
                    padding=20, 
                    alignment=ft.Alignment.CENTER
                )
            ],
            expand=True
        )

    return ft.ListView(
        controls=[ItemTile(item, item.get("id") in selected_ids, on_toggle) for item in items],
        expand=True,
        spacing=5,
        padding=10
    )


def BenchListView(selected_ids: Set[str], all_items: List[Dict[str, Any]]) -> ft.ListView:
    """Renders selected lab items based strictly on active global selections."""
    selected_items = [x for x in all_items if x.get("id") in selected_ids]
    
    if not selected_items:
        return ft.ListView(controls=[ft.Text("No items selected yet.", size=16)], padding=15, expand=True)
        
    return ft.ListView(
        controls=[
            ft.ListTile(
                title=ft.Text(item.get("name")),
                subtitle=ft.Text(f"ID Ref: {item.get('id')}")
            ) for item in selected_items
        ],
        expand=True,
        padding=15
    )


# =====================================================================
# MAIN RUNTIME VIEWPORT ROUTER
# =====================================================================

def main(page: ft.Page):
    page.title = "AoN Alchemical Archivist"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    state = AppState()

    # -----------------------------------------------------------------
    # RE-RENDER REACTION TRIGGER
    # -----------------------------------------------------------------
    def render():
        """
        The central declarative core loop. Instead of manually editing DOM tree lists,
        it evaluates state mutations and completely overwrites layout structures.
        """
        # Guard clause to ensure boundaries stay logically sound
        if state.min_level > state.max_level:
            state.max_level = state.min_level
            max_level_filter.value = str(state.min_level)

        # Re-fetch structural lists from the pure state
        filtered_dataset = state.get_filtered_items()
        
        # Declaratively assign the entire main body view contents based on current route
        if page.route == "/catalog":
            main_layout_wrapper.controls = [
                header_bar,
                CatalogListView(filtered_dataset, state.selected_ids, on_checkbox_toggle),
                bottom_navigation_bar
            ]
        elif page.route == "/selection":
            # Grabbing all entries for our bench reference lookup mapper
            all_db_records = db.filter_items() 
            main_layout_wrapper.controls = [
                ft.AppBar(title=ft.Text("My Active Laboratory Bench"), bgcolor=ft.Colors.SURFACE_CONTAINER),
                BenchListView(state.selected_ids, all_db_records),
                bottom_navigation_bar
            ]
        
        page.update()

    # -----------------------------------------------------------------
    # STATE MUTATION EVENT HANDLERS
    # -----------------------------------------------------------------
    def on_checkbox_toggle(e):
        print(e)
        item_id = e.control.data
        print(item_id)
        if e.control.value:
            state.selected_ids.add(item_id)
        else:
            state.selected_ids.discard(item_id)
        render()

    def on_filter_ui_change(e):
        print(e)
        state.search_name = name_filter.value
        state.min_level = int(min_level_filter.value)
        state.max_level = int(max_level_filter.value)
        state.sort_by = sort_dropdown.value
        render()

    def on_navigation_change(e):
        print(e)
        page.route = "/catalog" if e.control.selected_index == 0 else "/selection"
        render()

    # -----------------------------------------------------------------
    # PERSISTENT DECLARED FILTERS & CONTROLS
    # -----------------------------------------------------------------
    name_filter = ft.TextField(
        label="Search Name", expand=True, prefix_icon=ft.Icons.SEARCH, on_change=on_filter_ui_change
    )
    
    level_choices = [ft.dropdown.Option(str(i)) for i in range(21)]
    min_level_filter = ft.Dropdown(label="Min Lvl", width=95, options=level_choices, value="0", on_select=on_filter_ui_change)
    max_level_filter = ft.Dropdown(label="Max Lvl", width=95, options=level_choices, value="20", on_select=on_filter_ui_change)
    
    sort_dropdown = ft.Dropdown(
        label="Sort By", width=140, value="name_asc", on_select=on_filter_ui_change,
        options=[
            ft.dropdown.Option("name_asc", "Name (A-Z)"),
            ft.dropdown.Option("name_desc", "Name (Z-A)"),
            ft.dropdown.Option("level_asc", "Level (Asc)"),
            ft.dropdown.Option("level_desc", "Level (Desc)"),
        ]
    )

    header_bar = ft.Container(
        content=ft.Row(controls=[name_filter, min_level_filter, max_level_filter, sort_dropdown], spacing=8),
        padding=12, 
    )

    bottom_navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.SEARCH, label="Catalog"),
            ft.NavigationBarDestination(icon=ft.Icons.SCIENCE, label="My Bench"),
        ],
        on_change=on_navigation_change
    )

    # The single layout shell that gets modified via state maps
    main_layout_wrapper = ft.Column(expand=True)
    
    page.add(main_layout_wrapper)
    
    # Initialize views on boot
    page.route = "/catalog"
    render()

ft.run(main)