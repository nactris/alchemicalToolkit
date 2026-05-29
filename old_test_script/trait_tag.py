import flet as ft

@ft.component
def RemovableTag(text: str, description: str, on_delete):
    """
    A custom declarative tag component.
    
    :param text: The primary text string displayed on the badge.
    :param description: The tooltip text that appears when hovered.
    :param on_delete: Callback function executed when the delete icon is clicked.
    """
    
    def handle_hover(e):
        # Visually shifts the background color slightly on hover to feel clickable
        e.control.bgcolor = ft.colors.SURFACE_CONTAINER_HIGHEST if e.data == "true" else ft.colors.SURFACE_CONTAINER
        e.control.update()

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(text, size=14, weight=ft.FontWeight.W_500),
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    icon_size=14,
                    visual_density=ft.VisualDensity.COMPACT,
                    tooltip="Remove tag",
                    on_click=on_delete  # Fires the parent deletion logic
                )
            ],
            tight=True,
            spacing=4
        ),
        bgcolor=ft.colors.SURFACE_CONTAINER,
        padding=ft.padding.only(left=12, right=4, top=4, bottom=4),
        border_radius=16,
        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT),
        tooltip=description,  # Handles displaying the description text on hover
        on_hover=handle_hover
    )




def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    # 1. OUR STATE DATA MODEL
    # A list of dictionaries representing our active tag data models
    active_tags = [
        {"id": "t1", "label": "Alchemical", "desc": "Item matches the Alchemical crafting matrix."},
        {"id": "t2", "label": "Poison", "desc": "Deals continuous toxic damage attributes."},
        {"id": "t3", "label": "Consumable", "desc": "Item is destroyed completely upon activation use."}
    ]

    # 2. STATE MUTATION CONTROLLER
    def delete_tag_handler(tag_id: str):
        # Find the tag by ID and remove it from our tracking state layout
        nonlocal active_tags
        active_tags = [t for t in active_tags if t["id"] != tag_id]
        render()

    # 3. CENTRAL RENDERING PIPELINE
    def render():
        # Completely maps the tag array state into visual RemovableTag controls
        tag_row.controls = [
            RemovableTag(
                text=tag["label"],
                description=tag["desc"],
                # We use a lambda to pass the exact target ID down to our state engine
                on_delete=lambda e, tid=tag["id"]: delete_tag_handler(tid)
            ) for tag in active_tags
        ]
        page.update()

    # A flexible horizontal wrapping row layout shell to display our components
    tag_row = ft.Row(wrap=True, spacing=10)
    page.add(tag_row)
    
    # Run initial component mount render loop
    render()

if __name__ == "__main__":
    ft.run(main)