import 'package:alchemical_toolkit/file_service.dart';
import 'package:flutter/material.dart';

import 'layout.dart';
import 'dart:io';

class FormulaBookDetails extends StatefulWidget {
  final FormulaBook formulaBook;
  final List<Map<String, dynamic>> cachedItems;
  final Function(FormulaBook formulaBook, bool shouldSave) onChanged;

  const FormulaBookDetails({
    super.key,
    required this.formulaBook,
    required this.cachedItems,
    required this.onChanged,
  });

  @override
  State<FormulaBookDetails> createState() => _FormulaBookDetailsState();
}

class _FormulaBookDetailsState extends State<FormulaBookDetails> {
  late TextEditingController _nameController;
  List<SearchController> _slotControllers = [];
  final _fService = FileService();
  String _lastCategory = "Alchemical Crafting";
  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.formulaBook.name);
    _slotControllers = List.generate(22, (_) => SearchController());
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  void _updateBook(bool shouldSave) {
    print("updated details ${widget.formulaBook}");
    widget.onChanged(widget.formulaBook, shouldSave);
    _nameController.text = widget.formulaBook.name;
  }

  Map<String, dynamic> getItemDetails(String id) {
    final result = widget.cachedItems.firstWhere(
      (item) => item["id"] == id,
      orElse: () => {},
    );
    return result;
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
        crossAxisAlignment: .start,
        children: [
          Expanded(
            child: ListView(
              children: [
                _buildFormulaBookSelector(),
                SizedBox(height: 12),

                Row(
                  children: [
                    Expanded(child: _buildNameField()),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 86,
                      child: _buildLevelSelect(
                        boxLabel: "Level",
                        min: 1,
                        currentValue: widget.formulaBook.level,
                        onChanged: (val) {
                          if (val != null) {
                            widget.formulaBook.setLevel(val);
                            _updateBook(true);
                          }
                        },
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 12),
                //_buildLevelField(),
                ...List<Widget>.generate(
                  widget.formulaBook.level + 2,
                  (index) => _buildCatergory(index),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCatergory(int index) {
    final totalSlots = index == 0 ? 4 : 2;
    final parsedIndex = index > 1
        ? (index - 1).toString()
        : index == 0
        ? "Alchemical Crafting"
        : "Research Field";

    final currentSlots = widget.formulaBook.free[parsedIndex]?.length ?? 0;
    final colorScheme = Theme.of(context).colorScheme;

    return Padding(
      padding: EdgeInsets.symmetric(vertical: 8),
      child: InputDecorator(
        decoration: InputDecoration(
          //filled: true,
          //fillColor: colorScheme.inversePrimary,
          label: Text(
            "${index > 1 ? "Level " : ""}$parsedIndex",
            style: TextStyle(color: colorScheme.onSurfaceVariant),
          ),
          hintStyle: TextStyle(
            color: colorScheme.onSurfaceVariant,
            fontSize: 12,
          ),
          // prefixIcon: Icon(
          //   Icons.search,
          //   size: 16,
          //   color: colorScheme.onSurfaceVariant,
          // ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 8),
          enabledBorder: OutlineInputBorder(
            borderSide: BorderSide(color: colorScheme.inversePrimary, width: 2),
            borderRadius: BorderRadius.circular(6),
          ),
          focusedBorder: OutlineInputBorder(
            borderSide: BorderSide(color: colorScheme.inversePrimary, width: 2),
            borderRadius: BorderRadius.circular(6),
          ),
        ),
        child: Container(
          padding: EdgeInsets.only(top: 18, bottom: 16, left: 8, right: 8),
          child: Column(
            children: [
              ...List.generate(
                currentSlots * 2,
                (slotIndex) => (slotIndex % 2 == 1)
                    ? SizedBox(height: 4)
                    : SizedBox(
                        width: double.infinity,
                        child: Container(
                          child: TextButton(
                            onPressed: () {
                              widget.formulaBook.removeFree(
                                widget
                                        .formulaBook
                                        .free[parsedIndex]?[(slotIndex / 2)
                                        .toInt()] ??
                                    "",
                              );
                              _updateBook(true);
                            },
                            style: OutlinedButton.styleFrom(
                              side: BorderSide(
                                color: colorScheme.onPrimaryFixedVariant,
                                width: 2,
                              ),

                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(6),
                              ),
                            ),
                            child: Row(
                              children: [
                                Text(
                                  getItemDetails(
                                        widget
                                                .formulaBook
                                                .free[parsedIndex]?[(slotIndex /
                                                    2)
                                                .toInt()] ??
                                            "none",
                                      )['name'] ??
                                      "invalid name",
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: colorScheme.onSurfaceVariant,
                                  ),
                                ),
                                const Spacer(),
                                Text(
                                  "Level ${getItemDetails(widget.formulaBook.free[parsedIndex]?[(slotIndex / 2).toInt()] ?? "none")['level'] ?? "invalid level"}",
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: colorScheme.onSurfaceVariant,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
              ),
              if (currentSlots < totalSlots)
                _buildFreeFormulaSelection(
                  label:
                      "${totalSlots - currentSlots} slot${totalSlots - currentSlots > 1 ? 's' : ''} left",
                  index: parsedIndex,
                  controllerIndex: index,
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFreeFormulaSelection({
    required String label,
    required String index,
    required int controllerIndex,
  }) {
    final colorScheme = Theme.of(context).colorScheme;

    final avaiableFormulae = widget.formulaBook.formulae
        .where(
          (formula) => !widget.formulaBook.free.values
              .expand((i) => i)
              .contains(formula),
        )
        .toList();
    return SizedBox(
      width: double.infinity,
      child: Center(
        child: Row(
          children: [
            Expanded(
              child: SearchAnchor(
                isFullScreen: false,
                searchController: _slotControllers[controllerIndex],
                viewBackgroundColor: colorScheme.onSecondary,
                builder: (context, controller) {
                  return InkWell(
                    onTap: widget.formulaBook.formulae.isNotEmpty
                        ? () {
                            controller.openView();
                            _lastCategory = index;
                          }
                        : null,
                    borderRadius: BorderRadius.circular(6),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 10,
                      ),
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: colorScheme.onPrimaryFixedVariant,
                          width: 2,
                        ),
                        borderRadius: BorderRadius.circular(6),
                        //color: colorScheme.onPrimaryFixedVariant
                      ),
                      child: Row(
                        children: [
                          Center(
                            child: Text(
                              label,
                              style: TextStyle(
                                fontSize: 12,
                                color: colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ),
                          const Spacer(),
                          Icon(
                            widget.formulaBook.formulae.isNotEmpty
                                ? Icons.arrow_drop_down
                                : Icons.block,
                            color: colorScheme.onSurfaceVariant,
                          ),
                        ],
                      ),
                    ),
                  );
                },
                enabled: avaiableFormulae.isNotEmpty,
                viewHintText: 'Search formulae...',
                viewOnSubmitted: (text) {
                  if (text.isEmpty) return;

                  final matches = widget.formulaBook.formulae.where(
                    (formula) =>
                        formula.toLowerCase().contains(text.toLowerCase()),
                  );

                  if (matches.isNotEmpty) {
                    final selected = matches.first;
                    //print(selected);
                    //widget.criteria.selectedKeywords.add(selected);
                    //_updateCriteria();
                    _slotControllers[controllerIndex].closeView(selected);
                  }
                },
                suggestionsBuilder: (context, controller) {
                  final query = controller.text.toLowerCase();

                  final filtered = avaiableFormulae
                      .where((formula) {
                        return formula.toLowerCase().contains(query);
                      })
                      .map((item) => getItemDetails(item))
                      .toList();

                  filtered.sort(
                    (a, b) => a['name'].toLowerCase().compareTo(
                      b['name'].toLowerCase(),
                    ),
                  );
                  filtered.sort((a, b) => a['level'].compareTo(b['level']));

                  return filtered.map((item) {
                    return ListTile(
                      dense: true,
                      title: Row(
                        children: [
                          Text(
                            item['name'] ?? "none",
                            style: TextStyle(
                              fontSize: 12,
                              color: colorScheme.onSurface,
                            ),
                          ),
                          const Spacer(),
                          Text(
                            "Level ${item['level']}",
                            style: TextStyle(
                              fontSize: 12,
                              color: colorScheme.onSurface,
                            ),
                          ),
                        ],
                      ),
                      onTap: () {
                        widget.formulaBook.setFree(_lastCategory, item['id']);
                        controller.closeView(item['id']);
                        controller.clear();
                        _updateBook(true);
                      },
                    );
                  });
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNameField() {
    final colorScheme = Theme.of(context).colorScheme;
    return TextField(
      controller: _nameController,
      style: TextStyle(fontSize: 12, color: colorScheme.onSurfaceVariant),
      onSubmitted: (val) => {
        widget.formulaBook.name = val.trim().isEmpty ? "" : val.trim(),
        _updateBook(true),
      },
      decoration: InputDecoration(
        label: Text(
          'Name',
          style: TextStyle(color: colorScheme.onSurfaceVariant),
        ),
        hintStyle: TextStyle(color: colorScheme.onSurfaceVariant, fontSize: 12),
        // prefixIcon: Icon(
        //   Icons.draw,
        //   size: 16,
        //   color: colorScheme.onSurfaceVariant,
        // ),
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
        contentPadding: Platform.isAndroid || Platform.isIOS
            ? const EdgeInsets.symmetric(horizontal: 0, vertical: 0)
            : const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
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
          ? TextButton(
              onPressed: () => _openLevelDialog(onChanged: onChanged),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 16,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6),
                ),
                //backgroundColor: colorScheme.secondaryFixed,
              ),
              child: Text(
                widget.formulaBook.level.toString(),
                style: TextStyle(
                  fontSize: 12,
                  color: colorScheme.onSurfaceVariant,
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
                      (index) => (min ?? 0) + index,
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

  Widget _buildFormulaBookSelector() {
    final colorScheme = Theme.of(context).colorScheme;

    return OutlinedButton(
      onPressed: _openBookDialog,
      style: OutlinedButton.styleFrom(
        side: BorderSide(color: colorScheme.primaryContainer, width: 2),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        //backgroundColor: colorScheme.secondaryFixed,
      ),
      child: Text(
        "Select Formula Book",
        style: TextStyle(fontSize: 12, color: colorScheme.onSurfaceVariant),
      ),
    );
  }

  Future<void> _openBookDialog() async {
    final colorScheme = Theme.of(context).colorScheme;
    dynamic selectedHighlight;

    Future<List<dynamic>> booksFuture = _fService.load();

    await showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 12,
              ),
              titlePadding: EdgeInsets.zero,
              actionsPadding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 12,
              ),
              backgroundColor: colorScheme.onSecondaryFixed,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(6),
                side: BorderSide(color: colorScheme.inversePrimary, width: 2),
              ),
              title: Container(
                decoration: BoxDecoration(
                  color: colorScheme.inversePrimary,
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: colorScheme.inversePrimary,
                    width: 2,
                  ),
                ),
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: Center(
                    child: Text(
                      'Select Formula Book',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: colorScheme.onSurface,
                      ),
                    ),
                  ),
                ),
              ),
              content: SizedBox(
                width: double.maxFinite,
                height: 400,
                child: FutureBuilder<List<dynamic>>(
                  future: booksFuture, // 2. Pass the cached variable here
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return const Center(child: CircularProgressIndicator());
                    }

                    if (snapshot.hasError ||
                        !snapshot.hasData ||
                        (snapshot.data as List).isEmpty) {
                      return Center(
                        child: Text(
                          'No formula books found.',
                          style: TextStyle(color: colorScheme.onSurface),
                        ),
                      );
                    }

                    final books = snapshot.data!;

                    return ListView.builder(
                      shrinkWrap: true,
                      itemCount: books.length,
                      itemBuilder: (context, index) {
                        final book = books[index];
                        final time =
                            DateTime.tryParse(book['date'] ?? "") ??
                            DateTime.now();
                        final isSelected = selectedHighlight == book;

                        return Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                              color: isSelected
                                  ? colorScheme.primary
                                  : colorScheme.inversePrimary,
                              width: 2,
                            ),
                          ),
                          child: Column(
                            children: [
                              ListTile(
                                contentPadding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 4,
                                ),
                                title: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Expanded(
                                      child: Text(
                                        book['name'] ?? "Unnamed Book",
                                        style: TextStyle(
                                          color: colorScheme.onSurface,
                                          fontWeight: FontWeight.bold,
                                        ),
                                        softWrap: true,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      "Level ${book['level'] ?? 0}",
                                      style: TextStyle(
                                        color: colorScheme.onSurface,
                                        fontSize: 14,
                                      ),
                                    ),
                                  ],
                                ),
                                subtitle: Padding(
                                  padding: const EdgeInsets.only(top: 4),
                                  child: Text(
                                    parseDate(time),
                                    style: TextStyle(
                                      color: colorScheme.onSurfaceVariant,
                                      fontSize: 11,
                                    ),
                                  ),
                                ),
                                onTap: () {
                                  setDialogState(() {
                                    selectedHighlight = isSelected
                                        ? null
                                        : book;
                                  });
                                },
                              ),
                              if (isSelected)
                                Padding(
                                  padding: const EdgeInsets.only(
                                    left: 8.0,
                                    right: 8.0,
                                    bottom: 8.0,
                                  ),
                                  child: Row(
                                    children: [
                                      Expanded(
                                        child: OutlinedButton(
                                          style: OutlinedButton.styleFrom(
                                            padding: EdgeInsets.zero,
                                            shape: RoundedRectangleBorder(
                                              borderRadius:
                                                  BorderRadius.circular(6),
                                            ),
                                            side: BorderSide(
                                              color: colorScheme
                                                  .onPrimaryFixedVariant,
                                              width: 1,
                                            ),
                                            visualDensity:
                                                VisualDensity.compact,
                                          ),
                                          onPressed: () {
                                            Navigator.pop(context);
                                            widget.formulaBook.update(book);
                                            _updateBook(false);
                                          },
                                          child: const Text('Open'),
                                        ),
                                      ),
                                      const SizedBox(width: 6),
                                      Expanded(
                                        child: OutlinedButton(
                                          style: OutlinedButton.styleFrom(
                                            padding: EdgeInsets.zero,
                                            shape: RoundedRectangleBorder(
                                              borderRadius:
                                                  BorderRadius.circular(6),
                                            ),
                                            side: BorderSide(
                                              color: colorScheme
                                                  .onPrimaryFixedVariant,
                                              width: 1,
                                            ),
                                            visualDensity:
                                                VisualDensity.compact,
                                          ),
                                          onPressed: () async {
                                            // await _fService.copy(book);
                                            print("TODO");
                                            setDialogState(() {
                                              selectedHighlight = null;
                                              booksFuture = _fService.load();
                                            });
                                          },
                                          child: const Text('Copy'),
                                        ),
                                      ),
                                      const SizedBox(width: 6),
                                      Expanded(
                                        child: OutlinedButton(
                                          style: OutlinedButton.styleFrom(
                                            padding: EdgeInsets.zero,
                                            shape: RoundedRectangleBorder(
                                              borderRadius:
                                                  BorderRadius.circular(6),
                                            ),
                                            side: BorderSide(
                                              color: colorScheme
                                                  .onPrimaryFixedVariant,
                                              width: 1,
                                            ),
                                            foregroundColor: colorScheme.error,
                                            visualDensity:
                                                VisualDensity.compact,
                                          ),
                                          onPressed: () async {
                                            final confirm =
                                                await _openConfirmDeleteDialog(
                                                  context: context,
                                                  bookName:
                                                      book['name'] ?? 'Book',
                                                );
                                            if (confirm) {
                                              await _fService.delete(
                                                book['uuid'],
                                              );
                                              setDialogState(() {
                                                selectedHighlight = null;
                                                booksFuture = _fService.load();
                                              });
                                            }
                                          },
                                          child: const Text('Delete'),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                            ],
                          ),
                        );
                      },
                    );
                  },
                ),
              ),
              actions: [
                Row(
                  children: [
                    Expanded(
                      child: FilledButton.icon(
                        style: FilledButton.styleFrom(
                          backgroundColor: colorScheme.inversePrimary,
                          foregroundColor: colorScheme.onSurface,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(6),
                          ),
                        ),
                        icon: const Icon(Icons.add),
                        label: const Text('New'),
                        onPressed: () async {
                          widget.formulaBook.reset();
                          _updateBook(true);
                          setDialogState(() {
                            selectedHighlight = null;
                            booksFuture = _fService.load();
                          });

                          //Navigator.pop(context);
                        },
                      ),
                    ),
                  ],
                ),
              ],
            );
          },
        );
      },
    );
  }

  String parseDate(dynamic input) {
    final DateTime date = input is String
        ? DateTime.parse(input)
        : (input as DateTime);

    final local = date.toLocal();

    const weekdays = [
      'Monday',
      'Tuesday',
      'Wednesday',
      'Thursday',
      'Friday',
      'Saturday',
      'Sunday',
    ];
    const months = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];

    final weekday = weekdays[local.weekday - 1];
    final month = months[local.month - 1];
    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');

    return '$weekday, ${local.day} $month ${local.year} $hour:$minute';
  }

  Future<void> _openLevelDialog({required ValueChanged<int> onChanged}) async {
    final colorScheme = Theme.of(context).colorScheme;

    final selectedNumber = await showDialog<int>(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          backgroundColor: colorScheme.onSecondaryFixed,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: BorderSide(color: colorScheme.inversePrimary, width: 2),
          ),
          clipBehavior:
              Clip.antiAlias, // Clips title background to dialog border radius
          child: SizedBox(
            width: 320,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Title Header with inversePrimary background
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  color: colorScheme.inversePrimary,
                  child: Text(
                    'Select Level',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: colorScheme.onSurface,
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                // Grid of Outlined Buttons 1-20
                Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 5,
                          crossAxisSpacing: 8,
                          mainAxisSpacing: 8,
                          childAspectRatio: 1,
                        ),
                    itemCount: 20,
                    itemBuilder: (context, index) {
                      final number = index + 1;
                      final isSelected = number == widget.formulaBook.level;

                      return OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          padding: EdgeInsets.zero,
                          side: BorderSide(
                            color: isSelected
                                ? colorScheme.primary
                                : colorScheme.inversePrimary,
                            width: isSelected ? 2 : 1,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(6),
                          ),
                        ),
                        onPressed: () => Navigator.pop(context, number),
                        child: Text(
                          '$number',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: isSelected
                                ? FontWeight.bold
                                : FontWeight.normal,
                            color: colorScheme.onSurface,
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );

    if (selectedNumber != null) {
      onChanged(selectedNumber);
    }
  }

  Future<bool> _openConfirmDeleteDialog({
    required BuildContext context,
    required String bookName,
  }) async {
    final colorScheme = Theme.of(context).colorScheme;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          actionsAlignment: MainAxisAlignment.spaceAround,
          actionsPadding: EdgeInsets.symmetric(vertical: 12, horizontal: 16),
          backgroundColor: colorScheme.surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: BorderSide(color: colorScheme.inversePrimary, width: 2),
          ),
          title: Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: colorScheme.error),
              const SizedBox(width: 8),
              Text(
                'Delete Book',
                style: TextStyle(color: colorScheme.onSurface),
              ),
            ],
          ),
          content: Text(
            'Are you sure you want to delete "$bookName"?',
            style: TextStyle(color: colorScheme.onSurfaceVariant),
          ),
          actions: [
            OutlinedButton(
              style: OutlinedButton.styleFrom(
                padding: EdgeInsets.symmetric(vertical: 16, horizontal: 32),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6),
                ),
                side: BorderSide(
                  color: colorScheme.onPrimaryFixedVariant,
                  width: 1,
                ),
                //foregroundColor: colorScheme.error,
                visualDensity: VisualDensity.compact,
              ),
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              style: OutlinedButton.styleFrom(
                side: BorderSide(
                  color: colorScheme.tertiaryContainer,
                  width: 2,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6),
                ),
                backgroundColor: colorScheme.onTertiary,
                padding: EdgeInsets.symmetric(vertical: 16, horizontal: 32),
                visualDensity: VisualDensity.compact,
                foregroundColor: colorScheme.error,
              ),
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );

    return confirmed ?? false;
  }
}
