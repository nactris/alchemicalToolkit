import flet as ft

@ft.component
def AdvancedCraftingConfig():
    # 1. State Management
    level, set_level = ft.use_state(1)
    selected_research, set_selected_research = ft.use_state(None)
    player_options_expanded, set_player_options = ft.use_state(False)
    alchemical_crafting_expanded, set_alchemical_crafting = ft.use_state(False)
    formulabook_expanded, set_formula_book = ft.use_state(False)

    # Helper: Create numeric options 1-20 for Dropdowns
    level_options = [ft.dropdown.Option(str(i)) for i in range(1, 21)]

    return ft.Column(
        controls=[
            ft.Text("Base Configuration", weight=ft.FontWeight.BOLD),
           
            ft.ExpansionTile(
                title = "Character Options",
                expanded = player_options_expanded,
                controls=[
                    ft.Text("Research Field"),
                    ft.SegmentedButton(
                    selected_icon=ft.Icon(ft.Icons.CHECK),
                    allow_empty_selection=True,
                    segments=[
                        ft.Segment(value="Toxicologist", label=ft.Text("Toxicologist"),icon=ft.Icon(ft.Icons.LOOKS_4)),
                        ft.Segment(value="Mutagenist", label=ft.Text("Mutagenist"),icon=ft.Icon(ft.Icons.LOOKS_4)),
                        ft.Segment(value="Bomber", label=ft.Text("Bomber"),icon=ft.Icon(ft.Icons.LOOKS_4)),
                        ft.Segment(value="Chirurgeon", label=ft.Text("Chirurgeon"),icon=ft.Icon(ft.Icons.LOOKS_4)),
                    ],
                    selected=[],
                    on_change=lambda e: print(f"selected {e.control.selected}"),
                ),
                ]
            ),

            # --- Alchemical Crafting Section ---
            ft.ExpansionTile(
                title=ft.Text("Alchemical Crafting"),
                expanded = alchemical_crafting_expanded,
                controls=[
                    ft.TextField(label="Crafting Result 1"),
                    ft.TextField(label="Crafting Result 2"),
                    ft.TextField(label="Crafting Result 3"),
                    ft.TextField(label="Crafting Result 4"),
                ]
            ),

        # --- Formula Book Section ---
            ft.ExpansionTile(
                title=ft.Text("Formula Books"),
                expanded = formulabook_expanded,
                controls=[
                    ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Text(f"Free Formula Book: {4 + (max(0, level - 1) * 2)} entries"),
                            ft.Text("Paid Formula Book: 1 entry locked"),
                        ])
                    )
                ]
            )
        ]
    )