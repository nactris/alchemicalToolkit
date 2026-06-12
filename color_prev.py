import flet as ft

def main(page: ft.Page):
    page.title = "Material Color Roles"
    page.padding = 20

    color_roles = sorted([
        "ERROR",
        "ERROR_CONTAINER",
        "INVERSE_PRIMARY",
        "INVERSE_SURFACE",
        "ON_ERROR",
        "ON_ERROR_CONTAINER",
        "ON_INVERSE_SURFACE",
        "ON_PRIMARY",
        "ON_PRIMARY_CONTAINER",
        "ON_PRIMARY_FIXED",
        "ON_PRIMARY_FIXED_VARIANT",
        "ON_SECONDARY",
        "ON_SECONDARY_CONTAINER",
        "ON_SECONDARY_FIXED",
        "ON_SECONDARY_FIXED_VARIANT",
        "ON_SURFACE",
        "ON_SURFACE_VARIANT",
        "ON_TERTIARY",
        "ON_TERTIARY_CONTAINER",
        "ON_TERTIARY_FIXED",
        "ON_TERTIARY_FIXED_VARIANT",
        "OUTLINE",
        "OUTLINE_VARIANT",
        "PRIMARY",
        "PRIMARY_CONTAINER",
        "PRIMARY_FIXED",
        "PRIMARY_FIXED_DIM",
        "SCRIM",
        "SECONDARY",
        "SECONDARY_CONTAINER",
        "SECONDARY_FIXED",
        "SECONDARY_FIXED_DIM",
        "SHADOW",
        "SURFACE",
        "SURFACE_BRIGHT",
        "SURFACE_CONTAINER",
        "SURFACE_CONTAINER_HIGH",
        "SURFACE_CONTAINER_HIGHEST",
        "SURFACE_CONTAINER_LOW",
        "SURFACE_CONTAINER_LOWEST",
        "SURFACE_DIM",
        "SURFACE_TINT",
        "TERTIARY",
        "TERTIARY_CONTAINER",
        "TERTIARY_FIXED",
        "TERTIARY_FIXED_DIM",
        "TRANSPARENT"
    ])

    grid = ft.GridView(
        runs_count=4,
        max_extent=200,
        child_aspect_ratio=2.0,
        spacing=10,
        run_spacing=10,
    )

    for role in color_roles:
        color_value = getattr(ft.Colors, role.upper())
        
        grid.controls.append(
            ft.Container(
                content=ft.Text(role.upper(), size=10, weight="bold"),
                bgcolor=color_value,
                padding=10,
                border_radius=5,
                border=ft.Border.all(1, ft.Colors.BLACK)
            )
        )

    page.add(grid)

ft.app(target=main)