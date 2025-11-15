import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mathai_mobile/main.dart';

void main() {
  testWidgets('Landing screen shows Start Practice button', (tester) async {
    await tester.pumpWidget(const MathAIApp());
    expect(find.text('Start Practice'), findsOneWidget);
  });
}
