from typing import Dict, List, Optional
import json
from pathlib import Path
from datetime import datetime
from app.models.questions import QuestionResponse, StudentProgress

class SimpleDB:
    def __init__(self):
        self.db_dir = Path("data")
        self.db_dir.mkdir(exist_ok=True)
        self.questions_file = self.db_dir / "questions.json"
        self.progress_file = self.db_dir / "progress.json"
        self._init_db()
        
    def _init_db(self):
        if not self.questions_file.exists():
            self.questions_file.write_text("{}")
        if not self.progress_file.exists():
            self.progress_file.write_text("{}")
    
    def save_question(self, question: QuestionResponse):
        questions = self._read_json(self.questions_file)
        # Convert Pydantic model to dict and ensure datetimes are ISO-serializable
        qdict = question.model_dump()
        def _convert(obj):
            if isinstance(obj, dict):
                return {k: _convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_convert(v) for v in obj]
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        questions[question.id] = _convert(qdict)
        self._write_json(self.questions_file, questions)
        return question.id
    
    def get_question(self, question_id: str) -> Optional[QuestionResponse]:
        questions = self._read_json(self.questions_file)
        if question_id in questions:
            return QuestionResponse(**questions[question_id])
        return None
    
    def update_progress(self, progress: StudentProgress):
        all_progress = self._read_json(self.progress_file)
        key = f"{progress.student_id}_{progress.question_id}"
        progress_dict = progress.model_dump()
        progress_dict['last_attempt_at'] = progress_dict['last_attempt_at'].isoformat()
        all_progress[key] = progress_dict
        self._write_json(self.progress_file, all_progress)
    
    def get_student_progress(self, student_id: str) -> List[StudentProgress]:
        all_progress = self._read_json(self.progress_file)
        student_progress = []
        for key, progress in all_progress.items():
            if key.startswith(f"{student_id}_"):
                progress['last_attempt_at'] = datetime.fromisoformat(progress['last_attempt_at'])
                student_progress.append(StudentProgress(**progress))
        return student_progress
    
    def _read_json(self, file_path: Path) -> Dict:
        try:
            return json.loads(file_path.read_text())
        except:
            return {}
    
    def _write_json(self, file_path: Path, data: Dict):
        file_path.write_text(json.dumps(data, indent=2))