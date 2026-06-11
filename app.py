import flet as ft
from aon_database import *
from appstate import *

################################################################
#/////////////////////////// TRAITS ////////////////////////////
################################################################
@ft.component
def traitPlate(text: str, tooltip:str, on_delete)-> ft.Control:
    return ft.Container(
                ft.Button(
                    content = text,
                    on_click=on_delete,  # Fires the parent deletion logic
                    tooltip=tooltip,  
                    style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=0),
                    side=ft.BorderSide(width=2, color=ft.Colors.BLUE_ACCENT)
                    ) 

                )
    )

@ft.component 
def traitContainer(search_options:SearchOptions,trait_descriptions):
    def handle_trait_plate_click(trait: str):
        search_options.remove_trait(trait)
    
   
    container=ft.Row(
        wrap=True,          
        spacing=10,           
        run_spacing=10,
        alignment=ft.MainAxisAlignment.START,
        controls = [
            traitPlate(trait, trait_descriptions[trait],lambda e,t=trait: handle_trait_plate_click(t) )
            for trait in search_options.traits
        ]
    )
    return container

@ft.component
def traitSearch(search_options:SearchOptions,trait_list,db:AlchemicalDatabase)-> ft.Control:
    trait_field, set_trait_field = ft.use_state("")

    #traits_autofill = db.get_all_traits()
    '''["Acid","Additive","Adjustment","Air","Alchemical","Auditory","Aura","Bomb","Cold","Consumable","Contact",
    "Contract","Darkness","Disease","Divine","Drug","Earth","Electricity","Elixir","Emotion","Enchantment","Evil",
    "Expandable","Fear","Fire","Force","Healing","Illusion","Incapacitation","Ingested","Inhaled","Injury","Light",
    "Linguistic","Lozenge","Magical","Mental","Morph","Mutagen","Mythic","Necromancy","Negative","Nonlethal","Oil",
    "Olfactory","Plant","Poison","Polymorph","Positive","Precious","Processed","Rare","Sleep","Sonic","Splash",
    "Uncommon","Unique","Virulent","Visual","Vitality","Void","Water"]'''
    
    def handle_change(e: ft.Event[ft.AutoComplete]):
        pass

    def handle_select(e: ft.AutoCompleteSelectEvent):
        search_options.add_trait(e.selection.value)
        print(search_options.traits)
        set_trait_field("")
       

    content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.AutoComplete(
                            value="",
                            width=150,
                            on_change=handle_change,
                            on_select=handle_select,
                            suggestions=[
                                ft.AutoCompleteSuggestion(key=value, value= value)
                                for value in (set(trait_list) - set(search_options.traits))
                            ],
                        ),
                        border=ft.Border.all(1), # Surrounding box outline border
                        border_radius=4,                         # Sharp, crisp corners
                        padding=ft.Padding.only(left=15, right=15, bottom=5), # Comfortably positions the flat line out of view
                        alignment=ft.Alignment.CENTER,
                        height=48,
                        clip_behavior = ft.ClipBehavior.NONE
                    )
                ]
            )

    return content

################################################################
#/////////////////////////// ITEMS ////////////////////////////
################################################################

@ft.component
def itemCard(item: Dict[str, Any],trait_descriptions) -> ft.Control:
    def on_card_press(e):
        print(f"the item is {item.get('name')} with id {item.get('id')}")
        print(f"        item has rmid: {item.get('remaster_id')} and lgid {item.get('legacy_id')}")
    

    trait_list  = ft. Row(
        controls = [
            ft.Container(
                content = ft.Text(
                        trait,
                    ),
                    border=ft.Border.all(2, ft.Colors.BLUE_ACCENT),
                    padding = ft.Padding(left=3,right=3,bottom=1,top=1),
                    border_radius = 0,
                    tooltip= trait_descriptions[trait],  
            ) 
            for trait in item.get('trait')
        ],
        spacing =5
    )
    price = formula_price(item.get("level", ""))
    price_coin = ' gp' if price >= 1 else ' sp'
    price = price if price >= 1 else int(price*10)
    return ft.Card(
        content=ft.Container(
            on_click = on_card_press,
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row(controls =[
                                ft.Text(f"{item.get("name")}", weight=ft.FontWeight.BOLD, size=16),
                            ]),
                            trait_list,
                            ft.Text(
                                f"Level {item.get('level')} | {item.get('item_subcategory', 'Item')}"
                            ),
                        ],
                        expand=True
                    ),
                    ft.Text(f"{price}{price_coin}", italic=True)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=12


        )
    )

