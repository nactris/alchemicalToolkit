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
    is_loading, set_is_loading = ft.use_state(False)

    async def reload_database():
        set_is_loading(True)
        set_cloud_icon(ft.Icons.HOURGLASS_BOTTOM_ROUNDED)
        try:
            await download_database(app.db)
        finally:
            app.update_db()
            set_cloud_icon(ft.Icons.CLOUD_DOWNLOAD)
            set_is_loading(False)


    def setup_appbar():
        page = ft.context.page
        page.bottom_appbar = ft.BottomAppBar(
            bgcolor=ft.Colors.ON_SECONDARY,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=cloud_icon, 
                        icon_color=ft.Colors.ON_SURFACE,
                        on_click=reload_database,
                        disabled=is_loading  
                    ),
                ]
            ),
        )
        page.update() 


    if is_loading:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.SURFACE), 
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.ProgressRing(width=50, height=50, stroke_width=4),
                    ft.Text("Downloading & Updating Database...", size=16, weight=ft.FontWeight.W_500),
                    ft.Text("This might take a moment depending on your connection.", size=12, color=ft.Colors.SECONDARY)
                ]
            )
        )


    ft.use_effect(setup_appbar, [cloud_icon, is_loading])
    return AppContext(app,catalog.AlchemicalCatalogPage)


async def main(page: ft.Page):
    page.window.min_width = 1100
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