import 'package:flutter_test/flutter_test.dart';
import 'package:mathai_mobile/state/app_state.dart';
import 'package:mathai_mobile/models/question.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('AppState caches and restores question', () async {
  SharedPreferences.setMockInitialValues({});
  final appState = AppState();
    final q = Question(
      id: 'q1',
      question: 'What is 2 + 2?',
      grade: 3,
      difficulty: 'easy',
      topic: 'arithmetic',
      choices: ['3', '4', '5'],
      hints: [],
    );
    await appState.cacheQuestion(q);

  // Do NOT reset mock values so cached data persists
  final newState = AppState();
    await newState.loadCachedQuestion();
    expect(newState.lastQuestion?.id, 'q1');
    expect(newState.lastQuestion?.question, 'What is 2 + 2?');
    expect(newState.lastQuestion?.choices?.length, 3);
  });
}
