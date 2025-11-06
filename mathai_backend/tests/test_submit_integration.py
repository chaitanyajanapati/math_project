from fastapi.testclient import TestClient
from main import app
from app.utils.db import SimpleDB
from app.models.questions import QuestionResponse


def test_submit_answer_with_normalized_answers():
    client = TestClient(app)
    db = SimpleDB()

    q = QuestionResponse(
        question="What is 3/8 as a decimal?",
        grade=5,
        difficulty="easy",
        topic="fractions",
        correct_answer="3/8",
        normalized_answers=["3/8", "0.375"],
        hints=[],
        solution_steps=["1. Convert 3/8 to decimal", "2. ..."]
    )

    db.save_question(q)

    payload = {
        "question_id": q.id,
        "student_answer": "0.375",
        "attempt_number": 1
    }

    resp = client.post("/api/submit-answer", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("is_correct") is True
    # When correct, API may include correct_answer in response
    assert data.get("confidence", 0) >= 0.9
