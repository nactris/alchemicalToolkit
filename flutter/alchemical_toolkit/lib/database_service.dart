import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

class DatabaseService {
  static Database? _db;
  Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await _initDatabase();
    return _db!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'aon_items.db');
    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE items (
            id TEXT PRIMARY KEY,
            name TEXT,
            level SMALLINT,
            subcategory TEXT,
            primary_source TEXT,
            markdown TEXT,
            text TEXT,
            usage TEXT,
            source TEXT,
            price TEXT, 
            actions SMALLINT,
            bulk TEXT,
            rarity TEXT,
            remaster_id TEXT,
            legacy_id TEXT,
            url TEXT,
            excluded BOOL
          )
        ''');

        await db.execute('''
          CREATE TABLE traits (
            id TEXT ,
            trait TEXT,
            FOREIGN KEY (id) REFERENCES items (id) ON DELETE CASCADE
            PRIMARY KEY (id,trait)
            )
        ''');

        await db.execute('''
          CREATE TABLE trait_info (
            name TEXT PRIMARY KEY,
            markdown TEXT,
            text TEXT,
            url TEXT
          )
        ''');

        await db.execute('''
          CREATE TABLE children (
            parent_id TEXT,
            child_id TEXT,
            PRIMARY KEY (parent_id,child_id)
          )
        ''');

        await db.execute('''
            CREATE TABLE keywords (
            id TEXT ,
            keyword TEXT,
            FOREIGN KEY (id) REFERENCES items (id) ON DELETE CASCADE
            PRIMARY KEY (id,keyword)
           )
        ''');
      },
    );
  }
  // Formula price
  //[0.5, 1, 2, 3, 5, 8, 13, 18, 25, 35, 50, 70, 100, 150, 225, 325, 500, 750, 1200, 2000, 3500]

  Future<List<String>> getAllTraits() async {
    final db = await database;
    final List<Map<String, dynamic>> results = await db.query(
      'trait_info',
      distinct: true,
      columns: ['name'],
    );
    //print("fetched ${results.length} traits");
    return results.map((row) => row['name'].toString()).toList();
  }

  Future<bool> hasItems() async {
    final db = await database;
    final ans = await db.rawQuery('SELECT EXISTS(SELECT 1 FROM items);');
    return Sqflite.firstIntValue(ans) == 1;
  }

  Future<List<Map<String, dynamic>>> fetchAlchemicalItems() async {
    final url = Uri.parse('https://elasticsearch.aonprd.com/aon/_search');

    final payload = {
      "query": {
        "bool": {
          "filter": [
            {
              "query_string": {
                "default_operator": "AND",
                "minimum_should_match": 0,
                "query":
                    "category:equipment item_category:\"Alchemical Items\"",
              },
            },
          ],
        },
      },
      "size": 10000,
    };

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json', 'Accept': '*/*'},
        body: jsonEncode(payload),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List hits = data['hits']['hits'] ?? [];
        return hits.cast<Map<String, dynamic>>();
      } else {
        //print('AoN item search failed with status: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      //print('Network error fetching AoN item data: $e');
      return [];
    }
  }

  Future<List<Map<String, dynamic>>> fetchTraitInfo() async {
    final url = Uri.parse('https://elasticsearch.aonprd.com/aon/_search');

    final payload = {
      "query": {
        "bool": {
          "filter": [
            {
              "query_string": {
                "default_operator": "AND",
                "minimum_should_match": 0,
                "query": "category:trait",
              },
            },
          ],
        },
      },
      "size": 10000,
    };

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json', 'Accept': '*/*'},
        body: jsonEncode(payload),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List hits = data['hits']['hits'] ?? [];
        return hits.cast<Map<String, dynamic>>();
      } else {
       // print('AoN trait search failed with status: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      //print('Network error fetching AoN trait data: $e');
      return [];
    }
  }

  Future<void> populate(
    List<Map<String, dynamic>> itemHits,
    List<Map<String, dynamic>> traitHits,
  ) async {
    final db = await database;
    final Set<String> uniqueTraitsEncountered = {};

    await db.transaction((txn) async {
      for (var hit in itemHits) {
        final source = hit['_source'] ?? {};
        final itemId = source['id'] ?? hit['id'] ?? 'invalid-00';

        await txn.insert('items', {
          'id': source['id'] ?? 'invalidId',
          'name': source['name'] ?? 'invalidName',
          'level': source['level'] ?? 0,
          'subcategory': source['item_subcategory'] ?? 'invalid',
          'primary_source': source['primary_source'] ?? 'invalid',
          'markdown': source['markdown'] ?? '',
          'text': source['text'] ?? '',
          'source': source['primary_source_raw'] ?? '',
          'rarity': source['rarity'] ?? 'common',
          'remaster_id': source['remaster_id']?[0] ?? '',
          'legacy_id': source['legacy_id']?[0] ?? '',
          'url': source['url'] ?? '',
          'price': source['price_raw'] ?? '',
          'usage': source['usage'] ?? '',
          'bulk': source['bulk_raw'] ?? '',
          'excluded': source['exclude_from_search'] ? 1 : 0,
          'actions': actionsNumberToFont(source['actions_number'] ?? 9),
        }, conflictAlgorithm: ConflictAlgorithm.replace);

        final List<dynamic> traits = source['trait'] ?? [];
        for (var trait in traits) {
          await txn.insert('traits', {
            'id': itemId,
            'trait': trait.toString(),
          }, conflictAlgorithm: ConflictAlgorithm.replace);
          uniqueTraitsEncountered.add(trait.toString());
        }

        final List<dynamic> keywords = extractKeywords(source['text'] ?? "");
        for (var key in keywords) {
          await txn.insert('keywords', {
            'id': itemId,
            'keyword': key.toString(),
          }, conflictAlgorithm: ConflictAlgorithm.replace);
        }

        final List<dynamic> children = source['item_child_id'] ?? [];
        for (var child in children) {
          await txn.insert('children', {
            'parent_id': itemId,
            'child_id': child.toString(),
          }, conflictAlgorithm: ConflictAlgorithm.replace);
        }
      }
      for (var trait in uniqueTraitsEncountered) {
        final query = trait.toLowerCase();
        final matches = traitHits
            .map((item) => item['_source'])
            .where((item) => (item['name']).toLowerCase() == query)
            .toList();

        final traitData = matches.firstWhere(
          (item) =>
              !item.containsKey('remaster_id') || item['remaster_id'] == null,
          orElse: () => matches.first,
        );

        await txn.insert('trait_info', {
          'name': traitData['name'],
          'markdown': traitData['markdown'],
          'text': traitData['text'],
          'url': traitData['url'],
        }, conflictAlgorithm: ConflictAlgorithm.replace);
      }
    });
  }

  List<String> extractKeywords(String description) {
    List<String> keywords =
        const [
              "Counteract",
              "Blinded",
              "Concealed",
              "Dazzled",
              "Deafened",
              "Invisible",
              "Doomed",
              "Dying",
              "Unconscious",
              "Wounded",
              "Clumsy",
              "Drained",
              "Enfeebled",
              "Stupefied",
            ]
            .where(
              (word) => description.toLowerCase().contains(word.toLowerCase()),
            )
            .toList();
    return keywords;
  }

  Future<List<Map<String, dynamic>>> getLocalItems() async {
    final db = await database;
    return await db.query('items');
  }

  Future<List<Map<String, dynamic>>> getChildren({required String id}) async {
    final db = await database;

    final ans = await db.query(
      'items',
      columns: ['id', 'name', 'level'],
      where: 'id IN (SELECT child_id FROM children WHERE parent_id = ?)',
      whereArgs: [id],
    );

    return ans;
  }

  Future<List<String>> getTraits({required String id}) async {
    final db = await database;

    final ans = await db.query(
      'traits',
      columns: ['trait'],
      where: 'id = ?',
      whereArgs: [id],
    );
    return ans.map((item) => item['trait'].toString()).toList();
  }

  Future<List<Map<String, dynamic>>> searchItems({
    String? name,
    String? id,
    String? subcategory,
    int? minLevel,
    int? maxLevel,
    String? summary,
    bool? legacy,
    bool hideExcluded = false,
    bool? isOuterItem,
    Map<String, List<String>>? traits,
    List<String>? keywords,
  }) async {
    final db = await database;
    List<String> whereClauses = [];
    List<dynamic> whereArgs = [];

    if (name != null && name.isNotEmpty) {
      whereClauses.add('name LIKE ?');
      whereArgs.add('%$name%');
    }

    if (id != null && id.isNotEmpty) {
      whereClauses.add('id = ?');
      whereArgs.add(id);
    }

    if (subcategory != null && subcategory.isNotEmpty) {
      whereClauses.add('subcategory LIKE ?');
      whereArgs.add(subcategory);
    }

    if (minLevel != null) {
      whereClauses.add('level >= ?');
      whereArgs.add(minLevel);
    }

    if (maxLevel != null) {
      whereClauses.add('level <= ?');
      whereArgs.add(maxLevel);
    }

    if (summary != null && summary.isNotEmpty) {
      whereClauses.add('text LIKE ?');
      whereArgs.add('%$summary%');
    }

    if (legacy != null) {
      if (legacy) {
        whereClauses.add("(legacy_id IS NULL OR legacy_id = '')");
      } else {
        whereClauses.add("(remaster_id IS NULL OR remaster_id = '')");
      }
    }

    if (hideExcluded) {
      whereClauses.add('excluded = 0');
    }

    if (isOuterItem != null) {
      if (isOuterItem) {
        whereClauses.add(
          'NOT EXISTS (SELECT 1 FROM children WHERE children.child_id = items.id)',
        );
      } else {
        whereClauses.add(
          'EXISTS (SELECT 1 FROM children WHERE children.child_id = items.id)',
        );
      }
    }

    if (keywords != null && keywords.isNotEmpty) {
      final placeholders = List.filled(keywords.length, '?').join(',');
      whereClauses.add('''
        id IN (
          SELECT id FROM keywords 
          WHERE LOWER(keyword) IN ($placeholders)
        )
      ''');
      whereArgs.addAll(keywords.map((t) => t.toLowerCase()));
    }

    if (traits != null && traits.isNotEmpty) {
      if (traits.containsKey('include') && traits['include']!.isNotEmpty) {
        final includeTraits = traits['include']!;
        final placeholders = List.filled(includeTraits.length, '?').join(',');
        whereClauses.add('''
          id IN (
            SELECT id FROM traits 
            WHERE LOWER(trait) IN ($placeholders)
          )
        ''');
        whereArgs.addAll(includeTraits.map((t) => t.toLowerCase()));
      }

      if (traits.containsKey('exclude') && traits['exclude']!.isNotEmpty) {
        final excludeTraits = traits['exclude']!;
        final placeholders = List.filled(excludeTraits.length, '?').join(',');
        whereClauses.add('''
          id NOT IN (
            SELECT id FROM traits 
            WHERE LOWER(trait) IN ($placeholders)
          )
        ''');
        whereArgs.addAll(excludeTraits.map((t) => t.toLowerCase()));
      }
    }

    String? finalWhere = whereClauses.isNotEmpty
        ? whereClauses.join(' AND ')
        : null;

    final ans = await db.query(
      'items',
      where: finalWhere,
      whereArgs: whereArgs.isNotEmpty ? whereArgs : null,
    );

    final resultsWithChildren = await Future.wait(
      ans.map((entry) async {
        final mutableEntry = Map<String, dynamic>.from(entry);
        mutableEntry['children'] = await getChildren(
          id: mutableEntry['id'].toString(),
        );
        mutableEntry['traits'] = await getTraits(
          id: mutableEntry['id'].toString(),
        );
        return mutableEntry;
      }),
    );

    return resultsWithChildren;
  }

  bool isUniform(String parentName, String childName) {
    final pName = parentName.trim().toLowerCase();
    final cName = childName.trim().toLowerCase();

    if (cName == pName) {
      return true;
    }

    final uniformKeywords = [
      'minor',
      'lesser',
      'moderate',
      'greater',
      'major',
      'supreme',
      'true',
      'standard',
      'type i',
      'type ii',
      'type iii',
      'type iv',
      'type v',
      'type 1',
      'type 2',
      'type 3',
      'type 4',
      'type 5',
      'dose',
      'dose or round',
      'round',
      'horn',
      'keg',
      'aged',
      'experimental',
      'refined',
      'pure',
      'power',
    ];

    bool hasKeyword = uniformKeywords.any((keyword) => cName.contains(keyword));
    if (hasKeyword) {
      return true;
    }
    return false;
  }

}

int? actionsNumberToFont(int anum) {
  switch (anum) {
    // who the hell labeled this shi
    // like omg cant you do it normaly xD
    case 6: // aaa
      return 3;
    case 4: //aa
      return 2;
    case 2: //a
      return 1;
    case 1: //r
      return 5;
    case 0: //f
      return 4;
    default:
      return null;
  }
}
