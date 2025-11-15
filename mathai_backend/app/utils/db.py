from typing import Dict, List, Optional
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
from functools import lru_cache
import threading
from filelock import FileLock
from app.models.questions import QuestionResponse, StudentProgress


class SimpleDB:
    def __init__(self):
        self.db_dir = Path("data")
        self.db_dir.mkdir(exist_ok=True)
        self.questions_file = self.db_dir / "questions.json"
        self.progress_file = self.db_dir / "progress.json"
        
        # File locks for concurrent access
        self.questions_lock_file = self.db_dir / "questions.lock"
        self.progress_lock_file = self.db_dir / "progress.lock"
        
        self._init_db()
        
        # Performance: Add in-memory cache
        self._questions_cache = {}
        self._cache_lock = threading.Lock()
        self._load_cache()
        
    def _init_db(self):
        if not self.questions_file.exists():
            self.questions_file.write_text("{}")
        if not self.progress_file.exists():
            self.progress_file.write_text("{}")
    
    def _load_cache(self):
        """Load all questions into memory cache for faster reads"""
        with self._cache_lock:
            self._questions_cache = self._read_json(self.questions_file)
    
    def save_question(self, question: QuestionResponse):
        with FileLock(str(self.questions_lock_file)):
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
            self._write_json_atomic(self.questions_file, questions)
            
            # Update cache
            with self._cache_lock:
                self._questions_cache[question.id] = questions[question.id]
            
            return question.id
    
    def get_question(self, question_id: str) -> Optional[QuestionResponse]:
        # Performance: Read from cache first
        with self._cache_lock:
            if question_id in self._questions_cache:
                return QuestionResponse(**self._questions_cache[question_id])
        
        # Fallback to disk read with lock
        with FileLock(str(self.questions_lock_file)):
            questions = self._read_json(self.questions_file)
            if question_id in questions:
                with self._cache_lock:
                    self._questions_cache[question_id] = questions[question_id]
                return QuestionResponse(**questions[question_id])
        return None
    
    def update_progress(self, progress: StudentProgress):
        with FileLock(str(self.progress_lock_file)):
            all_progress = self._read_json(self.progress_file)
            key = f"{progress.student_id}_{progress.question_id}"
            progress_dict = progress.model_dump()
            progress_dict['last_attempt_at'] = progress_dict['last_attempt_at'].isoformat()
            all_progress[key] = progress_dict
            self._write_json_atomic(self.progress_file, all_progress)
    
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
        except Exception:
            return {}
    
    def _write_json(self, file_path: Path, data: Dict):
        """Legacy write method - kept for compatibility."""
        file_path.write_text(json.dumps(data, indent=2))
    
    def _write_json_atomic(self, file_path: Path, data: Dict):
        """Atomic write to prevent corruption from crashes or concurrent writes."""
        # Write to temporary file in same directory
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp"
        )
        
        try:
            # Write and sync to disk
            with os.fdopen(temp_fd, 'w') as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic rename (POSIX guarantee)
            os.replace(temp_path, file_path)
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            raise