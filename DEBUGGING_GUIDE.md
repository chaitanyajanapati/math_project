# Debugging Guide for Current Issues

## Issues to Test

### 1. Solutions Not Showing Sometimes
**Symptoms**: Solution steps don't appear after clicking "Get Solution"

**What to check**:
1. Open browser console (F12) and look for:
   - "Fetching solution for question: [id]"
   - "Solution response: {data}"
2. Check backend terminal for:
   - "Returning stored solution for question [id]"
   - Any error messages

**Possible causes**:
- Question ID not being set properly (check console log: "Generate response:")
- Backend endpoint returning empty solution_steps array
- Network error (check Network tab in browser DevTools)

### 2. MCQ Options Not Showing
**Symptoms**: Multiple choice options don't appear even when MCQ mode is selected

**What to check**:
1. Open browser console and generate a question in MCQ mode, look for:
   - "Generate response: {question, choices, ...}"
   - "Choices set to: [array of choices]"
2. Check backend terminal for:
   - "Received question request: ... question_type=mcq"
   - "Created question response with ... choices=[...] ..."

**Possible causes**:
- Frontend not sending `question_type: "mcq"` parameter
- Backend not generating distractors (check if answer is generated first)
- Response not including choices field

## How to Test

### Test MCQ Mode:
1. Refresh the frontend (http://localhost:5173)
2. Open Browser DevTools Console (F12 → Console tab)
3. Select "Multiple Choice" from Question Type dropdown
4. Click "Generate Question"
5. Check console logs for "Generate response:" and "Choices set to:"
6. Verify if choice buttons appear below the question

### Test Solution Display:
1. Generate any question (open or MCQ)
2. Click "Get Solution" button
3. Check console logs for "Fetching solution" and "Solution response:"
4. Verify if solution steps appear in the right panel

## Quick Fixes Applied

### 1. Fixed Duplicate Numbering in Solution Steps
**Location**: `/mathai_frontend/src/pages/QuestionGenerator.tsx` line 329
**Change**: Removed `<ol>` list styling since backend already adds "1. ", "2. " prefixes
**Result**: Solution steps now show "1. Step one" instead of "1. 1. Step one"

### 2. Added Debug Logging
**Locations**:
- Frontend: Lines 55-57, 77-79 in QuestionGenerator.tsx
- Backend: Line 28 in ai_router.py

**What it logs**:
- Frontend: Full generate response, choices array, solution response
- Backend: question_type parameter value

## Next Steps

1. **Test with browser console open** and share the console output
2. If choices still don't show:
   - Check if `res.data.choices` is null/undefined in console
   - Check backend terminal for "question_type=mcq"
3. If solutions don't show:
   - Check if `r.data.solution_steps` is empty array in console
   - Check backend terminal for solution endpoint logs

## Backend Endpoints to Verify

```bash
# Test generate question with MCQ
curl -X POST http://localhost:8000/api/generate-question \
  -H "Content-Type: application/json" \
  -d '{
    "grade": 8,
    "difficulty": "medium",
    "topic": "algebra",
    "question_type": "mcq"
  }'

# Test get solution (replace QUESTION_ID)
curl -X POST http://localhost:8000/api/questions/QUESTION_ID/solution
```

## Common Issues

### Issue: "Error connecting to backend"
**Solution**: Make sure FastAPI is running on port 8000
```bash
cd /home/jc/math_project/mathai_backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Issue: Frontend not loading changes
**Solution**: Vite should auto-reload, but if not:
1. Stop the frontend (Ctrl+C)
2. Clear browser cache
3. Restart: `npm run dev`

### Issue: Backend changes not applying
**Solution**: uvicorn should auto-reload with `--reload` flag
- Check terminal for "Reloading..." message after file changes
- If not reloading, restart manually
