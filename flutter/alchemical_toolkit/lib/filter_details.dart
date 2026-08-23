import 'package:flutter/material.dart';
import 'layout.dart';
import 'dart:io';

class FilterPanel extends StatefulWidget {
  final Function(FilterCriteria criteria) onChanged;
  final FilterCriteria criteria;
  final List<String> keywords;
  final List<String> traits;

  const FilterPanel({
    super.key,
    required this.traits,
    required this.onChanged,
    required this.criteria,
    this.keywords = const [
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
    ],
  });

  @override
  State<FilterPanel> createState() => _FilterPanelState();
}

class _FilterPanelState extends State<FilterPanel> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _maximumValueControler = TextEditingController();
  final TextEditingController _minimumValueControler = TextEditingController();
  final SearchController _keywordController = SearchController();
  final SearchController _traitController = SearchController();


  @override
  void initState() {
    super.initState();
   
  }

  @override
  void dispose() {
    _nameController.dispose();
    _keywordController.dispose();
    _traitController.dispose();
    _maximumValueControler.dispose();
    _minimumValueControler.dispose();
    super.dispose();
  }

  void _updateCriteria() {
    widget.onChanged(widget.criteria);
  }

  void _clearFilters() {
    setState(() {
      _nameController.clear();
    });
    widget.criteria.reset();
    _updateCriteria();
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

                  _buildKnownOnlyButton(),
                  const SizedBox(height: 8),

                  _buildClearButton(),
                  const SizedBox(height: 16),

                  _buildTraitsSection(),
                  const SizedBox(height: 12),

                  _buildKeywordSection(),
                  const SizedBox(height: 16),

                  Row(
                    children: [
                      Expanded(
                        child: _buildLevelSelect(
                          boxLabel: "Min",
                          max: widget.criteria.maxLevel,
                          currentValue: widget.criteria.minLevel,
                          onChanged: (val) {
                            if (val != null) {
                              widget.criteria.minLevel = val;
                              _updateCriteria();
                            }
                          },
                        ),
                      ),
                      Padding(
                        padding: EdgeInsets.symmetric(horizontal: 6.0),
                        child: Text(
                          '-',
                          style: TextStyle(color: colorScheme.onSurfaceVariant),
                        ),
                      ),
                      Expanded(
                        child: _buildLevelSelect(
                          boxLabel: "Max",
                          min: widget.criteria.minLevel,
                          currentValue: widget.criteria.maxLevel,
                          onChanged: (val) {
                            if (val != null) {
                              widget.criteria.maxLevel = val;
                              _updateCriteria();
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
        widget.criteria.name = val.trim().isEmpty ? null : val.trim();
        _updateCriteria();
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
            initialValue: widget.criteria.sortBy,
            onSelected: (String selected) {
              if (selected != widget.criteria.sortBy) {
                widget.criteria.sortBy = selected;
                _updateCriteria();
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
                    sortLabels[widget.criteria.sortBy] ?? 'Level',
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
          widget.criteria.ascending ? Icons.move_down : Icons.move_up,
          size: 24,
          color: colorScheme.onSurfaceVariant,
        ),
        onPressed: () {
          widget.criteria.ascending = !widget.criteria.ascending;
          _updateCriteria();
        },
        style: IconButton.styleFrom(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
      ),
    );
  }

  Widget _buildKnownOnlyButton() {
    final colorScheme = Theme.of(context).colorScheme;
    final bool isSelected = widget.criteria.knownOnly;
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: () {
          widget.criteria.knownOnly = !widget.criteria.knownOnly;
          _updateCriteria();
        },
        style: OutlinedButton.styleFrom(
          side: BorderSide(
            color: isSelected
                ? colorScheme.primary
                : colorScheme.inversePrimary,
            width: 2,
          ),
          backgroundColor: colorScheme.onSecondaryFixed,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
        icon: Icon(
          isSelected ? Icons.bookmark : Icons.bookmark_border,
          size: 14,
          color: isSelected
              ? colorScheme.primary
              : colorScheme.onSurfaceVariant,
        ),
        label: Text(
          'Known Only',
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
          side: BorderSide(color: colorScheme.inversePrimary, width: 2),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        ),
        child: Text(
          'Clear All Filters',
          style: TextStyle(fontSize: 12, color: colorScheme.onSurfaceVariant),
        ),
      ),
    );
  }

  Widget _buildTraitsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTraitSelector(),
        if (widget.criteria.selectedTraits.isNotEmpty)
          const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerLeft,
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: widget.criteria.selectedTraits.keys.map((trait) {
              return _buildTraitPlate(trait);
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildTraitSelector() {
    final colorScheme = Theme.of(context).colorScheme;

    final availableTraits = widget.traits
        .where((trait) => !widget.criteria.selectedTraits.containsKey(trait))
        .toList();

    return SearchAnchor(
      isFullScreen: false,
      searchController: _traitController,
      viewBackgroundColor: colorScheme.onSecondary,
      builder: (context, controller) {
        return InkWell(
          onTap: availableTraits.isNotEmpty ? controller.openView : null,
          borderRadius: BorderRadius.circular(6),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
            decoration: BoxDecoration(
              border: Border.all(color: colorScheme.inversePrimary, width: 2),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.search,
                  size: 16,
                  color: colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: 8),
                Text(
                  'Traits',
                  style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
                ),
                const Spacer(),
                Icon(
                  availableTraits.isNotEmpty
                      ? Icons.arrow_drop_down
                      : Icons.block,
                  color: colorScheme.onSurfaceVariant,
                ),
              ],
            ),
          ),
        );
      },
      viewHintText: 'Search traits...',
      viewOnSubmitted: (text) {
        if (text.isEmpty) return;

        final matches = availableTraits.where(
          (trait) => trait.toLowerCase().contains(text.toLowerCase()),
        );

        if (matches.isNotEmpty) {
          final selected = matches.first;

          widget.criteria.selectedTraits[selected] = true;
          _updateCriteria();
          _traitController.closeView(selected);
        }
      },
      suggestionsBuilder: (context, controller) {
        final query = controller.text.toLowerCase();

        final filtered = availableTraits.where((trait) {
          return trait.toLowerCase().contains(query);
        }).toList();

        return filtered.map((trait) {
          return ListTile(
            dense: true,
            title: Text(
              trait,
              style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
            ),
            onTap: () {
              widget.criteria.selectedTraits[trait] = true;
              _updateCriteria();
              controller.closeView(trait);
              controller.clear();
            },
          );
        });
      },
    );
  }

  Widget _buildTraitPlate(String trait) {
    final colorScheme = Theme.of(context).colorScheme;
    final bool isIncluded = widget.criteria.selectedTraits[trait] ?? true;

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
              widget.criteria.selectedTraits.remove(trait);
              _updateCriteria();
            },
            child: Text(
              trait,
              style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
            ),
          ),
          const SizedBox(width: 4),
          InkWell(
            onTap: () {
              widget.criteria.selectedTraits[trait] = !isIncluded;
              _updateCriteria();
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
        if (widget.criteria.selectedKeywords.isNotEmpty)
          const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerLeft,
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: widget.criteria.selectedKeywords.map((keyword) {
              return _buildKeywordPlate(keyword);
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildKeywordSelector() {
    final colorScheme = Theme.of(context).colorScheme;

    final availableKeywords = widget.keywords
        .where((keyword) => !widget.criteria.selectedKeywords.contains(keyword))
        .toList();

    return SearchAnchor(
      isFullScreen: false,
      searchController: _keywordController,
      viewBackgroundColor: colorScheme.onSecondary,
      builder: (context, controller) {
        return InkWell(
          onTap: widget.keywords.isNotEmpty ? controller.openView : null,
          borderRadius: BorderRadius.circular(6),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
            decoration: BoxDecoration(
              border: Border.all(color: colorScheme.inversePrimary, width: 2),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.search,
                  size: 16,
                  color: colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: 8),
                Text(
                  'Keywords',
                  style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
                ),
                const Spacer(),
                Icon(
                  widget.keywords.isNotEmpty
                      ? Icons.arrow_drop_down
                      : Icons.block,
                  color: colorScheme.onSurfaceVariant,
                ),
              ],
            ),
          ),
        );
      },
      viewHintText: 'Search keywords...',
      viewOnSubmitted: (text) {
        if (text.isEmpty) return;

        final matches = widget.keywords.where(
          (key) => key.toLowerCase().contains(text.toLowerCase()),
        );

        if (matches.isNotEmpty) {
          final selected = matches.first;

          widget.criteria.selectedKeywords.add(selected);
          _updateCriteria();

          _keywordController.closeView(selected);
        }
      },
      suggestionsBuilder: (context, controller) {
        final query = controller.text.toLowerCase();

        final filtered = availableKeywords.where((keyword) {
          return keyword.toLowerCase().contains(query);
        }).toList();

        return filtered.map((keyword) {
          return ListTile(
            dense: true,
            title: Text(
              keyword,
              style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
            ),
            onTap: () {
              widget.criteria.selectedKeywords.add(keyword);
              _updateCriteria();
              controller.closeView(keyword);
              controller.clear();
            },
          );
        });
      },
    );
  }

  Widget _buildKeywordPlate(String keyword) {
    final colorScheme = Theme.of(context).colorScheme;

    return GestureDetector(
      onTap: () {
        widget.criteria.selectedKeywords.remove(keyword);
        _updateCriteria();
      },
      child: Container(
        padding: const EdgeInsets.all(4),
        decoration: BoxDecoration(
          border: Border.all(color: colorScheme.inversePrimary, width: 2),
          borderRadius: BorderRadius.circular(6),
        ),
        child: Text(
          keyword,
          style: TextStyle(fontSize: 12, color: colorScheme.onSurface),
        ),
      ),
    );
  }

    Widget _buildLevelSelect({
    required String boxLabel,
    int? min,
    int? max,
    required int currentValue,
    required ValueChanged<int?> onChanged,
  }) {
    final colorScheme = Theme.of(context).colorScheme;

    return InputDecorator(
      expands: false,
      decoration: InputDecoration(
        isCollapsed: true,
        isDense: true,
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
        floatingLabelAlignment: FloatingLabelAlignment.start,
        floatingLabelStyle: TextStyle(
          fontSize: 14,
          color: colorScheme.onSurfaceVariant,
        ),

        label: Text(
          boxLabel,
          style: TextStyle(color: colorScheme.onSurfaceVariant),
        ),
        enabledBorder: OutlineInputBorder(
          borderSide: BorderSide(width: 2, color: colorScheme.inversePrimary),
          borderRadius: BorderRadius.circular(6),
        ),
      ),
      child: Platform.isAndroid || Platform.isIOS
          ? SizedBox(
              height: 32,
              child: ListWheelScrollView.useDelegate(
                itemExtent: 30,
                perspective: 0.003,
                diameterRatio: 1.5,
                physics: const FixedExtentScrollPhysics(),
                onSelectedItemChanged: (index) {
                  //print(index + (min ?? 0));
                },
                childDelegate: ListWheelChildBuilderDelegate(
                  childCount: (max ?? 20) - (min ?? 0) + 1,
                  builder: (context, index) {
                    return Center(
                      child: Text(
                        '${index + (min ?? 0)}',
                        style: const TextStyle(fontSize: 12),
                      ),
                    );
                  },
                ),
              ),
            )
          : DropdownButtonHideUnderline(
              child: DropdownButton<int>(
                value: currentValue,
                isDense: true,
                style: TextStyle(fontSize: 13, color: colorScheme.onSurface),
                items:
                    List.generate(
                      (max ?? 20) - (min ?? 0) + 1,
                      (index) => (min??0) + index,
                    ).map((number) {
                      return DropdownMenuItem<int>(
                        value: number,
                        child: Text(
                          '$number',
                          style: TextStyle(color: colorScheme.onSurfaceVariant),
                        ),
                      );
                    }).toList(),
                onChanged: (newValue) {
                  if (newValue != null) {
                    onChanged(newValue);
                  }
                },
              ),
            ),
    );
  }
}
