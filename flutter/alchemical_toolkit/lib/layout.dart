import 'package:alchemical_toolkit/file_service.dart';
import 'package:alchemical_toolkit/theme_color_grid.dart';
import 'database_service.dart';
import 'filter_details.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:uuid/uuid.dart';
import 'book_details.dart';
import 'dart:io';

var uuidGen = Uuid();

class ArchivistMainScreen extends StatefulWidget {
  const ArchivistMainScreen({super.key, required this.title});
  final String title;

  @override
  State<ArchivistMainScreen> createState() => _ArchivistMainScreenState();
}

class FilterCriteria {
  String? name;
  bool knownOnly;
  String sortBy;
  bool ascending;
  Map<String, bool> selectedTraits;
  Set<String> selectedKeywords;
  //String? category
  int minLevel;
  int maxLevel;

  FilterCriteria({
    this.name,
    this.sortBy = 'level',
    this.ascending = true,
    this.knownOnly = false,
    Map<String, bool>? selectedTraits,
    Set<String>? selectedKeywords,
    //this.category = '',
    this.minLevel = 0,
    this.maxLevel = 20,
  }) : selectedTraits = selectedTraits ?? {},
       selectedKeywords = selectedKeywords ?? {};

  void reset() {
    name = null;
    knownOnly = false;
    selectedTraits.clear();
    selectedKeywords.clear();
    minLevel = 0;
    maxLevel = 20;
  }
}

class FormulaBook {
  String name;
  String uuid;
  Map<String, List<String>> free;
  List<String> formulae;
  int level;

  FormulaBook({
    this.level = 1,
    this.name = "Empty Formula Book",
    List<String>? formulae,
    Map<String, List<String>>? free,
  }) : formulae = formulae ?? [],
       free = free ?? {},
       uuid = uuidGen.v1();

  void reset() {
    level = 1;
    name = "Empty Formula Book";
    formulae = [];
    free = {};
    uuid = uuidGen.v1();
  }

  void update(Map<String, dynamic> data) {
    level = data['level'];
    name = data['name'];
    uuid = data['uuid'];
    formulae = List<String>.from(data['formulae']);
    free = (data['free'] as Map<String, dynamic>).map(
      (key, value) => MapEntry(key, List<String>.from(value as List)),
    );
  }

  void setLevel(level) {
    if (level <= 20 && level >= 0) this.level = level;
  }

  void setName(name) {
    this.name = name;
  }

  void change(String id) {
    if (formulae.contains(id)) {
      formulae.remove(id);
    } else {
      formulae.add(id);
    }
  }

  bool isFree(String id) {
    return free.values.any((category) => category.any((item) => item == id));
  }

  bool contains(String id) {
    return formulae.any((item) => item.startsWith(id));
  }

  void setFreeStatus(String category, String id) {
    final maxCount = (category == "Alchemical Crafting") ? 4 : 2;
    final categoryList = free[category];
    if (categoryList == null) free[category] = [];
    if (categoryList != null && categoryList.length < maxCount) {
      if (categoryList.contains(id)) {
        free[category]?.remove(id);
      } else {
        free[category]?.add(id);
      }
    }
  }

  Map<String, dynamic> map() {
    return {
      "name": name,
      "level": level,
      "free": free,
      "formulae": formulae,
      "uuid": uuid,
    };
  }

  void setUuid(String id) {
    uuid = id;
  }
}

class _ArchivistMainScreenState extends State<ArchivistMainScreen> {
  final DatabaseService _dbService = DatabaseService();
  final _fService = FileService();

  List<Map<String, dynamic>> _queriedCatalogItems = [];
  List<String> _traits = [];
  bool _isLoading = false;
  final FilterCriteria _criteria = FilterCriteria();
  FormulaBook _formulaBook = FormulaBook();
  double _totalPrice = 0;

  @override
  void initState() {
    super.initState();

    _refreshLocalItems();
    _updatePrice();
  }

  Future<void> _refreshLocalItems() async {
    _handleFilterChange(_criteria);
    final fetchedTraits = await _dbService.getAllTraits();
    setState(() {
      _traits = fetchedTraits;
    });
  }

  Future<void> _updatePrice() async {
    final List<double> priceTags = [
      0.5,
      1,
      2,
      3,
      5,
      8,
      13,
      18,
      25,
      35,
      50,
      70,
      100,
      150,
      225,
      325,
      500,
      750,
      1200,
      2000,
      3500,
    ];
    final double calcPrice = (await Future.wait(
      _formulaBook.formulae.map((entry) async {
        final item = await _dbService.searchItems(id: entry);
        return (priceTags[item[0]['level']]);
      }),
    )).fold(0.0, (a, b) => a + b);
    setState(() {
      _totalPrice = calcPrice;
    });
  }

