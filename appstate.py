import flet as ft
from typing import Dict, List, Any, Set
from aon_database import *
from dataclasses import dataclass, field
import json
import uuid
import re

AppContext: ft.ContextProvider[AppState | None] = ft.create_context(None)




@ft.observable
@dataclass
class FormulaBook:
    id: int = str(uuid.uuid4())
    name: str = "Empty Formula Book"
    level: str = 1
    formulas: list[str] = field(default_factory=list)
    free_selection: dist[list] = field(default_factory=dict)
    # here be settings, alchemical crafting and such

    def mark_free(self, key,itemId: str ):
        if not itemId in self.formulas:
            self.formulas.append(itemId)
        
        if  not key in self.free_selection :
            self.free_selection[key] = []


        if key == "AC" or key == 1:
            if len(self.free_selection[key]) <= 4:
                self.free_selection[key].append(itemId)
       
        else:
            if len(self.free_selection[key]) <= 2:
                self.free_selection[key].append(itemId)

        # formula book -> 4x 1st level item + 2 items per next level -> 2 + 2*level
        # research field -> 2x item
        # alchemical crafting - 4x item

    def get_free(self):
        return [item for sublist in self.free_selection.values() for item in sublist]

    def remove_free(self,key,order):
        print(self.free_selection[key],order)
        if key in self.free_selection and len(self.free_selection[key]) > order :
            self.free_selection[key].pop(order)

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
        if not id in self.formulas:
            self.formulas.append(id)

    def switchItem(self,id:str):
        if not id in self.formulas:
            self.formulas.append(id)
        else:
            self.formulas.remove(id)

    def remove(self,id:str):
        if id in self.formulas:
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
    catalog_page: int = 1
    min_level: int = 0
    max_level: int = 20
    name: str = ""
    traits: list[str] = field(default_factory=list)

    
    def set_name(self,name):
        self.name=name
        self.catalog_page = 1

    def set_catalog_page(self,catalog_page):
        self.catalog_page=catalog_page

    def add_trait(self,trait:str):
        self.catalog_page = 1
        if not trait in self.traits:
            self.traits.append(trait)


    def remove_trait(self,trait:str):
        self.catalog_page = 1
        self.traits.remove(trait)
    
    def set_levels(self,low:int, high:int):
        self.catalog_page = 1
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
    

    
