import 'dart:ffi';
import 'aon_database.dart';
import 'filters.dart';
import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';

class ArchivistMainScreen extends StatefulWidget {
  const ArchivistMainScreen({super.key, required this.title});
  final String title;

  @override
  State<ArchivistMainScreen> createState() => _ArchivistMainScreenState();
}

class _ArchivistMainScreenState extends State<ArchivistMainScreen> {
  final DatabaseService _dbService = DatabaseService();

  List<Map<String, dynamic>> _queriedCatalogItems = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
  }

  Future<void> _refreshLocalItems() async {
    final items = await _dbService.getLocalItems();
    setState(() {
      _queriedCatalogItems = items;
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

    if (itemHits.isNotEmpty & traitHits.isNotEmpty) {
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
      isOuterItem: true,
      traits: criteria.selectedTraits.isEmpty ? null : traitTranslation,
      // keywords: criteria.selectedKeywords
      //summary:,
    );
    setState(() {
      _queriedCatalogItems = items;
      print("found ${items.length} hits");
    });
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Row(
          children: [
            FilterPanel(onFilterChanged: _handleFilterChange),
            Expanded(child: _buildCatalog()),
          ],
        ),
      ),
      bottomNavigationBar: Container(
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
      ),
    );
  }

  void showModal(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (BuildContext context) => AlertDialog(
        content: const Text('Example Dialog'),
        actions: <TextButton>[
          TextButton(
            onPressed: () {
              Navigator.pop(context);
            },
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildCatalog() {
    final colorScheme = Theme.of(context).colorScheme;
    if (_queriedCatalogItems.isEmpty) {
      return Center(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text(
            'No items found.',
            style: TextStyle(color: colorScheme.onSurfaceVariant),
          ),
        ),
      );
    }

    return Padding(
      padding: EdgeInsets.all(8),
      child: ListView.builder(
        itemCount: _queriedCatalogItems.length,
        itemBuilder: (context, index) {
          final item = _queriedCatalogItems[index];
          return _buildItem(item);
        },
      ),
    );
  }

  Widget _buildItem(Map<String, dynamic> item) {
    final colorScheme = Theme.of(context).colorScheme;

    final bool isRemaster =
        item['remaster_id'] == null || item['remaster_id'].toString().isEmpty;
    final List<dynamic> subentries = item['children'] ?? [];
    final List<String> descriptions = parseMarkdown(item) ?? [''];
    return Container(
      margin: const EdgeInsets.only(bottom: 8.0),
      decoration: BoxDecoration(
        color: colorScheme.onPrimaryFixedVariant,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colorScheme.inversePrimary, width: 1),
      ),
      child: ExpansionTile(
        shape: const Border(),
        collapsedShape: const Border(),
        tilePadding: const EdgeInsets.symmetric(
          horizontal: 12.0,
          vertical: 4.0,
        ),
        childrenPadding: const EdgeInsets.only(
          left: 12.0,
          right: 12.0,
          bottom: 12.0,
        ),

        title: Text(
          "${item['name'] ?? 'Unknown'}   Level ${item['level'] ?? '?'}  ${isRemaster ? 'Remaster' : 'Legacy'}",
          style: TextStyle(fontSize: 16, color: colorScheme.onSurface),
        ),

        children: [
          if (descriptions[0].toString().isNotEmpty)
             MarkdownBody(
                selectable: true,
                data: descriptions[0].toString(),
                onTapLink: (String text, String? href, String title) {
                  if (href != null) {
                    //launchUrl(Uri.parse(href));
                    print("link clik!");
                  }
                },
                styleSheet: MarkdownStyleSheet(
                  code: const TextStyle(
                    fontFamily: 'PF2e Icons',
                    fontSize: 25.0,
                  ),
                ),
              ),

          if (subentries.isNotEmpty) ...[
            const SizedBox(height: 12),
            Divider(color: colorScheme.inversePrimary),
            const SizedBox(height: 8),

            ...subentries.asMap().entries.map((entry) {
                final int subIndex = entry.key;
                final Map<String, dynamic> subItem = entry.value as Map<String, dynamic>;
                final int descIndex = subIndex + 1;
                
                final String? subDesc = descIndex < descriptions.length 
                    ? descriptions[descIndex] 
                    : null;

                return _buildSubentry(subItem, subDesc);
              }),
          ],
        ],
      ),
    );
  }

  Widget _buildSubentry(Map<String, dynamic> subItem,String? description) {
    final colorScheme = Theme.of(context).colorScheme;
    return Column(
      children:[
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: colorScheme.onPrimary,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: colorScheme.onPrimaryFixed, width: 1),
          ),
          padding: const EdgeInsets.symmetric(horizontal:8.0,vertical: 4.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "${subItem['name'] ?? 'Unknown'}   Level ${subItem['level'] ?? '?'}",
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: colorScheme.primary,
                ),
              ),

              if (description != null && description.isNotEmpty)
                  MarkdownBody(
                    selectable: true,
                    data: description,
                    onTapLink: (String text, String? href, String title) {
                      if (href != null) {
                        //launchUrl(Uri.parse(href));
                        print("link clik!");
                      }
                    },
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
      ]
    );
  }

  String formatActions(Match matchObj) {
    final actionType = matchObj.group(1)?.trim() ?? '';
    switch (actionType) {
      case 'Single Action':
        return '`a` ';
      case 'Two Actions':
        return '`d` ';
      case 'Three Actions':
        return '`d` ';
      case 'Free Action':
        return '`.` ';
      case 'Reaction':
        return '`r` ';
      default:
        return '';
    }
  }

  List<String>? parseMarkdown(Map<String, dynamic> item) {
    final String descriptions = item['markdown']?.toString() ?? '';

    final blockRegex = RegExp(
      r'<title.*?<\/column>.*?.(?:\s*?---\s*)?(.*?)(?=<c|<t|$)',
      dotAll: true,
    );
    final linkRegex = RegExp(r'\[(.*?)]\((/.*?)\)');
    final actionsRegex = RegExp(
      r'<actions.*?"(.*?)".+?>(?: Interact)?(?:[; ]+)?',
    );

    List<String> parsedDescriptions = [];

    for (final match in blockRegex.allMatches(descriptions)) {
      String text = match.group(1)?.trim() ?? '';

      text = text.replaceAllMapped(linkRegex, (Match m) {
        final textContent = m.group(1);
        final urlPath = m.group(2);
        return '[$textContent](https://2e.aonprd.com/$urlPath)';
      });
      parsedDescriptions.add(text);
    }
     parsedDescriptions = parsedDescriptions.map((text) {
       String modifiedText = text.replaceAllMapped(actionsRegex, formatActions);
       //modifiedText = modifiedText.replaceAll('<br />', '\n');
       return modifiedText;
     }).toList();
    return parsedDescriptions;
  }
}