  Future<void> _updateDatabase() async {
    setState(() {
      _isLoading = true;
    });

    final itemHits = await _dbService.fetchAlchemicalItems();
    print("Downloaded ${itemHits.length} items from AoN!");
    final traitHits = await _dbService.fetchTraitInfo();
    print("Downloaded ${traitHits.length} items from AoN!");

    if (itemHits.isNotEmpty && traitHits.isNotEmpty) {
      await _dbService.populate(itemHits, traitHits);
      print("Done populating database!");

      await _refreshLocalItems();
    }

    setState(() {
      _isLoading = false;
    });
    print("Update finished!");
  }

  void _handleFilterChange(FilterCriteria criteria) async {
    var traitTranslation = {
      'include': criteria.selectedTraits.entries
          .where((entry) => entry.value)
          .map((entry) => entry.key)
          .toList(),
      'exclude': criteria.selectedTraits.entries
          .where((entry) => !entry.value)
          .map((entry) => entry.key)
          .toList(),
    };
    final items = await _dbService.searchItems(
      name: criteria.name,
      //subcategory: criteria.subcategory,
      minLevel: criteria.minLevel,
      maxLevel: criteria.maxLevel,
      hideExcluded: true,
      legacy: false,
      isOuterItem: true,
      traits: criteria.selectedTraits.isEmpty ? null : traitTranslation,
      // keywords: criteria.selectedKeywords
      //summary:,
    );
    setState(() {
      _queriedCatalogItems = _criteria.knownOnly
          ? items.where((item) => _formulaBook.contains(item["id"])).toList()
          : items;
      if (_criteria.sortBy == "level") {
        _queriedCatalogItems.sort((a, b) {
          final result = a['name'].toLowerCase().compareTo(
            b['name'].toLowerCase(),
          );

          return _criteria.ascending ? result : -result;
        });
      }
      _queriedCatalogItems.sort((a, b) {
        final levelC = a['level'].compareTo(b['level']);
        final result = _criteria.sortBy == "level"
            ? levelC == 0
                  ? a['name'].toLowerCase().compareTo(b['name'].toLowerCase())
                  : levelC
            : a['name'].toLowerCase().compareTo(b['name'].toLowerCase());

        return _criteria.ascending ? result : -result;
      });
      print("found ${items.length} hits");
    });
  }

  void _handleBookChange(FormulaBook formulaBook, bool shouldSave) async {
    if (shouldSave) {
      _fService.saveOrUpdate(
        itemData: formulaBook.map(),
        uuid: formulaBook.uuid,
      );
    }
    setState(() {
      _formulaBook = formulaBook;
    });
    _updatePrice();
  }

