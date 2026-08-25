import 'package:flutter/material.dart';
import 'layout.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'dart:io';
Future main() async {
  if (Platform.isWindows || Platform.isLinux) {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi; 
  }
  runApp(ArchivistApp());
}

class ArchivistApp extends StatelessWidget {
  const ArchivistApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AoN Alchemical Search',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.indigo,
          brightness: Brightness.dark,

          ),
      ),
      //home: const ThemeColorGrid(),
      home: const ArchivistMainScreen(title: 'PF2e Alchemical Search'), 
    );
  }
}
