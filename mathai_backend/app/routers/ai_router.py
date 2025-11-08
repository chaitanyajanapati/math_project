from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import time

from app.models.questions import (
    QuestionRequest, QuestionResponse, AnswerSubmission,
    AnswerResponse, StudentProgress
)
from app.utils.math_service import MathAIService
from app.utils.db import SimpleDB

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
    print(f"Received question request: grade={req.grade}, difficulty={req.difficulty}, topic={req.topic}")
    try:
        question_text = math_service.generate_question_only(req.grade, req.difficulty, req.topic)

        # Always generate solution (needed for validation and display after correct answer)
        answer, solution_steps = math_service.generate_solution_for_question(question_text, req.topic)
        
        # For MCQ, also generate distractors
        all_choices = None
        if req.question_type == "mcq":
            distractors = math_service.generate_distractors(answer, req.topic) if answer else []
            all_choices = math_service.mix_choices(answer, distractors) if answer else None

        question_response = QuestionResponse(
            question=question_text,
            grade=req.grade,
            difficulty=req.difficulty,
            topic=req.topic,
            correct_answer=answer or "",
            normalized_answers=math_service.normalize_answer(answer) if answer else [],
            choices=all_choices,
            hints=[],
            solution_steps=solution_steps or []
        )

        print(f"Created question response with question: {question_text} | type={req.question_type} | choices={all_choices} | steps={len(solution_steps) if solution_steps else 0}")

        try:
            db.save_question(question_response)
        except Exception as db_error:
            print(f"Warning: Could not save question to database: {str(db_error)}")

        # Hide correct_answer, normalized_answers, and solution_steps before returning to frontend
        safe_response = question_response.model_copy()
        safe_response.correct_answer = ""
        safe_response.normalized_answers = []
        safe_response.solution_steps = []  # Hide steps initially
        return safe_response

    except Exception as e:
        print(f"Error in generate_question_api: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/{question_id}/hint")
async def generate_hint_api(
    question_id: str,
    math_service: MathAIService = Depends(get_math_service),
    db: SimpleDB = Depends(get_db)
):
    """Generate a hint for a stored question on-demand."""
    try:
        q = db.get_question(question_id)
        if not q:
            raise HTTPException(status_code=404, detail="Question not found")

        hint = math_service.generate_hint_for_question(q.question, q.topic)

        # Persist hint to DB
        q.hints = [hint]
        try:
            db.save_question(q)
        except Exception as db_error:
            print(f"Warning: Could not update question with hint: {db_error}")

        return {"hint": hint}

    except Exception as e:
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
            print(f"Returning stored solution for question {question_id}")
            return {"answer": q.correct_answer, "solution_steps": q.solution_steps}
        
        # Otherwise, generate solution on-demand
        answer, steps = math_service.generate_solution_for_question(q.question, q.topic)

        # Normalize answer(s) and store variants for robust validation
        print(f"Pre-normalizing answer: {answer}")
        normalized_list = math_service.normalize_answer(answer) if answer else []

        # Persist solution to DB (store correct answer and steps)
        q.correct_answer = answer
        q.normalized_answers = normalized_list
        q.solution_steps = steps
        try:
            db.save_question(q)
        except Exception as db_error:
            print(f"Warning: Could not update question with solution: {db_error}")

        # Return the solution (answer + steps). If you don't want to expose the answer to the frontend,
        # remove it here and only return steps.
        return {"answer": answer, "solution_steps": steps}

    except Exception as e:
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
            time_taken
        )
        
        # Update student progress
        progress = StudentProgress(
            student_id="test_student",  # TODO: Implement proper student authentication
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
