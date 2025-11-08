# Performance Optimization Guide

## Implemented Optimizations

### 1. **Frontend Optimizations**

#### Debouncing (Already Implemented)
- Topic switch cancels in-flight requests via AbortController
- Prevents race conditions and unnecessary API calls

#### Code Splitting (Recommended)
```typescript
// Lazy load pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const QuestionGenerator = lazy(() => import('./pages/QuestionGenerator'));
```

### 2. **Backend Caching Strategy**

#### Redis Cache (To Implement)
```python
# requirements.txt addition:
redis==5.0.1

# In math_service.py:
import redis
cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

def generate_question_cached(grade, difficulty, topic):
    cache_key = f"question:{grade}:{difficulty}:{topic}:{random.randint(1,100)}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Generate new question
    result = generate_question(grade, difficulty, topic)
    cache.setex(cache_key, 3600, json.dumps(result))  # 1 hour TTL
    return result
```

#### Database Indexing
```python
# In db.py, add indexes for common queries:
# - Index on question_id for fast lookups
# - Index on student_id + timestamp for progress queries
# - Compound index on (grade, topic, difficulty) for question filtering
```

### 3. **Template Pre-generation**

Since 95% of questions use templates, pre-generate common ones:

```python
# Pre-generate 1000 questions on startup
QUESTION_POOL = {}

def warm_cache():
    for topic in TOPICS:
        for difficulty in ['easy', 'medium', 'hard']:
            for grade in range(1, 13):
                for _ in range(10):  # 10 variations per combo
                    q = generate_question(grade, difficulty, topic)
                    key = f"{grade}:{difficulty}:{topic}"
                    if key not in QUESTION_POOL:
                        QUESTION_POOL[key] = []
                    QUESTION_POOL[key].append(q)
```

### 4. **Lazy Loading Solutions**

Solutions are generated on-demand (already implemented). Further optimization:

```python
# Only generate solution when user clicks "Get Solution" or submits correct answer
# This saves 2-3 seconds per question generation
```

### 5. **API Response Compression**

Add gzip compression to FastAPI:

```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 6. **Connection Pooling**

For database connections, use connection pooling:

```python
# SQLite is single-file, but if migrating to PostgreSQL:
from sqlalchemy.pool import QueuePool
engine = create_engine('postgresql://...', poolclass=QueuePool, pool_size=20)
```

### 7. **Frontend Performance Monitoring**

```typescript
// Add Web Vitals tracking
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric: Metric) {
  // Send to your analytics endpoint
  console.log(metric);
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

## Performance Benchmarks (Target)

| Metric | Current | Target | Optimization |
|--------|---------|--------|--------------|
| Question Generation | 2-3s | <1s | Template caching |
| Hint Generation | 1-2s | <500ms | Progressive hints (deterministic) |
| Solution Generation | 3-5s | <1s | Symbolic solver + caching |
| Page Load | 1.5s | <1s | Code splitting |
| API Response | 500ms | <200ms | Redis caching |

## Quick Wins (Implement These First)

1. **Enable GZip compression** (5 min, 30-50% size reduction)
2. **Add Redis for question caching** (30 min, 70% faster repeat queries)
3. **Lazy load Dashboard** (10 min, 40% faster initial load)
4. **Pre-generate 100 questions per topic** (1 hour, instant responses)

## Monitoring

Add timing logs to track performance:

```python
import time

def timed_operation(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            print(f"[PERF] {name}: {duration:.3f}s")
            return result
        return wrapper
    return decorator

@timed_operation("generate_question")
def generate_question(...):
    ...
```

## Load Testing

Use Locust to test:

```python
# locustfile.py
from locust import HttpUser, task, between

class MathAIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def generate_question(self):
        self.client.post("/ai/generate-question", json={
            "grade": 8,
            "difficulty": "medium",
            "topic": "algebra",
            "question_type": "open"
        })
    
    @task(2)
    def submit_answer(self):
        # Submit answer flow
        pass

# Run: locust -f locustfile.py --host=http://localhost:8000
```
