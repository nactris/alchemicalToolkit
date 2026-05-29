import flet as ft
from typing import Dict, List, Any, Set
from aon_database import *
from dataclasses import dataclass, field


db = AlchemicalDatabase("alchemical_items.db")

@ft.observable
@dataclass
class FormulaBook:
    name: str
    formuas: list[str] = field(default_factory=list)
    # here be settings, alchemical crafting and such

    def update(self, name: str): #TODO add settings
        self.name = name
    
    def add(self,id:str):
        self.formuas.append(id)

    def remove(self,id:str):
        self.formuas.remove(id)


@ft.observable
@dataclass
class SearchOptions:
    max_level: int = 0
    min_level: int = 20
    name: str = ""
    traits: list[str] = field(default_factory=list)

    def add_trait(self,trait:str):
        if not trait in self.traits:
            self.traits.append(trait)


    def remove_trait(self,trait:str):
        self.traits.remove(trait)
    

@ft.observable
@dataclass
class AppState:
    current_formula_book:FormulaBook
    search_options: SearchOptions = field(default_factory=SearchOptions)



@ft.component
def traitPlate(text: str, on_delete)-> ft.Control:
    description = "some trait description"
    return ft.Container(
                ft.Button(
                    content = text,
                    on_click=on_delete,  # Fires the parent deletion logic
                    tooltip=description,  # Handles displaying the description text on hover
                    style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=0),
                    side=ft.BorderSide(width=2, color=ft.Colors.BLUE_ACCENT)
                    ) 

                )
    )

@ft.component 
def traitContainer(search_options: SearchOptions):
    def handle_trait_plate_click(trait: str):
        search_options.remove_trait(trait)

    container=ft.Row(
        wrap=True,          
        spacing=10,           
        run_spacing=10,
        alignment=ft.MainAxisAlignment.START,
        controls = [
            traitPlate(trait,lambda e,t=trait: handle_trait_plate_click(t) )
            for trait in search_options.traits
        ]
    )
    return container

@ft.component
def searchBar(search_options:SearchOptions) -> ft.Control:
    trait_field, set_trait_field = ft.use_state("")

    traits_autofill = ["Acid","Additive","Adjustment","Air","Alchemical","Auditory","Aura","Bomb","Cold","Consumable","Contact",
    "Contract","Darkness","Disease","Divine","Drug","Earth","Electricity","Elixir","Emotion","Enchantment","Evil",
    "Expandable","Fear","Fire","Force","Healing","Illusion","Incapacitation","Ingested","Inhaled","Injury","Light",
    "Linguistic","Lozenge","Magical","Mental","Morph","Mutagen","Mythic","Necromancy","Negative","Nonlethal","Oil",
    "Olfactory","Plant","Poison","Polymorph","Positive","Precious","Processed","Rare","Sleep","Sonic","Splash",
    "Uncommon","Unique","Virulent","Visual","Vitality","Void","Water"]
    
    def handle_change(e: ft.Event[ft.AutoComplete]):
        pass

    def handle_select(e: ft.AutoCompleteSelectEvent):
        search_options.add_trait(e.selection.value)
        print(search_options.traits)
        set_trait_field("")
       

    content=ft.Row(
                controls=[
                    ft.AutoComplete(
                        value="",
                        #name="Traits",
                        width=150,
                        on_change=handle_change,
                        on_select=handle_select,
                        suggestions=[
                            ft.AutoCompleteSuggestion(key=value, value= value)
                            for value in (set(traits_autofill) - set(search_options.traits))
                        ],
                    )
                   
                ]
            )

    return content




@ft.component
def AppView() -> list[ft.Control]:
    database = AlchemicalDatabase("alchemical_items.db")
   # download_database(database)
    empty_book = FormulaBook(name="Formula Book")
    app, _ = ft.use_state(
       AppState(current_formula_book=empty_book)
    )
    return [
       # list of components as items not fncs
        searchBar(app.search_options),
        traitContainer(app.search_options)
    ]


async def main(page: ft.Page):
    page.render(AppView)



ft.run(main)