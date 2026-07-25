import 'package:flutter/material.dart';
import 'aon_database.dart';

/// Data model representing current filter criteria
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
    this.ascending = false,
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

class FilterPanel extends StatefulWidget {
  final Function(FilterCriteria criteria) onFilterChanged;
  final List<String> availableKeywords;

  const FilterPanel({
    super.key,
    required this.onFilterChanged,
    this.availableKeywords = const ["Counteract","Blinded", "Concealed", "Dazzled", "Deafened",
     "Invisible", "Doomed", "Dying", "Unconscious", "Wounded", "Clumsy", "Drained", "Enfeebled", "Stupefied"]

  });

  @override
  State<FilterPanel> createState() => _FilterPanelState();
}

class _FilterPanelState extends State<FilterPanel> {
  final DatabaseService _dbService = DatabaseService();
  final TextEditingController _nameController = TextEditingController();
  final FilterCriteria _criteria = FilterCriteria();
  List<String> _traits = [];

  @override
  void initState() {
    super.initState();
    _loadTraits();
  }

  Future<void> _loadTraits() async {
  
    final fetchedTraits = await _dbService.getTraits();
    setState(() {
      _traits = fetchedTraits;
      print(fetchedTraits);
    });
    
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  void _notifyParent() {
    widget.onFilterChanged(_criteria);
  }

  void _clearFilters() {
    setState(() {
      _nameController.clear();
      _criteria.reset();
    });
    _notifyParent();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      width: 280,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colorScheme.onSecondaryFixed,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colorScheme.inversePrimary, width: 2),
      ),
      child: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: .start,
                children: [
                  // 1. Search Name Input
                  _buildSearchInput(),
                  const SizedBox(height: 12),

                  Row(
                    children: [
                      _buildSortOptions(),
                      const SizedBox(width: 8),
                      _buildSortButton(),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // 3. Known Only Toggle
                  _buildKnownOnlyButton(),
                  const SizedBox(height: 8),

                  // 4. Clear All Filters
                  _buildClearButton(),
                  const SizedBox(height: 16),

                  // 5. Traits Selector
                  _buildTraitsSection(),
                  const SizedBox(height: 12),

                  // 6. Keywords Selector
                  _buildKeywordSection(),
                  const SizedBox(height: 16),

                  // 7. Min & Max Level Range
                  Row(
                    children: [
                      Expanded(
                        child: _buildLevelRangeBox(
                          label: 'Min level',
                          currentValue: _criteria.minLevel,
                          onChanged: (val) {
                            if (val != null) {
                              setState(() => _criteria.minLevel = val);
                              _notifyParent();
                            }
                          },
                        ),
                      ),
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 6.0),
                        child: Text('-', style: TextStyle(color: Colors.grey)),
                      ),
                      Expanded(
                        child: _buildLevelRangeBox(
                          label: 'Max level',
                          currentValue: _criteria.maxLevel,
                          onChanged: (val) {
                            if (val != null) {
                              setState(() => _criteria.maxLevel = val);
                              _notifyParent();
                            }
                          },
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchInput() {
    final colorScheme = Theme.of(context).colorScheme;
    return TextField(
      controller: _nameController,
      style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
      onChanged: (val) {
        _criteria.name = val.trim().isEmpty ? null : val.trim();
        _notifyParent();
      },
      decoration: InputDecoration(
        hintText: 'Search Name',
        hintStyle: TextStyle(color: colorScheme.onSurfaceVariant, fontSize: 12),
        prefixIcon: Icon(
          Icons.search,
          size: 16,
          color: colorScheme.onSurfaceVariant,
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 0),
        enabledBorder: OutlineInputBorder(
          borderSide: BorderSide(color: colorScheme.inversePrimary, width: 2),
          borderRadius: BorderRadius.circular(6),
        ),
        focusedBorder: OutlineInputBorder(
          borderSide: BorderSide(color: colorScheme.inversePrimary, width: 2),
          borderRadius: BorderRadius.circular(6),
        ),
      ),
    );
  }

  Widget _buildSortOptions() {
    final colorScheme = Theme.of(context).colorScheme;

    final sortLabels = {'level': 'Sort by Level', 'name': 'Sort by Name'};

    return Expanded(
      child: LayoutBuilder(
        builder: (context, constraints) {
          return PopupMenuButton<String>(
            position: PopupMenuPosition.under,
            color: colorScheme.onSecondaryFixed,
            constraints: BoxConstraints(
              minWidth: constraints.maxWidth,
              maxWidth: constraints.maxWidth,
            ),
            initialValue: _criteria.sortBy,
            onSelected: (String selected) {
              if (selected != _criteria.sortBy) {
                setState(() {
                  _criteria.sortBy = selected;
                });
                _notifyParent();
              }
            },
            itemBuilder: (BuildContext context) {
              return sortLabels.entries.map((entry) {
                return PopupMenuItem<String>(
                  value: entry.key,
                  child: Text(
                    entry.value,
                    style: TextStyle(
                      fontSize: 12,
                      color: colorScheme.onSurface,
                    ),
                  ),
                );
              }).toList();
            },
            child: Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                border: Border.all(color: colorScheme.inversePrimary, width: 2),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Row(
                children: [
                  Text(
                    sortLabels[_criteria.sortBy] ?? 'Level',
                    style: TextStyle(
                      fontSize: 12,
                      color: colorScheme.onSurface,
                    ),
                  ),
                  const Spacer(),
                  Icon(
                    Icons.arrow_drop_down,
                    color: colorScheme.onSurfaceVariant,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSortButton() {
    final colorScheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(2),
      decoration: BoxDecoration(
        border: Border.all(color: colorScheme.inversePrimary, width: 2),
        borderRadius: BorderRadius.circular(6),
      ),

      child: IconButton(
        icon: Icon(
          _criteria.ascending ? Icons.move_down : Icons.move_up,
          size: 24,
          color: colorScheme.onSurfaceVariant,
        ),
        onPressed: () {
          setState(() => _criteria.ascending = !_criteria.ascending);
          _notifyParent();
        },
        style: IconButton.styleFrom(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
      ),
    );
  }

  Widget _buildKnownOnlyButton() {
    final colorScheme = Theme.of(context).colorScheme;
    final bool isSelected = _criteria.knownOnly;
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: () {
          setState(() => _criteria.knownOnly = !_criteria.knownOnly);
          _notifyParent();
        },
        style: OutlinedButton.styleFrom(
          side: BorderSide(
            color: isSelected ? colorScheme.primary : colorScheme.inversePrimary,
            width: 2,
          ),
          backgroundColor: colorScheme.onSecondaryFixed,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6), ),
        ),
        icon: Icon(
          isSelected ? Icons.bookmark : Icons.bookmark_border,
          size: 14,
          color: isSelected
              ? colorScheme.primary
              : colorScheme.onSurfaceVariant,
        ),
        label: Text(
          'Known only',
          style: TextStyle(
            fontSize: 12,
            color: isSelected
                ? colorScheme.primary
                : colorScheme.onSurfaceVariant,
          ),
        ),
      ),
    );
  }

  Widget _buildClearButton() {
    final colorScheme = Theme.of(context).colorScheme;
    return SizedBox(
      width: double.infinity,
      height: 36,
      child: OutlinedButton(
        onPressed: _clearFilters,
        style: OutlinedButton.styleFrom(
          side: BorderSide(color: colorScheme.inversePrimary,width: 2),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
        child: const Text(
          'Clear All Filters',
          style: TextStyle(fontSize: 12, color: Colors.white),
        ),
      ),
    );
  }

  Widget _buildTraitsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTraitSelector(),
        if (_criteria.selectedTraits.isNotEmpty) const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerLeft,
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _criteria.selectedTraits.keys.map((trait) {
              return _buildTraitPlate(trait);
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildTraitSelector() {
    final colorScheme = Theme.of(context).colorScheme;

    final availableTraits = _traits
        .where((trait) => !_criteria.selectedTraits.containsKey(trait))
        .toList();

    return LayoutBuilder(
      builder: (context, constraints) {
        return PopupMenuButton<String>(
          position: PopupMenuPosition.under,

          color: colorScheme.onSecondary,
          constraints: BoxConstraints(
            minWidth: constraints.maxWidth,
            maxWidth: constraints.maxWidth,
          ),
          onSelected: (String selected) {
            setState(() {
              _criteria.selectedTraits[selected] = true;
            });
            _notifyParent();
          },
          itemBuilder: (BuildContext context) {
            return availableTraits.map((trait) {
              return PopupMenuItem<String>(
                value: trait,
                child: Text(
                  trait,
                  style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
                ),
              );
            }).toList();
          },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10,vertical: 10),
            decoration: BoxDecoration(
              border: Border.all(color: colorScheme.inversePrimary, width: 2),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Row(
              children: [
                Icon(Icons.search, size: 16, color: colorScheme.onSurfaceVariant),
                const SizedBox(width: 8),
                Text(
                  'Traits',
                  style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
                ),
                const Spacer(),
                Icon(
                  Icons.arrow_drop_down,
                  color: colorScheme.onSurfaceVariant,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTraitPlate(String trait) {
    final colorScheme = Theme.of(context).colorScheme;
    final bool isIncluded = _criteria.selectedTraits[trait] ?? true;

    return Container(
      padding: const EdgeInsets.only(left: 10, right: 2, top: 2, bottom: 2),
      decoration: BoxDecoration(
        border: Border.all(color: colorScheme.inversePrimary, width: 2),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          GestureDetector(
            onTap: () {
              setState(() {
                _criteria.selectedTraits.remove(trait);
              });
              _notifyParent();
            },
            child: Text(
              trait,
              style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
            ),
          ),
          const SizedBox(width: 4),
          InkWell(
            onTap: () {
              setState(() {
                _criteria.selectedTraits[trait] = !isIncluded;
              });
              _notifyParent();
            },
            borderRadius: BorderRadius.circular(4),
            child: Padding(
              padding: const EdgeInsets.all(4.0),
              child: Icon(
                isIncluded ? Icons.check_circle_outline : Icons.block,
                size: 14,
                color: isIncluded
                    ? Colors.green
                    : Colors.red, // Used your blue/primary color here
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildKeywordSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildKeywordSelector(),
        if (_criteria.selectedKeywords.isNotEmpty) const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerLeft,
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _criteria.selectedKeywords.map((keyword) {
              return _buildKeywordPlate(keyword);
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildKeywordSelector() {
    final colorScheme = Theme.of(context).colorScheme;

    final availableKeywords= widget.availableKeywords
        .where((keyword) => !_criteria.selectedKeywords.contains(keyword))
        .toList();

    return LayoutBuilder(
      builder: (context, constraints) {

        return PopupMenuButton<String>(
          position: PopupMenuPosition.under,
          color: colorScheme.onSecondary,
          constraints: BoxConstraints(
            minWidth: constraints.maxWidth,
            maxWidth: constraints.maxWidth,
          ),
          onSelected: (String selected) {
            setState(() {
              _criteria.selectedKeywords.add(selected);
            });
            _notifyParent();
          },
          itemBuilder: (BuildContext context) {
            return availableKeywords.map((trait) {
              return PopupMenuItem<String>(
                value: trait,
                child: Text(
                  trait,
                  style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
                ),
              );
            }).toList();
          },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10,vertical: 10),
            decoration: BoxDecoration(
              border: Border.all(color: colorScheme.inversePrimary, width: 2),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Row(
              children: [
                Icon(Icons.search, size: 16, color: colorScheme.onSurfaceVariant),
                const SizedBox(width: 8),
                Text(
                  'Keywords',
                  style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
                ),
                const Spacer(),
                Icon(
                  Icons.arrow_drop_down,
                  color: colorScheme.onSurfaceVariant,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildKeywordPlate(String keyword) {
    final colorScheme = Theme.of(context).colorScheme;

    return GestureDetector(
      onTap: () {
        setState(() {
          _criteria.selectedKeywords.remove(keyword);
        });
        _notifyParent();
      },
      child:Container(
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        border: Border.all(color: colorScheme.inversePrimary, width: 2),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
              keyword,
              style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
            ),
          )
      );
  }

  Widget _buildLevelRangeBox({
    required String label,
    required int currentValue,
    required ValueChanged<int?> onChanged,
  }) {
    final colorScheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        border: Border.all(color: colorScheme.inversePrimary,width: 2),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Column(
        crossAxisAlignment: .start,
        children: [
          Text(label, style: const TextStyle(fontSize: 9, color: Colors.grey)),
          DropdownButtonHideUnderline(
            child: DropdownButton<int>(
              value: currentValue,
              isDense: true,
              isExpanded: true,
              dropdownColor: const Color(0xFF172030),
              style: const TextStyle(fontSize: 12, color: Colors.white),
              items: List.generate(21, (index) => index).map((lvl) {
                return DropdownMenuItem<int>(value: lvl, child: Text('$lvl'));
              }).toList(),
              onChanged: onChanged,
            ),
          ),
        ],
      ),
    );
  }
}
