from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
import time
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from starlette.concurrency import run_in_threadpool

from app.models.questions import (
    QuestionRequest, QuestionResponse, AnswerSubmission,
    AnswerResponse, StudentProgress
)
from app.utils.math_service import MathAIService
from app.utils.db import SimpleDB
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

# Dependencies
def get_math_service():
    return MathAIService()

def get_db():
    return SimpleDB()

@router.post("/generate-question", response_model=QuestionResponse)
async def generate_question_api(
    req: QuestionRequest,
    math_service: MathAIService = Depends(get_math_service),
    db: SimpleDB = Depends(get_db)
):
    """Generate a math question only. Hints and solutions are generated on-demand via separate endpoints."""
    logger.info(
        "Received question request",
        extra={
            "grade": req.grade,
            "difficulty": req.difficulty.value,
            "topic": req.topic.value,
            "question_type": req.question_type.value
        }
    )
    try:
        # Use threadpool for CPU-bound question generation
        question_text = await run_in_threadpool(
            math_service.generate_question_only,
            req.grade,
            req.difficulty.value,
            req.topic.value
        )

        # Generate solution (CPU-bound)
        answer, solution_steps = await run_in_threadpool(
            math_service.generate_solution_for_question,
            question_text,
            req.topic.value
        )
        
        # For MCQ, also generate distractors
        all_choices = None
        if req.question_type.value == "mcq":
            if answer:
                distractors = await run_in_threadpool(
                    math_service.generate_distractors,
                    answer,
                    req.topic.value
                )
                all_choices = math_service.mix_choices(answer, distractors)

        question_response = QuestionResponse(
            question=question_text,
            grade=req.grade,
            difficulty=req.difficulty.value,
            topic=req.topic.value,
            correct_answer=answer or "",
            normalized_answers=math_service.normalize_answer(answer) if answer else [],
            choices=all_choices,
            hints=[],
            solution_steps=solution_steps or []
        )

        logger.info(
            "Generated question",
            extra={
                "question_type": req.question_type.value,
                "has_choices": all_choices is not None,
                "num_steps": len(solution_steps) if solution_steps else 0
            }
        )

        try:
            db.save_question(question_response)
        except Exception as db_error:
            logger.warning("Could not save question to database", extra={"error": str(db_error)})

        # Hide correct_answer, normalized_answers, and solution_steps before returning to frontend
        safe_response = question_response.model_copy()
        safe_response.correct_answer = ""
        safe_response.normalized_answers = []
        safe_response.solution_steps = []  # Hide steps initially
        return safe_response

    except Exception as e:
        logger.error("Error in generate_question_api", extra={"error": str(e)}, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/{question_id}/hint")
async def generate_hint_api(
    question_id: str,
    hint_level: int = 1,  # 1=conceptual, 2=strategic, 3=procedural
    math_service: MathAIService = Depends(get_math_service),
    db: SimpleDB = Depends(get_db)
):
    """Generate a progressive hint for a stored question on-demand.
    
    Hint levels:
    - 1 (Conceptual): What concept/formula to use
    - 2 (Strategic): What approach/strategy to take
    - 3 (Procedural): Specific first step
    
    Each level reveals more information. Cost: -10 points per hint level used.
    """
    try:
        q = db.get_question(question_id)
        if not q:
            raise HTTPException(status_code=404, detail="Question not found")

        # Clamp hint_level to valid range
        hint_level = max(1, min(3, hint_level))

        # Use threadpool for CPU-bound hint generation
        hint = await run_in_threadpool(
            math_service.generate_hint_for_question,
            q.question,
            q.topic,
            hint_level=hint_level
        )

        # Store all hints for tracking (append if multiple levels requested)
        if not q.hints:
            q.hints = []
        if hint not in q.hints:
            q.hints.append(hint)
        try:
            db.save_question(q)
        except Exception as db_error:
            logger.warning("Could not update question with hint", extra={"error": str(db_error)})

        logger.info("Generated hint", extra={"question_id": question_id, "hint_level": hint_level})
        return {"hint": hint, "hint_level": hint_level, "points_penalty": hint_level * 10}

    except Exception as e:
        logger.error("Error generating hint", extra={"question_id": question_id, "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/{question_id}/solution")
async def generate_solution_api(
    question_id: str,
    math_service: MathAIService = Depends(get_math_service),
    db: SimpleDB = Depends(get_db)
):
    """Generate solution (answer + steps) for a stored question on-demand."""
    try:
        q = db.get_question(question_id)
        if not q:
            raise HTTPException(status_code=404, detail="Question not found")

        # If solution already exists (e.g., for MCQ questions), return it
        if q.correct_answer and q.solution_steps:
            logger.info("Returning stored solution", extra={"question_id": question_id})
            return {"answer": q.correct_answer, "solution_steps": q.solution_steps}
        
        # Otherwise, generate solution on-demand (CPU-bound)
        answer, steps = await run_in_threadpool(
            math_service.generate_solution_for_question,
            q.question,
            q.topic
        )

        # Normalize answer(s) and store variants for robust validation
        logger.debug("Pre-normalizing answer", extra={"answer": answer})
        normalized_list = math_service.normalize_answer(answer) if answer else []

        # Persist solution to DB (store correct answer and steps)
        q.correct_answer = answer
        q.normalized_answers = normalized_list
        q.solution_steps = steps
        try:
            db.save_question(q)
        except Exception as db_error:
            logger.warning("Could not update question with solution", extra={"error": str(db_error)})

        logger.info("Generated solution on-demand", extra={"question_id": question_id})
        return {"answer": answer, "solution_steps": steps}

    except Exception as e:
        logger.error("Error generating solution", extra={"question_id": question_id, "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-answer", response_model=AnswerResponse)
async def submit_answer(
    submission: AnswerSubmission,
    math_service: MathAIService = Depends(get_math_service),
    db: SimpleDB = Depends(get_db)
):
    """Validate a submitted answer and provide feedback."""
    try:
        # Get the original question with correct answer
        question = db.get_question(submission.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # If the question doesn't have a stored correct_answer, generate it on-demand
        if not question.correct_answer:
            try:
                generated_answer, generated_steps = math_service.generate_solution_for_question(
                    question.question, question.topic
                )
                # Persist without exposing to frontend here
                question.correct_answer = generated_answer
                question.solution_steps = generated_steps
                try:
                    db.save_question(question)
                except Exception as db_err:
                    print(f"Warning: could not persist generated solution: {db_err}")
            except Exception as gen_err:
                print(f"Warning: solution generation failed during submit: {gen_err}")

        # Validate the answer
        start_time = time.time()
        # Prefer using persisted normalized answers for validation when available
        normalized_from_db = getattr(question, "normalized_answers", None)
        is_correct, confidence, feedback, next_hint = math_service.validate_answer(
            question.correct_answer,
            submission.student_answer,
            submission.attempt_number,
            correct_normalized=normalized_from_db
        )
        time_taken = time.time() - start_time
        
        # Calculate points
        points = math_service.calculate_points(
            is_correct, 
            submission.attempt_number,
            time_taken,
            question.difficulty
        )
        
        # Update student progress
        progress = StudentProgress(
            student_id=submission.student_id or "test_student",  # Provided by client or fallback
            question_id=submission.question_id,
            attempts=submission.attempt_number,
            solved=is_correct,
            last_attempt_at=datetime.now(),
            time_spent=time_taken,
            points_earned=points
        )
        db.update_progress(progress)
        
        # Prepare response
        # Include solution_steps and correct_answer when the student solved it
        response = AnswerResponse(
            is_correct=is_correct,
            confidence=confidence,
            feedback=feedback,
            hint=next_hint if not is_correct else None,
            next_step=question.solution_steps[submission.attempt_number - 1] if not is_correct and question.solution_steps and submission.attempt_number <= len(question.solution_steps) else None,
            points_earned=points,
            time_taken=time_taken,
            solution_steps=question.solution_steps if is_correct else [],
            correct_answer=question.correct_answer if is_correct else None
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/{question_id}/choices")
async def regenerate_choices(
    question_id: str,
    math_service: MathAIService = Depends(get_math_service),
    db: SimpleDB = Depends(get_db)
):
    """Regenerate MCQ choices for an existing question without revealing the correct answer.
    This is useful when initial generation failed to provide options on the frontend.
    """
    try:
        q = db.get_question(question_id)
        if not q:
            raise HTTPException(status_code=404, detail="Question not found")

        # Ensure we have a correct answer; generate if missing
        if not q.correct_answer:
            ans, steps = math_service.generate_solution_for_question(q.question, q.topic)
            q.correct_answer = ans
            q.solution_steps = steps
            try:
                db.save_question(q)
            except Exception as db_error:
                print(f"Warning: Could not persist generated solution while regenerating choices: {db_error}")

        if not q.correct_answer:
            # Cannot create choices without an answer
            return {"choices": []}

        distractors = math_service.generate_distractors(q.correct_answer, q.topic)
        all_choices = math_service.mix_choices(q.correct_answer, distractors)
        # Persist choices on the question
        q.choices = all_choices
        try:
            db.save_question(q)
        except Exception as db_error:
            print(f"Warning: Could not update question with choices: {db_error}")
        return {"choices": all_choices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student-progress/{student_id}")
async def get_progress(student_id: str, db: SimpleDB = Depends(get_db)):
    """Get student's progress and performance statistics."""
    try:
        progress = db.get_student_progress(student_id)
        total_points = sum(p.points_earned for p in progress)
        total_questions = len(progress)
        solved_questions = sum(1 for p in progress if p.solved)
        
        return {
            "total_points": total_points,
            "questions_attempted": total_questions,
            "questions_solved": solved_questions,
            "success_rate": solved_questions / total_questions if total_questions > 0 else 0,
            "detailed_progress": progress
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- Question Quality & Complexity Dashboard APIs ----------------

# Configure path to mathai_ai_models for validators/scorers (same approach as MathAIService)
try:
    import sys
    from pathlib import Path as _Path
    PROJECT_ROOT = _Path(__file__).resolve().parents[3]
    MODEL_PATH = PROJECT_ROOT / "mathai_ai_models"
    if MODEL_PATH.exists() and str(MODEL_PATH) not in sys.path:
        sys.path.insert(0, str(MODEL_PATH))
except Exception as _e:
    print(f"[quality-endpoints] Warning setting model path: {_e}")

try:
    from complexity_scorer import ComplexityScorer  # type: ignore
    from question_validator import QuestionValidator, QuestionQualityScorer  # type: ignore
    _QUALITY_TOOLS_AVAILABLE = True
except Exception as _e:
    print(f"[quality-endpoints] Quality tools unavailable: {_e}")
    _QUALITY_TOOLS_AVAILABLE = False


def _load_all_questions(db: SimpleDB) -> List[QuestionResponse]:
    """Load all stored questions from the DB file."""
    try:
        data_path = db.questions_file
        raw = json.loads(data_path.read_text()) if data_path.exists() else {}
        out: List[QuestionResponse] = []
        for qid, qdata in raw.items():
            try:
                out.append(QuestionResponse(**qdata))
            except Exception as e:
                print(f"[quality-endpoints] Skipping corrupted question {qid}: {e}")
        return out
    except Exception as e:
        print(f"[quality-endpoints] Failed reading questions.json: {e}")
        return []


@router.get("/quality/summary")
async def quality_summary(db: SimpleDB = Depends(get_db)):
    """Aggregate quality and complexity metrics across stored questions.

    Returns a compact summary used by the frontend dashboard. If quality tools
    are unavailable or there are no questions yet, returns a minimal placeholder
    so the UI can still render.
    """
    try:
        questions = _load_all_questions(db)
        if not _QUALITY_TOOLS_AVAILABLE or not questions:
            return {
                "counts": {"total": len(questions), "by_topic": {}},
                "quality": {"overall": 0.0, "clarity": 0.0, "difficulty_calibration": 0.0, "educational_value": 0.0, "engagement": 0.0},
                "complexity": {"avg_score": 0.0, "by_level": {}},
                "issues": {"top": []},
                "samples": []
            }

        # Aggregates
        total = len(questions)
        by_topic: Dict[str, int] = {}
        sum_quality = {"clarity": 0.0, "difficulty_calibration": 0.0, "educational_value": 0.0, "engagement": 0.0, "overall": 0.0}
        level_counts: Dict[str, int] = {}
        issue_counts: Dict[str, int] = {}
        samples: List[Dict[str, Any]] = []

        for q in questions:
            by_topic[q.topic] = by_topic.get(q.topic, 0) + 1

            # Compute complexity
            comp = ComplexityScorer.calculate_complexity(q.question, q.topic)
            level = comp.get("level", "unknown")
            level_counts[level] = level_counts.get(level, 0) + 1

            # Compute quality scores/validation
            scores = QuestionQualityScorer.score_question(q.question, q.correct_answer, q.topic, q.grade)
            for k in sum_quality.keys():
                sum_quality[k] += float(scores.get(k, 0.0))

            validation = QuestionValidator.validate(q.question, q.correct_answer, q.solution_steps or [], q.grade, q.difficulty, q.topic)
            for issue in validation.get("issues", []):
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

            # Keep a few representative samples (up to 10)
            if len(samples) < 10:
                samples.append({
                    "id": q.id,
                    "question": q.question,
                    "topic": q.topic,
                    "grade": q.grade,
                    "difficulty": q.difficulty,
                    "complexity": {
                        "score": comp.get("score", 0),
                        "level": comp.get("level", "unknown"),
                        "normalized": comp.get("normalized", 0.0),
                    },
                    "quality": scores,
                    "issues": validation.get("issues", [])
                })

        avg_quality = {k: (v / total if total else 0.0) for k, v in sum_quality.items()}

        # Top 5 issues by frequency
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_issues_fmt = [{"issue": k, "count": v} for k, v in top_issues]

        return {
            "counts": {"total": total, "by_topic": by_topic},
            "quality": avg_quality,
            "complexity": {"avg_score": sum(c for c in [s.get("quality", {}).get("overall", 0) for s in samples]) if samples else 0.0, "by_level": level_counts},
            "issues": {"top": top_issues_fmt},
            "samples": samples
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality/questions")
async def quality_per_question(
    db: SimpleDB = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum number of questions to return"),
    offset: int = Query(default=0, ge=0, description="Number of questions to skip")
):
    """Return per-question quality + complexity metrics for table views with pagination."""
    try:
        questions = _load_all_questions(db)
        if not _QUALITY_TOOLS_AVAILABLE:
            return {"total": 0, "items": [], "limit": limit, "offset": offset}
        
        total = len(questions)
        paginated_questions = questions[offset:offset + limit]
        
        out: List[Dict[str, Any]] = []
        for q in paginated_questions:
            comp = ComplexityScorer.calculate_complexity(q.question, q.topic)
            scores = QuestionQualityScorer.score_question(q.question, q.correct_answer, q.topic, q.grade)
            validation = QuestionValidator.validate(q.question, q.correct_answer, q.solution_steps or [], q.grade, q.difficulty, q.topic)
            out.append({
                "id": q.id,
                "question": q.question,
                "topic": q.topic,
                "grade": q.grade,
                "difficulty": q.difficulty,
                "complexity": comp,
                "quality": scores,
                "issues": validation.get("issues", [])
            })
        
        logger.info("Quality questions fetched", extra={"total": total, "returned": len(out), "offset": offset, "limit": limit})
        return {"total": total, "items": out, "limit": limit, "offset": offset}
    except Exception as e:
        logger.error("Error fetching quality per question", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
