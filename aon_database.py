import json
import sqlite3
from typing import Dict, List, Any, Optional
from elasticsearch import Elasticsearch
import asyncio

class AlchemicalDatabase:
    def __init__(self, db_name: str = "alchemical_items.db"):
        self.db_name = db_name
        self._create_item_table()
        self._create_trait_table()
    
    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  
        return conn

    def _create_item_table(self):
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

    def _create_trait_table(self):

        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS traits (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    full_raw_data TEXT NOT NULL
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_name ON traits(name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_id ON traits(id)')

    def save_trait(self, trait_json: Dict[str, Any]):
        name = trait_json.get("name")
        id = trait_json.get("id")
        description = trait_json.get("text")
        full_raw_data = json.dumps(trait_json)

        if not name:
            return  

        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO traits (id, name, description, full_raw_data)
                VALUES (?, ?, ?, ?)
               ''', (id, name, description, full_raw_data))

    def filter_items(self, 
                     name: Optional[str] = None, 
                     id: Optional[str] = None,
                     subcategory: Optional[str] = None, 
                     min_level: Optional[int] = None,  
                     max_level: Optional[int] = None,  
                     skill: Optional[str] = None, 
                     summary: Optional[str] = None, 
                     legacy_only = False,
                     remaster_only = True,
                     hide_excluded = True,
                     is_outer_item = True,
                     traits: Optional[Dict[str, List[str]]] = None) -> List[Dict[str, Any]]:

        query = "SELECT DISTINCT full_raw_data FROM alchemical_items WHERE 1=1"
        # where 1=1 is an always filter, all the next additions to query can start with and safely
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if id:
            query += " AND id LIKE ?"
            params.append(f"%{id}%")

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
        
        if legacy_only:
            query += """ AND json_type(full_raw_data, '$.legacy_id') IS NULL"""

        if remaster_only:
            query += """ AND json_type(full_raw_data, '$.remaster_id') IS NULL"""

        if hide_excluded:
            query += """ AND (
                json_type(full_raw_data, '$.exclude_from_search') IS NOT NULL 
                AND json_extract(full_raw_data, '$.exclude_from_search') = 0
            )"""

        if is_outer_item:
            query += """ AND (
            json_type(full_raw_data, '$.item_parent_id') IS NULL
            )"""
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
    

    def get_trait_description(self, trait: str):
        query = """
           SELECT description FROM traits WHERE LOWER(name) = LOWER(?)
            ORDER BY CASE 
            WHEN json_type(full_raw_data, '$.legacy_id') IS NOT NULL THEN 0 
            ELSE 1 END ASC LIMIT 1; """

        with self._get_connection() as conn:
            cursor = conn.execute(query,[trait])
            return cursor.fetchone()[0]


    def filter_traits(self, 
                     name: Optional[str] = None, 
                     legacy_only = False,
                     remaster_only = True):

        query = "SELECT DISTINCT full_raw_data FROM traits WHERE 1=1"
        params = []

        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")

        if legacy_only:
            query += """ AND json_type(full_raw_data, '$.legacy_id') IS NULL"""

        if remaster_only:
            query += """ AND json_type(full_raw_data, '$.remaster_id') IS NULL"""

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [json.loads(row[0]) for row in cursor.fetchall()]
   
    
    def get_all_traits(self) -> List[str]:
        query = """
            SELECT json_group_array(DISTINCT json_each.value) 
            FROM alchemical_items, 
                 json_each(alchemical_items.full_raw_data, '$.trait')
        """
        with self._get_connection() as conn:
            cursor = conn.execute(query)
            row = cursor.fetchone()
            traits_list = json.loads(row[0]) if row[0] else []
            return sorted(traits_list)


async def download_database(db_instance: AlchemicalDatabase, save_json=False):
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
        await asyncio.sleep(0.01)

        if save_json:
            with open(f"pf2e_alchemical_items.json", 'w', encoding='utf-8') as f:
                json.dump(raw_items, f, indent=4, ensure_ascii=False)

        print(f"Successfully retrieved {len(raw_items)} records from online index.")

        print("Populating local database...")
        for item in raw_items:
            db_instance.save_item(item)
            await asyncio.sleep(0)

        print("Downloading trait descriptions...")
        await download_traits(db_instance)
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


async def download_traits(db_instance: AlchemicalDatabase, save_json=True):
    local_traits = db_instance.get_all_traits()
    
    if not local_traits:
        print("No items found in local database. Sync your alchemical items first!")
        return

    print(f"Found {len(local_traits)} unique traits in your database items.")

    es = Elasticsearch(
        "https://elasticsearch.aonprd.com/",
        headers={"Accept": "application/json", "Content-Type": "application/json"}
    )

    print("Querying AoN for matching trait metadata updates...")
    try:
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"category": "trait"}},
                        {"terms": {"name": [t.lower() for t in local_traits]}}
                    ]
                }
            },
            "size": 1000
        }

        response = es.search(index="aon", body=query_body)
        hits = response.get('hits', {}).get('hits', [])
        raw_items = [hit['_source'] for hit in hits]
        await asyncio.sleep(0.01)

        if save_json:
            with open(f"pf2e_traits.json", 'w', encoding='utf-8') as f:
                json.dump(raw_items, f, indent=4, ensure_ascii=False)

        print(f"Downloaded {len(hits)} matching trait records from online index.")
        await asyncio.sleep(0.01)

  
        for trait in raw_items:
            db_instance.save_trait(trait)
        print(f"Success! Saved {len(raw_items)} trait definitions.")

    except Exception as e:
        print(f"Failed to fetch trait definitions: {e}")
