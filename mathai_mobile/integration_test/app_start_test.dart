// Placeholder integration test. Requires an emulator or real device.
// Run locally (after emulator up):
// flutter test integration_test/app_start_test.dart --flavor dev
// Later can be migrated to `flutter drive` when UI interactions added.

import 'package:flutter_test/flutter_test.dart';
import 'package:mathai_mobile/main.dart';

void main() {
  testWidgets('App builds landing screen', (tester) async {
    await tester.pumpWidget(const MathAIApp());
    expect(find.text('Configure Practice'), findsOneWidget);
  });
}
