import flet as ft
from aon_database import *
from appstate import *
import catalog


@ft.component
def AppView(save_data,book) -> ft.Control:
    app, _ = ft.use_state(
       AppState(current_formula_book=book,save_data=save_data)
    )
    cloud_icon, set_cloud_icon = ft.use_state(ft.Icons.CLOUD_DOWNLOAD)


    async def reload_database():
        set_cloud_icon(ft.Icons.HOURGLASS_BOTTOM_ROUNDED)
        await download_database(app.db)
        set_cloud_icon(ft.Icons.CLOUD_DOWNLOAD)

    ft.context.page.bottom_appbar = ft.BottomAppBar(
        bgcolor=ft.Colors.ON_SECONDARY,
        #shape=ft.CircularRectangleNotchShape(),
        content=ft.Row(
            controls=[
                ft.IconButton(icon= cloud_icon, icon_color=ft.Colors.ON_SURFACE,on_click=reload_database),
                ft.Container(expand=True),
                #ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.ON_SURFACE, on_click=lambda : ft.context.page.navigate("")),
                #ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=ft.Colors.ON_SURFACE,  on_click=lambda: ft.context.page.navigate("/settings")),
            ]
        ),
    )


    
    return AppContext(app,catalog.AlchemicalCatalogPage)


async def main(page: ft.Page):
    page.window.min_width = 1000
    page.window.min_height = 550
    page.window.alignment = ft.Alignment.CENTER
    await page.window.center()
    page.title = "AoN Alchemical Archivist"
    page.padding = 0
    page.fonts = {
        "PF2e Icons": "assets/fonts/Pathfinder2eActions.ttf",
    }

    page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

    
    save_data = open_save()
    empty_book = FormulaBook(name="New Formula Book")
    if save_data:
        bookID =next(iter(save_data))
        empty_book.update(save_data[bookID],bookID)


    page.render(lambda: AppView(save_data,empty_book))


ft.run(main,assets_dir="assets")