  void _handleLinkClick(String text, String? href, String title) {
    if (href != null) {
      //launchUrl(Uri.parse(href));
      print("link clik! $text https://2e.aonprd.com$href ");
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final screenWidth = MediaQuery.of(context).size.width;
    final bool isMobile = screenWidth < 800;
    //return ThemeColorGrid();
    return Scaffold(
      body: Scaffold(
        backgroundColor: Colors.transparent,
        drawerEdgeDragWidth: MediaQuery.of(context).size.width / 3,
        drawer: _buildLeftDrawer(),
        endDrawer: _buildRightDrawer(),
        body: SafeArea(
          child: isMobile
              ? _buildCatalog() // Mobile layout
              : Row(
                  // Desktop Layout
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 300,
                      child: FilterPanel(
                        traits: _traits,
                        criteria: _criteria,
                        onChanged: _handleFilterChange,
                      ),
                    ),
                    Expanded(child: _buildCatalog()),
                    SizedBox(
                      width: 300,
                      child: FormulaBookDetails(
                        formulaBook: _formulaBook,
                        onChanged: _handleBookChange,
                      ),
                    ),
                  ],
                ),
        ),
      ),
      bottomNavigationBar: _buildBottomBar(),
    );
  }

  Widget? _buildLeftDrawer() {
    //final screenWidth = MediaQuery.of(context).size.width;
    final bool isMobile =
        Platform.isAndroid || Platform.isIOS; //screenWidth < 800;
    //final colorScheme = Theme.of(context).colorScheme;
    return isMobile
        ? Drawer(
            backgroundColor: Colors.transparent,
            shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(8.0)),
            ),
            child: SafeArea(
              child: FilterPanel(
                traits: _traits,
                criteria: _criteria,
                onChanged: _handleFilterChange,
              ),
            ),
          )
        : null;
  }

  Widget? _buildRightDrawer() {
    //final screenWidth = MediaQuery.of(context).size.width;
    final bool isMobile =
        Platform.isAndroid || Platform.isIOS; //screenWidth < 800;
    //final colorScheme = Theme.of(context).colorScheme;
    return isMobile
        ? Drawer(
            backgroundColor: Colors.transparent,
            shape: const RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(8.0)),
            ),
            child: SafeArea(
              child: FormulaBookDetails(
                formulaBook: _formulaBook,
                onChanged: _handleBookChange,
              ),
            ),
          )
        : null;
  }

  Widget _buildCatalog() {
    final colorScheme = Theme.of(context).colorScheme;
    return Column(
      children: [
        _buildTopBar(),
        Expanded(
          child: _queriedCatalogItems.isEmpty
              ? Padding(
                  padding: EdgeInsets.all(4.0),
                  child: Text(
                    'No items found.',
                    style: TextStyle(color: colorScheme.onSurfaceVariant),
                  ),
                )
              : Padding(
                  padding: EdgeInsets.only(left: 8.0, right: 8.0, top: 4.0),
                  child: ListView.builder(
                    itemCount: _queriedCatalogItems.length,
                    itemBuilder: (context, index) {
                      final item = _queriedCatalogItems[index];
                      return _buildItem(item);
                    },
                  ),
                ),
        ),
      ],
    );
  }

  Widget _buildItem(Map<String, dynamic> item) {
    final colorScheme = Theme.of(context).colorScheme;

    final List<dynamic> subentries = item['children'] ?? [];
    final List<String> descriptions = parseMarkdown(item) ?? [''];
    final pureCollection = subentries.every(
      (subItem) => !_dbService.isUniform(item['name'], subItem['name']),
    );
    final pureUniform = subentries.every(
      (subItem) => _dbService.isUniform(item['name'], subItem['name']),
    );
    final formatedAction = item['actions'] != null
        ? "`${item['actions']}` "
        : '';
    final formatedActivation = findActionType(item['markdown']);
    return Container(
      margin: const EdgeInsets.only(bottom: 8.0),
      decoration: BoxDecoration(
        color: colorScheme.onPrimaryFixedVariant,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colorScheme.inversePrimary, width: 1),
      ),
      child: ExpansionTile(
        showTrailingIcon: false,
        shape: const Border(),
        collapsedShape: const Border(),
        tilePadding: const EdgeInsets.only(
          top: 0,
          bottom: 0.0,
          left: 4.0,
          right: 8.0,
        ),
        childrenPadding: const EdgeInsets.only(
          left: 12.0,
          right: 12.0,
          bottom: 12.0,
        ),

        title: Row(
          children: [
            Padding(
              padding: EdgeInsets.all(0),
              child: IconButton(
                style: IconButton.styleFrom(
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                onPressed: () => {
                  print(item['traits']),
                  if (!pureCollection || subentries.isEmpty)
                    {
                      _formulaBook.change(item["id"]),
                      setState(() {}),
                      _handleBookChange(_formulaBook, true),
                    },
                },
                icon: Icon(
                  !pureUniform && subentries.isNotEmpty
                      ? Icons.bookmarks_outlined
                      : _formulaBook.contains(item['id'])
                      ? _formulaBook.isFree(item['id'])
                            ? Icons.bookmark_add
                            : Icons.bookmark
                      : Icons.bookmark_outline,
                ),
              ),
            ),

            Text(
              "${item['name'] ?? 'Unknown'}",
              style: TextStyle(fontSize: 16, color: colorScheme.onSurface),
            ),

            Spacer(),
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                //  color: colorScheme.onPrimary,
                //  borderRadius: BorderRadius.circular(8),
                //  border: Border.all(color: colorScheme.onPrimaryFixed, width: 2),
              ),
              child: Center(
                child: Text(
                  "${item['level']}",
                  style: TextStyle(fontSize: 18, color: colorScheme.onSurface),
                ),
              ),
            ),
          ],
        ),
        children: [
          const SizedBox(height: 4),
          _buildTraitBar(item),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Source
              if (item['source'] != null &&
                  item['source'].toString().trim().isNotEmpty)
                Align(
                  alignment: AlignmentDirectional.centerStart,
                  child: Text.rich(
                    TextSpan(
                      style: TextStyle(
                        fontSize: 14,
                        color: colorScheme.onSurface,
                      ),
                      children: [
                        const TextSpan(
                          text: "Source ",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        TextSpan(
                          text: "${item['source']}",
                          style: const TextStyle(fontWeight: FontWeight.normal),
                        ),
                      ],
                    ),
                  ),
                ),

              // Usage
              if (item['usage'] != null &&
                  item['usage'].toString().trim().isNotEmpty)
                Align(
                  alignment: AlignmentDirectional.centerStart,
                  child: Text.rich(
                    TextSpan(
                      style: TextStyle(
                        fontSize: 14,
                        color: colorScheme.onSurface,
                      ),
                      children: [
                        const TextSpan(
                          text: "Usage ",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        TextSpan(
                          text: "${item['usage']};",
                          style: const TextStyle(fontWeight: FontWeight.normal),
                        ),
                      ],
                    ),
                  ),
                ),
              //const SizedBox(height: 8),
              if (formatedActivation != null &&
                  formatedActivation.trim().isNotEmpty)
                // Actions / Activate
                Align(
                  alignment: AlignmentDirectional.centerStart,
                  child: MarkdownBody(
                    selectable: true,
                     onTapLink:_handleLinkClick,
                    styleSheet: MarkdownStyleSheet(
                      code: const TextStyle(
                        fontFamily: 'PF2e Icons',
                        fontSize: 25.0,
                      ),
                      p: TextStyle(color: colorScheme.onSurface),
                    ),

                    data: "**Activate** $formatedAction$formatedActivation",
                  ),
                ),
            ],
          ),

          const SizedBox(height: 8),

          if (descriptions[0].toString().isNotEmpty)
            MarkdownBody(
              selectable: true,
              data: descriptions[0].toString(),
              onTapLink:_handleLinkClick,
              styleSheet: MarkdownStyleSheet(
                code: const TextStyle(fontFamily: 'PF2e Icons', fontSize: 25.0),
              ),
            ),

          if (subentries.isNotEmpty) ...[
            const SizedBox(height: 12),
            Divider(color: colorScheme.inversePrimary),
            const SizedBox(height: 8),

            ...subentries.asMap().entries.map((entry) {
              final int subIndex = entry.key;
              final Map<String, dynamic> subItem =
                  entry.value as Map<String, dynamic>;
              final int descIndex = subIndex + 1;

              final String? subDesc = descIndex < descriptions.length
                  ? descriptions[descIndex]
                  : null;

              return _buildSubentry(
                subItem,
                subDesc,
                _dbService.isUniform(item['name'], subItem['name']),
              );
            }),
          ],
        ],
      ),
    );
  }

  Widget _buildTraitBar(Map<String, dynamic> item) {
    final List<dynamic> traits = item['traits'] ?? [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Align(
          alignment: Alignment.centerLeft,
          child: Wrap(
            spacing: 4,
            runSpacing: 8,
            children: traits.map((trait) {
              return _buildTraitPlate(trait);
            }).toList(),
          ),
        ),
        const SizedBox(height: 8),
      ],
    );
  }

  Widget _buildTraitPlate(String trait) {
    final colorScheme = Theme.of(context).colorScheme;
    //TODO remove that?
    final bgColor = trait == 'Uncommon'
        ? Colors.deepOrange
        : trait == 'Rare'
        ? Colors.indigo
        : trait == 'Unique'
        ? Colors.deepPurple
        : colorScheme.onPrimary;
    final frameColor = trait == 'Uncommon'
        ? Colors.deepOrangeAccent
        : trait == 'Rare'
        ? Colors.indigoAccent
        : trait == 'Unique'
        ? Colors.deepPurpleAccent
        : colorScheme.onPrimaryFixed;

    return Container(
      padding: const EdgeInsets.only(left: 4, right: 4, top: 2, bottom: 2),
      decoration: BoxDecoration(
        border: Border.all(color: frameColor, width: 1),
        borderRadius: BorderRadius.circular(6),
        color: bgColor,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          GestureDetector(
            onTap: () {},
            child: Text(
              trait,
              style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSubentry(
    Map<String, dynamic> subItem,
    String? description,
    isUniform,
  ) {
    final colorScheme = Theme.of(context).colorScheme;
    return Column(
      children: [
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: colorScheme.onPrimary,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: colorScheme.onPrimaryFixed, width: 1),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment
                    .start, // Aligns elements to the top when text wraps
                children: [
                  if (!isUniform)
                    IconButton(
                      onPressed: () {
                        print(subItem['id']);
                        _formulaBook.change(subItem["id"]);
                        setState(() {});
                        _handleBookChange(_formulaBook, true);
                        print(_formulaBook.formulae);
                      },
                      icon: Icon(
                        _formulaBook.contains(subItem['id'])
                            ? _formulaBook.isFree(subItem['id'])
                                  ? Icons.bookmark_add
                                  : Icons.bookmark
                            : Icons.bookmark_outline,
                      ),
                      style: IconButton.styleFrom(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                    ),

                  // Name: Expands and wraps
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(
                        top: 8.0,
                      ), // Adjust to align with the icon visually
                      child: Text(
                        "${subItem['name'] ?? 'Unknown'}",
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: colorScheme.primary,
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(width: 8), // Gap between name and level
                  // Level: Does not wrap
                  Padding(
                    padding: const EdgeInsets.only(
                      top: 8.0,
                    ), // Adjust to align with the name
                    child: Text(
                      "Level ${subItem['level'] ?? '?'}",
                      softWrap: false,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: colorScheme.primary,
                      ),
                    ),
                  ),
                ],
              ),
              if (description != null && description.isNotEmpty)
                MarkdownBody(
                  selectable: true,
                  data: description,
                  onTapLink:_handleLinkClick,
                  styleSheet: MarkdownStyleSheet(
                    code: const TextStyle(
                      fontFamily: 'PF2e Icons',
                      fontSize: 25.0,
                    ),
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 8.0),
      ],
    );
  }

  Widget _buildBottomBar() {
    final colorScheme = Theme.of(context).colorScheme;
    return Container(
      height: 68,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: colorScheme.primaryContainer,
        border: Border(
          top: BorderSide(
            //color: Theme.of(context).colorScheme.inversePrimary,
            width: 2,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Left Action
          IconButton(
            onPressed: _updateDatabase,
            icon: _isLoading
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.cloud_download),
          ),

          IconButton(
            icon: Icon(Icons.print, color: colorScheme.onSurface),
            onPressed: () async {
              print(
                await Future.wait([
                  _dbService.getChildren(id: "equipment-1311"),
                ]),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildTopBar() {
    final colorScheme = Theme.of(context).colorScheme;
    final int gp = _totalPrice.floor();
    final int sp = ((_totalPrice - gp) * 10).round();
    final price = (gp > 0 ? "$gp gp" : "") + (sp > 0 ? "$sp sp" : "");

    return Column(
      children: [
        Padding(
          padding: EdgeInsetsGeometry.only(bottom: 4, left: 8, right: 8),
          child: Container(
            width: double.infinity,
            decoration: BoxDecoration(
              color: colorScheme.onSecondaryFixed,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: colorScheme.inversePrimary, width: 2),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
            child: Row(
              children: [
                Text(
                  "${_formulaBook.name} $price",
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: colorScheme.primary,
                  ),
                ),

                Spacer(),
                Text(
                  "Level ${_formulaBook.level} ",
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: colorScheme.primary,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  String formatActions(Match matchObj) {
    final actionType = matchObj.group(1)?.trim() ?? '';
    switch (actionType) {
      case 'Single Action':
        return '`1` ';
      case 'Two Actions':
        return '`2` ';
      case 'Three Actions':
        return '`3` ';
      case 'Free Action':
        return '`4` ';
      case 'Reaction':
        return '`5` ';
      default:
        return '';
    }
  }

  String? findActionType(String markdown) {
    final actionsRegex = RegExp(
      r'<row gap="tiny">\s*<row>\*\*Activate\*\*</row>\s*<actions\b[^>]*/>\s*<row>([^<]+)</row>\s*</row>',
      dotAll: true,
    );
    return actionsRegex.firstMatch(markdown)?.group(1);
  }

  List<String>? parseMarkdown(Map<String, dynamic> item) {
    final String descriptions = item['markdown']?.toString() ?? '';

    final blockRegex = RegExp(
      r'<title.*?<\/column>.*?.(?:\s*?---\s*)?(.*?)(?=<c|<t|$)',
      dotAll: true,
    );
    //final linkRegex = RegExp(r'\[(.*?)]\((/.*?)\)');
    final actionsRegex = RegExp(
      r'<actions.*?"(.*?)".+?>(?: Interact)?(?:[; ]+)?',
    );

    List<String> parsedDescriptions = [];

    for (final match in blockRegex.allMatches(descriptions)) {
      String text = match.group(1)?.trim() ?? '';

      // text = text.replaceAllMapped(linkRegex, (Match m) {
      //   final textContent = m.group(1);
      //   final urlPath = m.group(2);
      //   return '[$textContent](https://2e.aonprd.com/$urlPath)';
      // });
      parsedDescriptions.add(text);
    }
    parsedDescriptions = parsedDescriptions.map((text) {
      String modifiedText = text.replaceAllMapped(actionsRegex, formatActions);
      modifiedText = modifiedText.replaceAll('<br />', '\n');
      return modifiedText;
    }).toList();
    return parsedDescriptions;
  }
}
