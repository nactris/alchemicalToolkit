import 'package:flutter/material.dart';
import 'layout.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'dart:io';
import 'package:flutter/services.dart';

Future main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      //systemNavigationBarColor: Colors.black, // Your desired color
      systemNavigationBarContrastEnforced:
          false, // Prevents Android from forcing a translucent/white scrim
    ),
  );

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
    return SafeArea(
      child: MaterialApp(
        title: 'AoN Alchemical Search',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.indigo,
            brightness: Brightness.dark,
          ),
        ),
        //home: const ThemeColorGrid(),
        home: const ArchivistMainScreen(title: 'PF2e Alchemical Search'),
      ),
    );
  }
}
