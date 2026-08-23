import 'package:alchemical_toolkit/file_service.dart';
import 'package:flutter/material.dart';
import 'layout.dart';
import 'dart:io';

class FormulaBookDetails extends StatefulWidget {
  final FormulaBook formulaBook;
  final Function(FormulaBook formulaBook, bool shouldSave) onChanged;

  const FormulaBookDetails({
    super.key,
    required this.formulaBook,
    required this.onChanged,
  });

  @override
  State<FormulaBookDetails> createState() => _FormulaBookDetailsState();
}

class _FormulaBookDetailsState extends State<FormulaBookDetails> {
  late TextEditingController _nameController;
  final _fService = FileService();

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.formulaBook.name);
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
          _buildFormulaBookSelector(),
          SizedBox(height: 12),
          Expanded(
            child: ListView(
              children: [
                SizedBox(height: 8),

                Row(
                  children: [
                    Expanded(child: _buildNameField()),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 86,
                      child: _buildLevelSelect(
                        boxLabel: "Book Level",
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
                SizedBox(height: 8),
                _buildDeleteButton(),
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
                currentSlots,
                (slotIndex) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2.0),
                  child: Text(
                    "Slot ${slotIndex + 1}",
                    style: TextStyle(color: colorScheme.onSurfaceVariant),
                  ),
                ),
              ),
              if (currentSlots < totalSlots)
                _buildSlot(
                  name:
                      "${totalSlots - currentSlots} slot${totalSlots - currentSlots > 1 ? 's' : ''} left",
                  onPressed: (val) => {print("pressed slot")},
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSlot({
    required String name,
    required ValueChanged<int?> onPressed,
  }) {
    final colorScheme = Theme.of(context).colorScheme;

    return SizedBox(
      width: double.infinity,
      child: Center(
        child: Row(
          children: [
            Expanded(
              child: TextButton(
                onPressed: () {
                  _openSlotDialog(name);
                  print("click!");
                },
                style: TextButton.styleFrom(
                  backgroundColor: colorScheme.onPrimaryFixedVariant,
                  shape: RoundedRectangleBorder(
                    borderRadius: const .all(Radius.circular(6)),
                    side: BorderSide(
                      color: colorScheme.onPrimaryFixedVariant,
                      width: 2,
                    ),
                  ),
                ),
                child: Text(
                  name,
                  style: TextStyle(color: colorScheme.onSurfaceVariant),
                ),
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

  Future<void> _openSlotDialog(String slotId) async {
    final colorScheme = Theme.of(context).colorScheme;
    final String? selectedFormula = await showDialog<String>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: colorScheme.surface,
          title: Text(
            'Assign Formula',
            style: TextStyle(color: colorScheme.onSurface),
          ),
          content: SizedBox(
            width: double.maxFinite,
            height: 300, 
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: widget.formulaBook.formulae.length,
              itemBuilder: (context, index) {
                final formula = widget.formulaBook.formulae[index];
                return ListTile(
                  title: Text(
                    formula,
                    style: TextStyle(color: colorScheme.onSurface),
                  ),
                  onTap: () {
                    Navigator.pop(context, formula);
                  },
                );
              },
            ),
          ),
        );
      },
    );

    if (selectedFormula != null) {
      setState(() {
        print("Assigned $selectedFormula to slot!");
      });
    }
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
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 12,
          vertical: 16,
        ),
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
                  print(index + (min ?? 0));
                },
                childDelegate: ListWheelChildBuilderDelegate(
                  childCount: (max ?? 20) - (min ?? 0) + 1,
                  builder: (context, index) {
                    return Center(
                      child: Text(
                        '${index + (min ?? 0)}',
                        style: TextStyle(
                          fontSize: 12,
                          color: colorScheme.onSurfaceVariant,
                        ),
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

    return FutureBuilder<List<Map<String, dynamic>>>(
      future: _fService.load(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const SizedBox(
            height: 48,
            child: Center(child: CircularProgressIndicator()),
          );
        }

        if (snapshot.hasError || !snapshot.hasData) {
          return const Text("Failed to load formula books");
        }

        final books = snapshot.data!;

        return InputDecorator(
          decoration: InputDecoration(
            isCollapsed: true,
            isDense: true,
            contentPadding: const EdgeInsets.only(
              left: 12,
              right: 4,
              top: 8,
              bottom: 8,
            ),
            labelText: "Formula Book",
            enabledBorder: OutlineInputBorder(
              borderSide: BorderSide(
                width: 2,
                color: colorScheme.inversePrimary,
              ),
              borderRadius: BorderRadius.circular(6),
            ),
          ),
          child: Row(
            children: [
              Expanded(
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    isExpanded: true,
                    hint: Text(
                      widget.formulaBook.name,
                      style: TextStyle(
                        fontSize: 12,
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                    items: books.map((book) {
                      return DropdownMenuItem<String>(
                        value: book["uuid"],
                        child: Text(book["name"]),
                      );
                    }).toList(),
                    onChanged: (select) {
                      if (select != null) {
                        final openBook = books.firstWhere(
                          (item) => item['uuid'] == select,
                        );
                        widget.formulaBook.update(openBook);
                        _updateBook(false);
                      }
                    },
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildDeleteButton() {
    final colorScheme = Theme.of(context).colorScheme;
    return OutlinedButton(
      onPressed: () => {
        _fService.delete(widget.formulaBook.uuid),
        widget.formulaBook.reset(),
        setState(() {}),
        _updateBook(false),
      },
      style: OutlinedButton.styleFrom(
        side: BorderSide(color: colorScheme.tertiaryContainer, width: 2),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
        backgroundColor: colorScheme.onTertiary,
      ),
      child: Text(
        "Delete Formula Book",
        style: TextStyle(fontSize: 12, color: colorScheme.tertiary),
      ),
    );
  }
}
