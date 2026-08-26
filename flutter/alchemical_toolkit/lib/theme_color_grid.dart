import 'package:flutter/material.dart';

class ThemeColorGrid extends StatelessWidget {
  const ThemeColorGrid({super.key});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

final Map<String, Color> themeColors = {
  // Primary Group
  'Primary': colorScheme.primary,
  'On Primary': colorScheme.onPrimary,
  'Primary Container': colorScheme.primaryContainer,
  'On Primary Container': colorScheme.onPrimaryContainer,
  'Primary Fixed': colorScheme.primaryFixed,
  'Primary Fixed Dim': colorScheme.primaryFixedDim,
  'On Primary Fixed': colorScheme.onPrimaryFixed,
  'On Primary Fixed Variant': colorScheme.onPrimaryFixedVariant,
  'Inverse Primary': colorScheme.inversePrimary,

  // Secondary Group
  'Secondary': colorScheme.secondary,
  'On Secondary': colorScheme.onSecondary,
  'Secondary Container': colorScheme.secondaryContainer,
  'On Secondary Container': colorScheme.onSecondaryContainer,
  'Secondary Fixed': colorScheme.secondaryFixed,
  'Secondary Fixed Dim': colorScheme.secondaryFixedDim,
  'On Secondary Fixed': colorScheme.onSecondaryFixed,
  'On Secondary Fixed Variant': colorScheme.onSecondaryFixedVariant,

  // Tertiary Group
  'Tertiary': colorScheme.tertiary,
  'On Tertiary': colorScheme.onTertiary,
  'Tertiary Container': colorScheme.tertiaryContainer,
  'On Tertiary Container': colorScheme.onTertiaryContainer,
  'Tertiary Fixed': colorScheme.tertiaryFixed,
  'Tertiary Fixed Dim': colorScheme.tertiaryFixedDim,
  'On Tertiary Fixed': colorScheme.onTertiaryFixed,
  'On Tertiary Fixed Variant': colorScheme.onTertiaryFixedVariant,

  // Error Group
  'Error': colorScheme.error,
  'On Error': colorScheme.onError,
  'Error Container': colorScheme.errorContainer,
  'On Error Container': colorScheme.onErrorContainer,

  // Surface & Containers Group
  'Surface': colorScheme.surface,
  'On Surface': colorScheme.onSurface,
  'On Surface Variant': colorScheme.onSurfaceVariant,
  'Inverse Surface': colorScheme.inverseSurface,
  'On Inverse Surface': colorScheme.onInverseSurface,
  'Surface Dim': colorScheme.surfaceDim,
  'Surface Bright': colorScheme.surfaceBright,
  'Surface Container Lowest': colorScheme.surfaceContainerLowest,
  'Surface Container Low': colorScheme.surfaceContainerLow,
  'Surface Container': colorScheme.surfaceContainer,
  'Surface Container High': colorScheme.surfaceContainerHigh,
  'Surface Container Highest': colorScheme.surfaceContainerHighest,
  'Surface Tint': colorScheme.surfaceTint,

  // Outline, Shadow & Overlay Group
  'Outline': colorScheme.outline,
  'Outline Variant': colorScheme.outlineVariant,
  'Shadow': colorScheme.shadow,
  'Scrim': colorScheme.scrim,
};

    return Scaffold(
      appBar: AppBar(
        title: const Text('Theme Color Palette'),
      ),
      body: GridView.builder(
        padding: const EdgeInsets.all(16.0),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 8, // 2 items per row
          crossAxisSpacing: 12.0,
          mainAxisSpacing: 12.0,
          childAspectRatio: 1.3,
        ),
        itemCount: themeColors.length,
        itemBuilder: (context, index) {
          final entry = themeColors.entries.elementAt(index);
          final colorName = entry.key;
          final colorValue = entry.value;

          // Convert Color to Hex string (e.g., #FF6200EE)
          final hexCode = '#${colorValue.value.toRadixString(16).padLeft(8, '0').substring(2).toUpperCase()}';

          // Determine contrasting text color based on background luminance
          final textColor = colorValue.computeLuminance() > 0.5 
              ? Colors.black 
              : Colors.white;

          return Card(
            color: colorValue,
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(
                color: Colors.black,
                width: 1,
              ),
            ),
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    colorName,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: textColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    hexCode,
                    style: TextStyle(
                      color: textColor,
                      fontSize: 12,
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}