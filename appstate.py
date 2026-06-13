import flet as ft
from typing import Dict, List, Any, Set
from aon_database import *
from dataclasses import dataclass, field


AppContext: ft.ContextProvider[AppState | None] = ft.create_context(None)

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
    catalog_page: int = 0
    min_level: int = 0
    max_level: int = 20
    name: str = ""
    traits: list[str] = field(default_factory=list)

    
    def set_name(self,name):
        self.name=name

    def set_page(self,catalog_page):
        print(f"{catalog_page}")
        self.catalog_page=catalog_page
        print(f"{self.catalog_page}")

    def add_trait(self,trait:str):
        if not trait in self.traits:
            self.traits.append(trait)


    def remove_trait(self,trait:str):
        self.traits.remove(trait)
    
    def set_levels(self,low:int, high:int):
        self.max_level = high
        self.min_level = low

    
db = AlchemicalDatabase("alchemical_items.db")
@ft.observable
@dataclass
class AppState:
    current_formula_book:FormulaBook
    search_options: SearchOptions = field(default_factory=SearchOptions)
    db: AlchemicalDatabase = AlchemicalDatabase("alchemical_items.db")
    trait_descriptions: dict = field(default_factory=lambda: {trait: db.get_trait_description(trait) for trait in  db.get_all_traits() } )
    

    
