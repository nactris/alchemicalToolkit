import flet as ft
from aon_database import *
from appstate import *





@ft.component
def menuBar():
    bottom_appbar = ft.BottomAppBar(
        bgcolor=ft.Colors.BLUE,
        shape=ft.CircularRectangleNotchShape(),
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.CLOUD_DOWNLOAD, icon_color=ft.Colors.WHITE),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.WHITE),
                ft.IconButton(icon=ft.Icons.FAVORITE, icon_color=ft.Colors.WHITE),
            ]
        ),
    )
    return bottom_appbar

import catalog
@ft.component
def CatalogView() -> ft.Control:
    print("-> catalog")
    return catalog.AlchemicalCatalogPage()
    


import settings
@ft.component
def SettingsView():
    print("-> catalog")
    return settings.AdvancedCraftingConfig()


import book
@ft.component
def FormulaView():
    print("-> book ")
    return book.AlchemicalFormulaBookPage()


@ft.component
def AppView() -> ft.Control:

    empty_book = FormulaBook(name="Formula Book")
    app, _ = ft.use_state(
       AppState(current_formula_book=empty_book)
    )
    cloud_icon, set_cloud_icon = ft.use_state(ft.Icons.CLOUD_DOWNLOAD)


    async def reload_database():
        set_cloud_icon(ft.Icons.HOURGLASS_BOTTOM_ROUNDED)
        await download_database(app.db)
        set_cloud_icon(ft.Icons.CLOUD_DOWNLOAD)

    ft.context.page.bottom_appbar = ft.BottomAppBar(
        bgcolor=ft.Colors.ON_SECONDARY,
        shape=ft.CircularRectangleNotchShape(),
        content=ft.Row(
            controls=[
                ft.IconButton(icon= cloud_icon, icon_color=ft.Colors.ON_SURFACE,on_click=reload_database),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.ON_SURFACE, on_click=lambda : ft.context.page.navigate("/catalog")),
                ft.IconButton(icon=ft.Icons.BOOK, icon_color=ft.Colors.ON_SURFACE,  on_click=lambda: ft.context.page.navigate("/formulas")),
                ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=ft.Colors.ON_SURFACE,  on_click=lambda: ft.context.page.navigate("/settings")),
            ]
        ),
    )

    return AppContext( 
            app, 
            lambda: ft.Router([
                ft.Route(path="formulas", component=FormulaView),
                ft.Route(path="catalog", component=CatalogView),
                ft.Route(path="settings", component=SettingsView),
                ],
                manage_views=True
            )   
        )


async def main(page: ft.Page):
    await page.window.center()
    page.window.width = 700
    page.window.height = 1000
    page.title = "AoN Alchemical Archivist"
    page.padding = 0
    page.fonts = {
        "PF2e Icons": "assets/fonts/Pathfinder2eActions.ttf",
    }
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.SHOPPING_CART_OUTLINED,
        shape=ft.CircleBorder(),
    )
    page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

    


    page.render(AppView)


ft.run(main,assets_dir="assets")