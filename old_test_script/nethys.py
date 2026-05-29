import json
import sqlite3
from typing import Dict, List, Any, Optional
from elasticsearch import Elasticsearch


class AlchemicalDatabase:
    def __init__(self, db_name: str = "alchemical_items.db"):
        self.db_name = db_name
        self._create_table()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  
        return conn

    def _create_table(self):
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alchemical_items (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    subcategory TEXT,
                    full_raw_data TEXT NOT NULL
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_search_coords ON alchemical_items(subcategory, level)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_name ON alchemical_items(name)')

    def save_item(self, item_json: Dict[str, Any]):
        item_id = item_json.get("id")
        name = item_json.get("name")
        level = int(item_json.get("level", 0))
        subcategory = item_json.get("item_subcategory")
        full_raw_data = json.dumps(item_json)

        if not item_id or not name:
            return  # skip malformed data

        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO alchemical_items (id, name, level, subcategory, full_raw_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_id, name, level, subcategory, full_raw_data))

    def filter_items(self, 
                     name: Optional[str] = None, 
                     subcategory: Optional[str] = None, 
                     min_level: Optional[int] = None,  
                     max_level: Optional[int] = None,  
                     skill: Optional[str] = None, 
                     summary: Optional[str] = None, 
                     traits: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:

        query = "SELECT DISTINCT full_raw_data FROM alchemical_items WHERE 1=1"
        # where 1=1 is an always filter, all the next additions to query can start with and safely
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")

        if subcategory:
            query += " AND subcategory LIKE ?"
            params.append(subcategory)

        if min_level is not None:
            query += " AND level >= ?"
            params.append(min_level)

        if max_level is not None:
            query += " AND level <= ?"
            params.append(max_level)

        if skill:
            query += """ AND EXISTS (
                SELECT 1 FROM json_each(alchemical_items.full_raw_data, '$.skill_mod') 
                WHERE json_each.key LIKE ?
            )"""
            params.append(skill)

        if summary:
            query += " AND json_extract(full_raw_data, '$.summary') LIKE ?"
            params.append(f"%{summary}%")

        if traits:
            for tag in traits.get("and", []):
                query += """ AND EXISTS (
                    SELECT 1 FROM json_each(alchemical_items.full_raw_data, '$.trait') 
                    WHERE json_each.value LIKE ?
                )"""
                params.append(tag)

            or_tags = traits.get("or", [])
            if or_tags:
                placeholders = ", ".join(["?"] * len(or_tags))
                query += f""" AND EXISTS (
                    SELECT 1 FROM json_each(alchemical_items.full_raw_data, '$.trait') 
                    WHERE json_each.value IN ({placeholders})
                )"""
                params.extend(or_tags)

            for tag in traits.get("not", []):
                query += """ AND NOT EXISTS (
                    SELECT 1 FROM json_each(alchemical_items.full_raw_data, '$.trait') 
                    WHERE json_each.value LIKE ?
                )"""
                params.append(tag)

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [json.loads(row[0]) for row in cursor.fetchall()]
    def get_all_unique_traits(self) -> List[str]:
        """Queries the database and returns a single sorted list of all unique traits."""
        query = """
            SELECT json_group_array(DISTINCT json_each.value) 
            FROM alchemical_items, 
                 json_each(alchemical_items.full_raw_data, '$.trait')
        """
        with self._get_connection() as conn:
            cursor = conn.execute(query)
            row = cursor.fetchone()
            # The result comes back as a JSON string array; parse it back to Python
            traits_list = json.loads(row[0]) if row[0] else []
            return sorted(traits_list)


def download_database(db_instance: AlchemicalDatabase):
    es = Elasticsearch(
        "https://elasticsearch.aonprd.com/",
        headers={"Accept": "application/json", "Content-Type": "application/json"}
    )
    
    print("Connecting to Archives of Nethys Elasticsearch cluster...")
    try:
        response = es.search(
            index="aon",
            query={
                    "bool": {
                        "must": [
                            {"match_phrase": {"item_category": "Alchemical Items"}},
                            {"term": {"category": "equipment"}}
                        ]
                    }
               },
            size=10000
        )
        hits = response.get('hits', {}).get('hits', [])
        raw_items = [hit['_source'] for hit in hits]
        print(f"Successfully retrieved {len(raw_items)} records from online index.")

        if output_file is None:
            output_file = f"pf2e_{category}s.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(raw_items, f, indent=4, ensure_ascii=False)
            
        print("Populating local database...")
        for item in raw_items:
            db_instance.save_item(item)
        print("Database sync complete!\n")

    except Exception as e:
        print(f"Failed to sync data from online database: {e}")

    def formula_price(level:int) -> int:
        if level < 0:
            level = 0
        if level > 20:
            level = 20

        prices = [0.5, 1, 2, 3, 5, 8, 13, 18, 25, 35, 50, 70, 100, 150, 225, 325, 500, 750, 1200, 2000, 3500]   
        return prices[level]



if __name__ == "__main__":
    # Initialize database orchestrator
    db = AlchemicalDatabase("alchemical_items.db")
    
    # Sync online data down to local database
    # download_database(db)

    print("-" * 50)
    print("DEMO 1: Standard Multi-Column Filter & Member Access")
    print("-" * 50)
    
    # Query for Level 0 items categorized specifically as "Drugs"
    drugs = db.filter_items(subcategory="Drugs", max_level=0)
    print(f"Found {len(drugs)} matches.")
    
    for item in drugs[:3]:  # Display up to 3 matches
        # Accessing top-level database filter columns
        print(f"\nItem ID:     {item.get('id')}")
        print(f"Name:        {item.get('name')} (Level {item.get('level')})")
        print(f"Subcategory: {item.get('item_subcategory')}")
        
        # Accessing pristine unindexed archive fields stored inside the JSON blob
        print(f"Price (Raw): {item.get('price_raw')}")
        print(f"Source:      {item.get('primary_source')}")
        print(f"Traits List: {', '.join(item.get('trait', []))}")


    print("\n" + "-" * 50)
    print("DEMO 2: Advanced Logical Trait Matrix Filtering")
    print("-" * 50)
    
    # Search for items that are 'Alchemical' AND 'Consumable', but NOT 'Poison'
    filtered_traits = db.filter_items(
        traits={
            "and": ["Magical"]
            
        }
    )
    print(f"Found {len(filtered_traits)} items matching the specified trait logic matrix.")
    if filtered_traits:
        for i in range(0,len(filtered_traits)):
            print(f"Example Match: {filtered_traits[i].get('name')} | Current Traits: {filtered_traits[i].get('trait')}")


    print("\n" + "-" * 50)
    print("DEMO 3: Keyword Text Summary Scan")
    print("-" * 50)
    
    # Scan long text strings nested deep inside summaries
    military_gear = db.filter_items(summary="alchemist")
    print(f"Found {len(military_gear)} items mentioning 'soldier' inside their text summaries.")
    for item in military_gear:
        print(f"- {item.get('name')}: \"{item.get('summary')[:75]}...\"")

        

    print("\n" + "-" * 50)
    print("DEMO 4: List of all traits")
    print("-" * 50)
    
    traits = db.get_all_unique_traits()
    print(f"Found {len(traits)} traits.")
    print("[")
    for t in traits:
        print(f"\"{t}\",")
    print ("]")
