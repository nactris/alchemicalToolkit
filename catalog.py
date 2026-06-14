import flet as ft
from appstate import AppState,AppContext
import aon_database as aon
import re


################################################################################################################################
#//////////////////////////////////////////// TRAITS ///////////////////////////////////////////////////////////////////////////
################################################################################################################################



@ft.component
def traitPlate(text: str, tooltip:str, on_delete)-> ft.Control:
    return ft.Container(
                ft.Button(
                    content = text,
                    on_click=on_delete,  # Fires the parent deletion logic
                    tooltip=tooltip,  
                    style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=0),
                    side=ft.BorderSide(width=2, color=ft.Colors.ON_PRIMARY)
                    ) 

                )
    )

@ft.component 
def traitContainer():

    search_options = ft.use_context(AppContext).search_options
    db =  ft.use_context(AppContext).db

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


################################################################################################################################
#/////////////////////////////////////////// SEARCH ////////////////////////////////////////////////////////////////////////////
################################################################################################################################

@ft.component 
def searchHeader(search_options: SearchOptions):

    entries  = ft.Row(controls=[
        nameSearch(search_options),
        traitSearch(search_options)

    ])
    total = ft.Column(
        controls =[
                levelSlider(search_options),
                entries,
                traitContainer()
        ]
    )
    return total


@ft.component
def nameSearch(search_options: SearchOptions):

    def handle_name_search_update(e):
        search_options.set_name(e.control.value)

    return ft.TextField(
        label="Item name",value=search_options.name, expand=True, prefix_icon=ft.Icons.SEARCH, on_submit=handle_name_search_update
    )


@ft.component
def levelSlider(search_options: SearchOptions):

    def handle_level_change(e: ft.Event[ft.RangeSlider]): 
        search_options.set_levels(e.control.start_value,e.control.end_value)

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
def traitSearch(search_options: SearchOptions)-> ft.Control:

    db = ft.use_context(AppContext).db
    trait_list = ft.use_context(AppContext).trait_descriptions
    trait_field, set_trait_field = ft.use_state("")

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


################################################################################################################################
#//////////////////////////////////////////// CATALOG LIST  ////////////////////////////////////////////////////////////////////
################################################################################################################################



@ft.component
def itemCard(item: Dict[str, Any]) -> ft.Control:
    db = ft.use_context(AppContext).db
    trait_descriptions = ft.use_context(AppContext).trait_descriptions
    expanded, expand = ft.use_state(False)

    def on_card_press(e):
        with open("filename.txt", 'w') as f:
            f.write(item.get('markdown'))
        expand(not expanded)

       

    trait_list  = ft. Row(
        spacing = 5,
        controls = [
            ft.Card(
                bgcolor = ft.Colors.ON_SECONDARY_FIXED,
                variant =ft.CardVariant.FILLED,
                shape = ft.RoundedRectangleBorder(radius=2),
                margin=0,
                elevation = 3,
                content=ft.Container(
                    border=ft.Border.all(0, ft.Colors.ON_SECONDARY_FIXED),
                    tooltip = trait_descriptions.get(trait), 
                    content=ft.Text(trait,size=13),       
                    padding = ft.Padding(left=3,right=3,bottom=1,top=1),             
                ),
            )
            for trait in item.get('trait')
        ],
    )
    price = aon.formula_price(item.get("level", ""))
   
    def format_actions(text):
        match text.group(1).strip():
            case "Single Action":
                return '`a` '
            case "Two Actions":
                return '`d` '
            case "Three Actions":
                return '`d` '
            case "Free Action":
                return '`.` '
            case "Reaction":
                return '`r` '
            

    def find_descriptions(text):
        matches = [re.sub(r'\[(.*?)]\((\/.*?)\)', lambda t: f"[{t.group(1)}](https://2e.aonprd.com/{t.group(2)})", m.group(1).strip()) for m in re.finditer(r'<title.*?<\/column>.*?.(?:\s*?---\s*)?(.*?)(?=<c|<t|$)', text,flags=re.DOTALL)]
        matches = [re.sub(r'<actions.*?"(.*?)".+?>(?: Interact)?(?:[; ]+)?',  format_actions, m) for m in matches]
        matches = [re.sub(r'<br \/>', r'\n', m) for m in matches]
        return matches
    description_text = find_descriptions(item.get('markdown'))

    

    @ft.component
    def childDescription(child_num,child):
        return ft.Row(
            expand =True,
            controls=[
                ft.Card(
                    bgcolor = ft.Colors.ON_SECONDARY_FIXED,
                    variant =ft.CardVariant.FILLED,
                    expand=True,
                    elevation = 3,
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                            ft.Text(f'{child.get('name')} Level {child.get('level')}', weight=ft.FontWeight.BOLD),
                            *([ft.Text(description_text[child_num+1])] if description_text[child_num+1] else [])
                            ],
                            expand=True
                        ),
                        padding =12,
                    )
                )
            ])

    
    
    async def handle_link_click(e):
        if e.data:
            await ft.context.page.launch_url(e.data)

    


    children = item.get('item_child_id')
    if children:
        children = [db.filter_items(id = child, hide_excluded=False, is_outer_item=False,remaster_only=False)[0] for child in children]
    description_card = ft.Row(
        controls=ft.Column(
            expand=True,
            spacing = 0,
            controls = [
                ft.Container(
                    content=ft.Markdown(
                        description_text[0],
                        selectable=True,
                        on_tap_link =handle_link_click,
                        md_style_sheet=ft.MarkdownStyleSheet(
                            code_text_style=ft.TextStyle(
                                font_family="PF2e Icons",
                                size = 25,
                            )
                        )
                    ),
                padding =12,
                )

            ] + ([
                childDescription(child_num,child)
                for child_num,child in enumerate(children)
            ] if children else []),
        )
    )
        
    title_panel = ft.Container(
        on_click=on_card_press,
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(controls=[
                            ft.Text(f"{item.get('name')}", weight=ft.FontWeight.BOLD, size=16),
                        ]),
                        trait_list,
                        ft.Text(
                            f"Level {item.get('level')} | {item.get('item_subcategory', 'Item')}"
                        )
                    ],
                    expand=True,
                    spacing =5
                ),
                ft.Text(f"{price[1]}", italic=True)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ), 
        padding=12
    )



    return ft.Column(
        controls=[
            ft.Card(
                bgcolor = ft.Colors.ON_SECONDARY,
                content=ft.Column(
                spacing=2,
                    controls=[
                        title_panel,
                        *([description_card] if expanded else [])
                    ]
                )
            )
        ]
    )

