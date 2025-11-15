import time
from fastapi.testclient import TestClient
from mathai_backend.main import app

client = TestClient(app)

def test_full_question_answer_progress_flow():
    # 1. Generate a question
    payload = {
        "grade": 6,
        "difficulty": "medium",
        "topic": "algebra",
        "question_type": "open"
    }
    resp = client.post("/api/generate-question", json=payload)
    assert resp.status_code == 200, resp.text
    qdata = resp.json()
    assert qdata.get("id")
    assert qdata.get("question")
    # Hidden fields should be empty at first
    assert qdata.get("correct_answer") in ("", None)
    assert qdata.get("solution_steps") == []

    qid = qdata["id"]

    # 2. Submit an answer (intentionally arbitrary). This may be incorrect.
    submit_payload = {
        "question_id": qid,
        "student_answer": "0",
        "attempt_number": 1,
        "student_id": "itest_student"
    }
    ans_resp = client.post("/api/submit-answer", json=submit_payload)
    assert ans_resp.status_code == 200, ans_resp.text
    ans = ans_resp.json()
    assert "is_correct" in ans
    assert "points_earned" in ans

    # 3. Request a hint (only if not solved)
    if not ans.get("is_correct"):
        hint_resp = client.post(f"/api/questions/{qid}/hint", params={"hint_level": 1})
        assert hint_resp.status_code == 200, hint_resp.text
        hint = hint_resp.json()
        assert "hint" in hint

    # 4. Request solution (answer + steps). Should return answer and steps list
    sol_resp = client.post(f"/api/questions/{qid}/solution")
    assert sol_resp.status_code == 200, sol_resp.text
    sol = sol_resp.json()
    assert sol.get("answer")
    assert isinstance(sol.get("solution_steps"), list)

    # 5. Fetch progress for student
    prog_resp = client.get("/api/student-progress/itest_student")
    assert prog_resp.status_code == 200, prog_resp.text
    progress = prog_resp.json()
    assert "total_points" in progress
    assert progress.get("questions_attempted") >= 1

    # Basic invariant: success_rate between 0 and 1
    sr = progress.get("success_rate")
    assert 0 <= sr <= 1

    # Optional: ensure detailed_progress entries align with question id
    detailed = progress.get("detailed_progress", [])
    assert isinstance(detailed, list)
    assert any(entry.get("question_id") == qid for entry in detailed)
