import json
from elasticsearch import Elasticsearch

def download_aon_data(category = 'alchemical',output_file=None):
    es = Elasticsearch(
        "https://elasticsearch.aonprd.com/",
        headers={"Accept": "application/json", "Content-Type": "application/json"}
    )
    
    if output_file is None:
        output_file = f"pf2e_{category}s.json"

    print(f"Connecting to Archives of Nethys to fetch {category}s...")

    try:
        # Simplified search call to avoid version-specific body wrappers
        response = es.search(
            index="aon",
            query={
                "match": {
                     "item_category": "Alchemical Items",
                }
            },
            size=10000
        )

        hits = response.get('hits', {}).get('hits', [])
        data = [hit['_source'] for hit in hits]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Success! Downloaded {len(data)} entries to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")




if __name__ == "__main__":
    download_aon_data()