@ft.component
def catalogPageButtons(selected, pages, handle_func) ->  ft.Control:
    return ft.Container(
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=2,
                    height=30,
                    controls=[

                        ft.Button(
                            content = f"{number+1}",
                            on_click=lambda e,num=number: handle_func(e,num),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                color=ft.Colors.ON_SURFACE,
                                bgcolor=(ft.Colors.ON_SECONDARY if not selected == number else ft.Colors.ON_TERTIARY)
                            )
                        ) 
                        for number in pages],
                ),
                alignment=ft.Alignment.CENTER
            )


@ft.component
def catalogList(search_options: SearchOptions):
    db = ft.use_context(AppContext).db

    items = db.filter_items(
       name= search_options.name if len(search_options.name) else None,
       traits= {"and":search_options.traits} if len(search_options.traits) else None,
       max_level = search_options.max_level,
       min_level = search_options.min_level)
    items_per_page=25
    some_pages = 2
    max_page = int(len(items)/items_per_page)
    low_bound =  min(max(1,max_page-(some_pages*2+1)),max(1, search_options.catalog_page-some_pages))
    high_bound = max(min(max_page,some_pages*2+1),min(max_page,search_options.catalog_page+some_pages))+1
    nearby_pages = list(range(low_bound,high_bound))

    if not 0 in nearby_pages: 
        nearby_pages = [0] + nearby_pages
    if not max_page in nearby_pages:
        nearby_pages.append(max_page)

    if not items:
        return ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Text("No items match your criteria.", size=16), 
                    padding=20, 
                    alignment=ft.Alignment.CENTER
                )
            ],
           # expand=True,

        )
    def handle_load_more_click(e,new_page):
        search_options.set_page(new_page)

    item_list = [catalogPageButtons(search_options.catalog_page,nearby_pages,handle_load_more_click)] +\
    [itemCard(item) for item in \
    items[items_per_page*search_options.catalog_page:\
    items_per_page*(search_options.catalog_page+1)]]

    item_list.append(catalogPageButtons(search_options.catalog_page,nearby_pages,handle_load_more_click))




    return ft.ListView(
        controls=item_list,
        expand=True,
        spacing=5,
        padding=10
    )

################################################################################################################################
#//////////////////////////////////////////// CATALOG //////////////////////////////////////////////////////////////////////////
################################################################################################################################

@ft.component
def AlchemicalCatalogPage():
    search_options = ft.use_context(AppContext).search_options
    return ft.Container(
        padding =10,
        expand=True,
        content= ft.Column( controls =[
            searchHeader(search_options),
            ft.Divider(),
            catalogList(search_options),
        ], expand=True),
    )