@ft.component
def catalogList(search_options:SearchOptions,trait_descriptions,db:AlchemicalDatabase):
    items = db.filter_items(
       name= search_options.name if len(search_options.name) else None,
       traits= {"and":search_options.traits} if len(search_options.traits) else None,
       max_level = search_options.max_level,
       min_level = search_options.min_level)
    print(f"There is {len(items)} hits")
    limit, set_limit = ft.use_state(50)

    if not items:
        return ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Text("No items match your criteria.", size=16), 
                    padding=20, 
                    alignment=ft.Alignment.CENTER
                )
            ],
            expand=True,

        )
    item_list = [itemCard(item,trait_descriptions) for item in items[:limit]]
    if len(items) > limit:
        def handle_load_more_click(e):
            set_limit(limit+50)
            
            
        item_list.append(
            ft.Container(
                content=ft.Button(
                    content="Load More",
                    on_click=handle_load_more_click,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.BLUE
                    )
                ),
                padding=ft.Padding.symmetric(vertical=20),
                alignment=ft.Alignment.CENTER
            )
        )




    return ft.ListView(
        controls=item_list,
        expand=True,
        spacing=5,
        padding=10
    )


################################################################
#/////////////////////////// SEARCH ////////////////////////////
################################################################

@ft.component 
def searchHeader(search_options:SearchOptions, trait_descriptions,db:AlchemicalDatabase):
    entries  = ft.Row(controls=[
        nameSearch(search_options),
        traitSearch(search_options,trait_descriptions.keys(),db)

    ])
    total = ft.Column(
        controls =[
                levelSlider(search_options),
                entries,
                traitContainer(search_options,trait_descriptions)
        ]
    )
    return total

@ft.component
def nameSearch(search_options:SearchOptions):
    def handle_name_search_update(e):
        search_options.set_name(e.control.value)
        print(e.control.value)

    return ft.TextField(
        label="Item name",value=search_options.name, expand=True, prefix_icon=ft.Icons.SEARCH, on_submit=handle_name_search_update
    )


@ft.component
def levelSlider(search_options:SearchOptions):

    def handle_level_change(e: ft.Event[ft.RangeSlider]): 
        search_options.set_levels(e.control.start_value,e.control.end_value)

        print(f"{e.control.start_value} - {e.control.end_value}")
        print(f"{search_options.min_level} - {search_options.max_level}")


    return ft.Column(
            controls=[
                ft.Container(height=20),
                ft.RangeSlider(
                    divisions=20,
                    min=0,
                    max=20,
                    start_value=search_options.min_level,
                    end_value=search_options.max_level,
                    on_change_end=handle_level_change,
                    label="Level {value}",
                )
            ]
        )



@ft.component
def menuBar():
    bottom_appbar = ft.BottomAppBar(
        bgcolor=ft.Colors.BLUE,
        shape=ft.CircularRectangleNotchShape(),
        content=ft.Row(
            controls=[
                ft.IconButton(icon=ft.Icons.CLOUD_DOWNLOAD, icon_color=ft.Colors.WHITE),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.WHITE),
                ft.IconButton(icon=ft.Icons.FAVORITE, icon_color=ft.Colors.WHITE),
            ]
        ),
    )
    return bottom_appbar


@ft.component
def CatalogView(app: AppState) -> ft.Control:
    
    #download_database(database)
    return ft.Column( controls =[
        searchHeader(app.search_options,app.trait_descriptions,app.db),
        catalogList(app.search_options,app.trait_descriptions,app.db),
    ])


import instant_testing as it
@ft.component
def SettingsView(app:AppState):
    return it.AdvancedCraftingConfig()


@ft.component
def AppView() -> ft.Control:

    empty_book = FormulaBook(name="Formula Book")
    app, _ = ft.use_state(
       AppState(current_formula_book=empty_book)
    )

    async def reload_database():
        print("reloading database")
        await download_database(app.db)

    ft.context.page.bottom_appbar = ft.BottomAppBar(
        bgcolor=ft.Colors.BLUE,
        shape=ft.CircularRectangleNotchShape(),
        content=ft.Row(
            controls=[
                ft.IconButton(icon= ft.Icons.CLOUD_DOWNLOAD, icon_color=ft.Colors.WHITE,on_click=reload_database),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.SEARCH, icon_color=ft.Colors.WHITE, on_click=lambda : ft.context.page.navigate("/catalog")),
                ft.IconButton(icon=ft.Icons.BOOK, icon_color=ft.Colors.WHITE,  on_click=lambda: ft.context.page.navigate("/formulas")),
                ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=ft.Colors.WHITE,  on_click=lambda: ft.context.page.navigate("/settings")),
            ]
        ),
    )

    return ft.Router(
        [
            ft.Route(path="catalog", component=lambda: CatalogView(app)),
            ft.Route(path="settings", component=lambda: SettingsView(app)),
        ],
        manage_views=True
    )


async def main(page: ft.Page):
    page.title = "AoN Alchemical Archivist"
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.SHOPPING_CART_OUTLINED,
        shape=ft.CircleBorder(),
    )
    page.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_DOCKED

    


    page.render(AppView)



ft.run(main)