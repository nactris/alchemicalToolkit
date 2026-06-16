import flet as ft
from typing import Dict, List, Any, Set
from aon_database import *
from dataclasses import dataclass, field
import json
import uuid

AppContext: ft.ContextProvider[AppState | None] = ft.create_context(None)

@ft.observable
@dataclass
class FormulaBook:
    id: int = str(uuid.uuid4())
    name: str = "Empty Formula Book"
    level: str = 1
    formulas: list[str] = field(default_factory=list)
    #free_selection[list] = field(default_factory=dict)
    # here be settings, alchemical crafting and such

    def update(self, data,id): # TODO optional
        self.id = id
        self.name = data.get('name')
        self.level = data.get('level')
        self.formulas = data.get('formulas')
    
    def set_name(self,name:str):
        self.name = name
    
    def set_level(self,level:int):
        self.level = level

    def add(self,id:str):
        self.formulas.append(id)

    def remove(self,id:str):
        self.formulas.remove(id)

    class Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            if isinstance(obj,FormulaBook):
                return {
                        'name':obj.name,
                        'level': obj.level,
                        'formulas': obj.formulas
                    }
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return super().default(obj)


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
    current_formula_book:FormulaBook = field(default_factory=FormulaBook)
    search_options: SearchOptions = field(default_factory=SearchOptions)
    db: AlchemicalDatabase = AlchemicalDatabase("alchemical_items.db")
    trait_descriptions: dict = field(default_factory=lambda: {trait: db.get_trait_description(trait) for trait in  db.get_all_traits() } )
    

    
