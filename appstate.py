import flet as ft
from typing import Dict, List, Any, Set
from aon_database import *
from dataclasses import dataclass, field
import json
import uuid
import re

AppContext: ft.ContextProvider[AppState | None] = ft.create_context(None)

FILE_PATH = "formula_books.json"

def open_save():
    with open(FILE_PATH, 'a+') as save_file:
        save_file.seek(0)
        content = save_file.read()
        
        if not content:
            book = FormulaBook()
            data = {book.id:book}
            content = json.dumps(data,cls=FormulaBook.Encoder, indent=4)

        data = json.loads(content)
        return data

def write_save(formula_book,data): 
    data[formula_book.id] = formula_book.asDict()
   
    with open(FILE_PATH, "w") as save:
        json.dump(data, save,cls=FormulaBook.Encoder, indent=4)


@ft.observable
@dataclass
class FormulaBook:
    id: int = str(uuid.uuid4())
    name: str = "Empty Formula Book"
    level: str = 1
    formulae: list[str] = field(default_factory=list)
    free_selection: dict[list] = field(default_factory=dict)
    

    def mark_free(self, key, itemId: str):
        if not itemId in self.formulae:
            self.formulae.append(itemId)
            self.formulae = list(self.formulae)
        
        if not key in self.free_selection:
            self.free_selection[key] = []

        if key == "AC" or key == 1:
            if len(self.free_selection[key]) < 4:
                self.free_selection[key].append(itemId)
        else:
            if len(self.free_selection[key]) < 2:
                self.free_selection[key].append(itemId)

        self.free_selection = dict(self.free_selection) 

    def get_free(self):
        return [item for sublist in self.free_selection.values() for item in sublist]

    def remove_free(self, key, order):
        if key in self.free_selection and len(self.free_selection[key]) > order:
            self.free_selection[key].pop(order)
            
            self.free_selection = dict(self.free_selection)

    def update(self, data, id): 
        self.id = id
        self.name = data.get('name')
        self.level = data.get('level')
        self.formulae = data.get('formulae')
        self.free_selection = data.get('free_selection')
    
    def set_name(self, name: str):
        self.name = name
    
    def set_level(self, level: int):
        self.level = level

    def add(self, id: str):
        if not id in self.formulae:
            self.formulae.append(id)
            self.formulae = list(self.formulae) 

    def switchItem(self, id: str):
        if not id in self.formulae:
            self.formulae.append(id)
        else:
            self.remove(id)
            
            
        self.formulae = list(self.formulae) 

    def remove(self, id: str):
        for key, itemList in self.free_selection.items():
            if id in itemList:
                self.free_selection[key].remove(id)
        if id in self.formulae:
            self.formulae.remove(id)

        self.free_selection = dict(self.free_selection)
        self.formulae = list(self.formulae)

    def asDict(self):
        return  {
            'name': self.name,
            'level': self.level,
            'formulae': self.formulae,
            'free_selection': self.free_selection
        }

    class Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            if isinstance(obj,FormulaBook):
                return {
                        'name':obj.name,
                        'level': obj.level,
                        'formulae': obj.formulae,
                        'free_selection': obj.free_selection
                    }
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return super().default(obj)


@ft.observable
@dataclass
class SearchOptions:
    known_only: bool = False
    catalog_page: int = 1
    min_level: int = 0 
    max_level: int = 20
    sort_asc: bool = True
    sort: str = "level"
    #permited_level: set[int] = field(default_factory=set) # Unused
    name: str = ""
    traits: dict[bool] = field(default_factory=dict)

    
    def check_known(self):
        self.catalog_page = 1
        self.known_only = not self.known_only

    def check_sort(self):
        self.sort_asc = not self.sort_asc

    def set_name(self,name):
        self.name=name
        self.catalog_page = 1

    def set_catalog_page(self,catalog_page):
        self.catalog_page=catalog_page

    def add_trait(self,trait:str):
        self.catalog_page = 1
        if not trait in self.traits:
            self.traits[trait] = True

    def negate(self,trait:str):
        if trait in self.traits.keys():
            self.traits[trait] = not self.traits[trait] 

    def remove_trait(self,trait:str):
        self.catalog_page = 1
        self.traits.pop(trait,None)
    
    def set_levels(self,low:int, high:int):
        self.catalog_page = 1
        self.max_level = high
        self.min_level = low

    
db = AlchemicalDatabase("alchemical_items.db")
@dataclass
class AppState:
    current_formula_book:FormulaBook = field(default_factory=FormulaBook)
    search_options: SearchOptions = field(default_factory=SearchOptions)
    db: AlchemicalDatabase = AlchemicalDatabase("alchemical_items.db")
    trait_descriptions: dict = field(default_factory=lambda: {trait: db.get_trait_description(trait) for trait in  db.get_all_traits() } )
    save_data:dict = field(default_factory=dict)
    

    
