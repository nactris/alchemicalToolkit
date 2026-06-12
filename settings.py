import flet as ft

@ft.component
def AdvancedCraftingConfig():
    level, set_level = ft.use_state(1)
    alchemical_crafting_expanded, set_alchemical_crafting = ft.use_state(False)
    formulabook_expanded, set_formula_book = ft.use_state(False)

    def handle_level_change(e: ft.Event[ft.RangeSlider]): 
        set_level(int(e.control.value))
        print(f"set character level: {level}")


    return ft.Column(
        controls=[
            ft.Text("Base Configuration", weight=ft.FontWeight.BOLD),
           
            ft.Row(
                controls=[
                    ft.Text(value=f"Character Level: {level}", size=16, weight=ft.FontWeight.BOLD),
                    ft.Slider(
                        min=1,
                        expand = True,
                        max=20,
                        divisions=19,  
                        value=level,       
                        label="{value}",
                        on_change=handle_level_change
                    )
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