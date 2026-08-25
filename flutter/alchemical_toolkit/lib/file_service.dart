import 'dart:convert';
import 'dart:io';
import 'package:alchemical_toolkit/database_service.dart';
import 'package:alchemical_toolkit/layout.dart';
import 'package:path_provider/path_provider.dart';
import 'package:uuid/uuid.dart';
import 'package:file_picker/file_picker.dart';

var uuidGen = Uuid();

class FileService {
  final String fileName;
  final _dbService = DatabaseService();
  FileService({this.fileName = 'formula_books.json'});

  Future<File> _getFile() async {
    final directory = await getApplicationDocumentsDirectory();
    return File('${directory.path}/$fileName');
  }

  Future<List<Map<String, dynamic>>> load() async {
    try {
      final file = await _getFile();
      if (!await file.exists()) {
        return [];
      }
      final contents = await file.readAsString();
      if (contents.isEmpty) return [];

      final List<dynamic> jsonList = jsonDecode(contents);
      return List<Map<String, dynamic>>.from(jsonList);
    } catch (e) {
      //print('Error reading JSON: $e');
      return [];
    }
  }

  Future<void> createFromFile() async {
    final result = await FilePicker.pickFile(
      type: FileType.custom,
      allowedExtensions: ['json'],
    );

    if (result != null && result.path != null) {
      final contents = await File(result.path!).readAsString();
      final jsonList = jsonDecode(contents);
      final book = Map<String, dynamic>.from(jsonList);
      await saveOrUpdate(uuid: book['uuid'], itemData: book);
    }
  }

  Future<void> exportAsJson(Map<String, dynamic> book) async {
    await FilePicker.saveFile(
      dialogTitle: 'Select save location',
      fileName: "${book['name'] ?? "Unnamed Book"}.json",
      type: FileType.custom,
      allowedExtensions: ['json'],
      bytes: utf8.encode(jsonEncode(book)),
    );
  }

  Future<void> exportAsText({
    required Map<String, dynamic> book,
    required Function(List data) parseFunction,
    required String ext,
  }) async {
    final items = await Future.wait(
      List<Future<Map<String, dynamic>>>.from(
        book['formulae'].map((item) async {
          final data = Map<String, dynamic>.from(
            (await _dbService.searchItems(id: item)).first,
          );
          return data;
        }),
      ),
    );
    items.sort((a, b) => a['level'].compareTo(b['level']));

    final output = parseFunction(items).toList().join('\n');

    await FilePicker.saveFile(
      dialogTitle: 'Select save location',
      fileName: "${book['name'] ?? "Unnamed Book"}$ext",
      type: FileType.custom,
      allowedExtensions: [ext],
      bytes: utf8.encode(output),
    );
  }

  Future<void> createNew() async {
    final empty = FormulaBook().map();
    await saveOrUpdate(uuid: empty['uuid'], itemData: empty);
  }

  Future<void> copy(Map<String, dynamic> book) async {
    book['uuid'] = uuidGen.v1();
    await saveOrUpdate(uuid: book['uuid'], itemData: book);
  }

  Future<void> save(List<Map<String, dynamic>> items) async {
    final file = await _getFile();
    file.writeAsString('');

    final jsonString = jsonEncode(items);
    await file.writeAsString(jsonString, flush: true);
  }

  Future<Map<String, dynamic>?> get(String id) async {
    final items = await load();
    try {
      return items.firstWhere((item) => item['uuid'] == id);
    } catch (_) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> getFirstOrNothing() async {
    final items = await load();
    try {
      return items.first;
    } catch (_) {
      return null;
    }
  }

  Future<void> saveOrUpdate({
    required String uuid,
    required Map<String, dynamic> itemData,
  }) async {
    itemData['date'] = DateTime.now().toIso8601String();

    final items = await load();
    final index = items.indexWhere((element) => element['uuid'] == uuid);
    //print(items.length);
    if (index != -1) {
      items[index] = itemData;
    } else {
      items.add(itemData);
      //print("add");
    }

    await save(items);
  }

  Future<void> delete(String idValue) async {
    final items = await load();
    items.removeWhere((item) => item['uuid'] == idValue);
    await save(items);
  }
}
