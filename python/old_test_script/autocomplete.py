import flet as ft

traits_autofill = ["Acid","Additive","Adjustment","Air","Alchemical","Auditory","Aura","Bomb","Cold","Consumable","Contact",
    "Contract","Darkness","Disease","Divine","Drug","Earth","Electricity","Elixir","Emotion","Enchantment","Evil",
    "Expandable","Fear","Fire","Force","Healing","Illusion","Incapacitation","Ingested","Inhaled","Injury","Light",
    "Linguistic","Lozenge","Magical","Mental","Morph","Mutagen","Mythic","Necromancy","Negative","Nonlethal","Oil",
    "Olfactory","Plant","Poison","Polymorph","Positive","Precious","Processed","Rare","Sleep","Sonic","Splash",
    "Uncommon","Unique","Virulent","Visual","Vitality","Void","Water"]


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def handle_change(e: ft.Event[ft.AutoComplete]):
        info.value = f"Current input 👀: {e.data!r} \n"

    def handle_select(e: ft.AutoCompleteSelectEvent):
        info.value = (
            f"Current input 👀: {e.control.value!r} \n"
            f"Your selection: {e.selection.value}"
        )

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    ft.AutoComplete(
                        value="One",
                        width=150,
                        on_change=handle_change,
                        on_select=handle_select,
                        suggestions=[
                            ft.AutoCompleteSuggestion(key=value, value=value)
                            for value in traits_autofill
                        ],
                    ),
                    # below shall be deleted
                    info := ft.Text(
                        "Enter a number (in words or digits) to get suggestions."
                    ),
                ]
            )
        ),
    )


if __name__ == "__main__":
    ft.run(main)