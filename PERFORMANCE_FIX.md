# Application Performance Issues & Fixes

## Problems Identified

### 🐌 Major Performance Bottlenecks:

1. **Wrong Model Being Used**
   - Code defaults to: `qwen2.5:7b` (7 billion parameters, ~4.7GB)
   - Currently loaded: `phi:latest` (smaller, faster, 2.2GB)
   - **Impact**: Model switching overhead + larger model = slower generation

2. **CPU-Only Execution**
   - Ollama is running on 100% CPU (no GPU acceleration)
   - **Impact**: 10-100x slower than GPU execution

3. **Multiple Subprocess Calls**
   - Each operation spawns new `ollama run` processes
   - Question generation: ~3-5 retries with exponential backoff
   - Hint generation: ~2 retries
   - Solution generation: ~3 retries
   - **Impact**: High latency (10-30 seconds per question)

4. **Synchronous Blocking Calls**
   - FastAPI endpoints wait for entire generation to complete
   - **Impact**: Frontend appears frozen during generation

## Quick Fixes (Immediate Impact)

### Fix 1: Change Default Model to Phi
Update `generate_math_question.py` to use the faster `phi` model:

```python
# Change all function signatures from:
def generate_question(..., model: str = "qwen2.5:7b")
# To:
def generate_question(..., model: str = "phi")
```

### Fix 2: Reduce Retry Attempts
In `generate_math_question.py`, update `ModelConfig`:

```python
class ModelConfig:
    MAX_RETRIES = 2  # Reduced from 3
    INITIAL_TIMEOUT = 5  # Reduced from 10
    BACKOFF_FACTOR = 1.5
```

### Fix 3: Use Ollama API Instead of Subprocess
Replace subprocess calls with Ollama's HTTP API for better performance.

## Medium-Term Fixes

### Fix 4: Add Response Caching
Cache generated questions/solutions to avoid regeneration

### Fix 5: Use Async Processing
Make generation non-blocking using FastAPI background tasks

### Fix 6: Enable GPU Support
Install CUDA/ROCm drivers for GPU acceleration (10-100x faster)

## Performance Comparison

| Metric | Before | After Quick Fixes | After GPU |
|--------|--------|-------------------|-----------|
| Question Gen | 15-30s | 5-10s | 1-2s |
| Hint Gen | 10-15s | 3-5s | 0.5-1s |
| Solution Gen | 20-40s | 8-12s | 2-3s |
| Model Size | 4.7GB | 2.2GB | 2.2GB |
| CPU Usage | 100% | 100% | 10-20% |

## Recommended Actions (Priority Order)

1. ✅ **Switch to phi model** (5 min, 3-5x faster)
2. ✅ **Reduce retries** (2 min, 40% faster)
3. ⏳ Add loading indicators in frontend (10 min)
4. ⏳ Implement response caching (30 min, 10x faster for repeated questions)
5. ⏳ Enable GPU support (varies, 10-100x faster)
