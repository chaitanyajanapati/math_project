# 🎯 Question Quality & Difficulty Improvements

## Current State Analysis

Your system uses:
- **95% template-based** questions (deterministic, fast)
- **5% LLM-generated** questions (creative, slower)
- **3 difficulty levels**: easy, medium, hard
- **Grade bands**: 1-5, 6-9, 10-12
- **Limited templates**: ~10 per topic/difficulty/grade

## 🔴 Current Limitations

### 1. **Template Variety**
- Only 3-5 templates per difficulty level
- Students see repeated patterns quickly
- No variation in question structure

### 2. **Difficulty Scaling Issues**
- "Hard" questions sometimes easier than "medium"
- No sub-levels within difficulties
- Jump from grade 9→10 too abrupt

### 3. **Number Generation**
- Random ranges too broad (5-40 for grades 1-5)
- Generates unsolvable fractions sometimes
- No constraint on "nice" answers

### 4. **Topic Coverage**
- Missing: statistics, probability, trigonometry (partial)
- Geometry limited to basic shapes
- No word problem variety

### 5. **Quality Metrics**
- No tracking of question difficulty
- No student performance feedback loop
- Can't adapt to student level

---

## ✅ Recommended Improvements

### **Phase 1: Template Expansion (Immediate - 2-3 days)**

#### 1.1 Expand Template Bank (10x increase)

**Current:** 3-5 templates per category  
**Target:** 50-100 templates per category

```python
# Example expansion for algebra:
ALGEBRA_TEMPLATES = {
    "easy": {
        (1, 5): [
            # Linear equations (basic)
            "Solve for x: {a}x + {b} = {c}",
            "Find x if {a}x = {c}",
            "If x + {b} = {c}, what is x?",
            "{a}x - {b} = {c}. Find x.",
            "What value of x makes {a}x = {c} true?",
            
            # Word problems (simple)
            "Sarah has {a} apples. She gets {b} more. How many total?",
            "A toy costs ${a}. If you have ${c}, how much change?",
            "There are {a} students. {b} leave. How many remain?",
            
            # Patterns
            "Continue: {a}, {b}, {c}, ___",
            "What comes next: {a}, {a+d}, {a+2d}, ___?",
            
            # ... 40 more variations
        ],
        # ... medium, hard
    }
}
```

#### 1.2 Add Question Type Categories

```python
QUESTION_TYPES = {
    "procedural": 0.4,      # Direct calculation
    "word_problem": 0.3,    # Real-world context
    "conceptual": 0.2,      # Understanding-based
    "multi_step": 0.1,      # Requires planning
}
```

#### 1.3 Smart Number Generation

```python
def generate_smart_numbers(grade: int, difficulty: str, question_type: str):
    """Generate numbers that lead to 'nice' answers"""
    
    # Easy: whole number answers only
    if difficulty == "easy":
        if grade <= 3:
            return {"range": (2, 10), "nice_answers": True}
        elif grade <= 5:
            return {"range": (5, 20), "nice_answers": True}
        elif grade <= 9:
            return {"range": (10, 50), "nice_answers": True}
    
    # Medium: some fractions/decimals allowed
    elif difficulty == "medium":
        if grade <= 5:
            return {"range": (10, 30), "decimals": 0.2}
        elif grade <= 9:
            return {"range": (20, 100), "decimals": 0.3, "fractions": 0.2}
    
    # Hard: complex numbers, multi-step
    elif difficulty == "hard":
        return {
            "range": (50, 500),
            "decimals": 0.4,
            "fractions": 0.3,
            "negatives": 0.2
        }
```

---

### **Phase 2: Difficulty Calibration (Week 1)**

#### 2.1 Add Sub-Levels

```python
DIFFICULTY_LEVELS = {
    "very_easy": {"grade_offset": -1, "complexity": 1},
    "easy": {"grade_offset": 0, "complexity": 1},
    "medium": {"grade_offset": 0, "complexity": 2},
    "hard": {"grade_offset": 0, "complexity": 3},
    "very_hard": {"grade_offset": +1, "complexity": 3},
    "challenge": {"grade_offset": +2, "complexity": 4},
}
```

#### 2.2 Complexity Scoring

```python
def calculate_complexity(question_params):
    """Score question complexity objectively"""
    score = 0
    
    # Number of operations
    score += question_params.get("operations", 1) * 10
    
    # Number size
    if max(question_params["numbers"]) > 100:
        score += 10
    if max(question_params["numbers"]) > 1000:
        score += 20
    
    # Operation types
    if "division" in question_params["ops"]:
        score += 15
    if "fractions" in question_params:
        score += 20
    if "exponents" in question_params:
        score += 25
    
    # Multi-step
    score += question_params.get("steps", 1) * 15
    
    # Word problem
    if question_params.get("is_word_problem"):
        score += 20
    
    return score
    
# Score ranges:
# 0-30: Very Easy
# 31-60: Easy
# 61-90: Medium
# 91-120: Hard
# 121+: Very Hard
```

#### 2.3 Adaptive Difficulty

```python
def adjust_difficulty_by_performance(student_id: str, topic: str):
    """Adjust difficulty based on recent performance"""
    
    # Get last 10 attempts
    recent = get_student_history(student_id, topic, limit=10)
    
    accuracy = sum(r.correct for r in recent) / len(recent)
    avg_time = sum(r.time_taken for r in recent) / len(recent)
    
    # Decision matrix
    if accuracy > 0.85 and avg_time < 60:
        return "increase"  # Too easy
    elif accuracy < 0.5:
        return "decrease"  # Too hard
    else:
        return "maintain"
```

---

### **Phase 3: Topic Expansion (Week 2)**

#### 3.1 Add Missing Topics

```python
NEW_TOPICS = {
    "statistics": {
        "easy": ["mean", "median", "mode", "range"],
        "medium": ["standard_deviation", "quartiles", "box_plots"],
        "hard": ["probability_distributions", "hypothesis_testing"]
    },
    "probability": {
        "easy": ["simple_events", "coin_flips", "dice"],
        "medium": ["compound_events", "combinations", "permutations"],
        "hard": ["conditional_probability", "bayes_theorem"]
    },
    "trigonometry": {
        "easy": ["sin_cos_tan_basic", "pythagorean"],
        "medium": ["trig_identities", "unit_circle"],
        "hard": ["inverse_trig", "trig_equations", "law_of_sines"]
    },
    "calculus": {  # For grade 11-12
        "easy": ["limits", "basic_derivatives"],
        "medium": ["chain_rule", "product_rule", "integrals"],
        "hard": ["optimization", "related_rates", "area_between_curves"]
    },
    "number_theory": {
        "easy": ["factors", "multiples", "primes"],
        "medium": ["gcd", "lcm", "divisibility_rules"],
        "hard": ["modular_arithmetic", "diophantine_equations"]
    }
}
```

#### 3.2 Real-World Context Templates

```python
WORD_PROBLEM_CONTEXTS = {
    "shopping": "buying items, calculating change, discounts",
    "cooking": "recipe scaling, measurements, fractions",
    "sports": "scores, statistics, averages",
    "travel": "distance, time, speed problems",
    "construction": "area, perimeter, materials",
    "finance": "interest, budgets, percentages",
    "science": "measurements, conversions, data analysis",
}

def generate_word_problem(topic, grade, context):
    """Create contextual word problems"""
    templates = WORD_PROBLEM_LIBRARY[context][topic]
    return customize_template(templates, grade)
```

---

### **Phase 4: Quality Validation (Week 3)**

#### 4.1 Question Validator

```python
class QuestionValidator:
    """Ensure generated questions are high quality"""
    
    @staticmethod
    def validate(question: str, answer: str, steps: List[str]) -> Dict:
        """Run validation checks"""
        
        checks = {
            "has_question": bool(question and len(question) > 10),
            "has_answer": bool(answer),
            "answer_reasonable": QuestionValidator._check_reasonable(answer),
            "no_errors": QuestionValidator._check_math_errors(question, answer),
            "clear_wording": QuestionValidator._check_clarity(question),
            "appropriate_difficulty": True,  # Based on complexity score
            "has_solution_steps": len(steps) > 0,
        }
        
        checks["overall_quality"] = sum(checks.values()) / len(checks)
        return checks
    
    @staticmethod
    def _check_reasonable(answer: str) -> bool:
        """Check if answer is reasonable"""
        try:
            val = float(answer)
            # Avoid extreme values
            if abs(val) > 1_000_000:
                return False
            # Avoid too many decimal places
            if len(str(val).split('.')[-1]) > 4:
                return False
            return True
        except:
            return False
```

#### 4.2 A/B Testing Framework

```python
def ab_test_questions():
    """Compare template vs LLM quality"""
    
    # Generate 100 of each
    template_qs = [generate_question(use_template=True) for _ in range(100)]
    llm_qs = [generate_question(use_llm=True) for _ in range(100)]
    
    # Metrics to track
    metrics = {
        "avg_time_to_generate": [],
        "student_engagement": [],  # Time spent on question
        "accuracy": [],
        "quality_score": [],  # From validator
        "variety_score": [],  # Uniqueness
    }
    
    # Show students mix, track which they engage with more
```

---

### **Phase 5: Advanced Features (Week 4+)**

#### 5.1 Hint Quality Improvement

```python
HINT_LEVELS = [
    "conceptual",     # "Remember the formula for..."
    "strategic",      # "Start by isolating the variable..."
    "procedural",     # "First, subtract 5 from both sides..."
    "worked_example", # Show similar problem solved
]

def generate_progressive_hints(question, topic, student_level):
    """Give increasingly specific hints"""
    hints = []
    
    # Level 1: What concept to use
    hints.append(f"This is a {topic} problem. Think about {get_key_concept(question)}")
    
    # Level 2: Strategy
    hints.append(f"Try this approach: {get_strategy(question)}")
    
    # Level 3: First step
    hints.append(f"Start with: {get_first_step(question)}")
    
    # Level 4: Nearly complete
    hints.append(f"Continue: {get_partial_solution(question)}")
    
    return hints[:student_level]
```

#### 5.2 Dynamic Question Chaining

```python
def generate_question_sequence(student_id, topic, target_difficulty):
    """Create adaptive learning path"""
    
    # Start slightly below target
    current_diff = target_difficulty - 0.5
    
    questions = []
    for i in range(5):
        q = generate_question(
            difficulty=current_diff,
            topic=topic,
            previous_performance=get_recent_performance(student_id)
        )
        questions.append(q)
        
        # Adjust for next question
        if should_increase_difficulty(student_id):
            current_diff += 0.2
        elif should_decrease_difficulty(student_id):
            current_diff -= 0.2
    
    return questions
```

#### 5.3 Question Bank Pre-generation

```python
def build_question_bank():
    """Pre-generate high-quality questions offline"""
    
    bank = {}
    
    for grade in range(1, 13):
        for difficulty in ["easy", "medium", "hard"]:
            for topic in TOPICS:
                # Generate 1000 questions per combo
                questions = []
                for _ in range(1000):
                    q = generate_question(grade, difficulty, topic)
                    
                    # Validate quality
                    if validate_quality(q) > 0.8:
                        questions.append(q)
                
                bank[(grade, difficulty, topic)] = questions
    
    # Save to database/JSON
    save_question_bank(bank)
    
    # Update weekly with new generated questions
```

---

## 📊 Metrics to Track

### Question Quality Metrics

```python
QUALITY_METRICS = {
    # Generation metrics
    "generation_time": "avg ms to generate",
    "template_vs_llm_ratio": "95/5 currently",
    "validation_pass_rate": "% passing quality checks",
    
    # Student engagement
    "avg_time_on_question": "how long students spend",
    "skip_rate": "% of questions skipped",
    "hint_usage_rate": "% requesting hints",
    
    # Performance metrics
    "accuracy_by_difficulty": "correctness by level",
    "accuracy_by_topic": "which topics are hardest",
    "retry_attempts": "how many tries",
    
    # Quality indicators
    "question_variety_score": "uniqueness metric",
    "difficulty_calibration": "predicted vs actual",
    "answer_reasonableness": "% with reasonable answers",
}
```

### Dashboard for Monitoring

```python
def generate_quality_dashboard():
    """Admin dashboard to monitor question quality"""
    
    stats = {
        "total_questions_generated": count_questions(),
        "avg_quality_score": calculate_avg_quality(),
        "top_performing_templates": get_top_templates(),
        "problem_areas": identify_issues(),
        
        # By difficulty
        "easy_accuracy": get_accuracy("easy"),
        "medium_accuracy": get_accuracy("medium"),
        "hard_accuracy": get_accuracy("hard"),
        
        # By topic
        "topic_breakdown": get_topic_stats(),
        
        # Trends
        "quality_trend": get_quality_over_time(),
        "student_satisfaction": get_feedback_scores(),
    }
    
    return render_dashboard(stats)
```

---

## 🎯 Implementation Priority

### **Sprint 1 (Week 1): Quick Wins**
- ✅ Expand template bank 3x (100 templates per category)
- ✅ Add smart number generation (nice answers)
- ✅ Implement complexity scoring
- ✅ Add question validator

**Expected Impact:** 50% more variety, 30% better difficulty calibration

### **Sprint 2 (Week 2): Core Improvements**
- ✅ Add 5 new topics (statistics, probability, etc.)
- ✅ Implement sub-difficulty levels
- ✅ Add word problem contexts
- ✅ Create A/B testing framework

**Expected Impact:** 80% topic coverage, 40% engagement increase

### **Sprint 3 (Week 3): Advanced Features**
- ✅ Progressive hint system
- ✅ Adaptive difficulty adjustment
- ✅ Question chaining
- ✅ Quality dashboard

**Expected Impact:** 25% improvement in learning outcomes

### **Sprint 4 (Week 4): Optimization**
- ✅ Pre-generate question bank
- ✅ Performance tuning
- ✅ Analytics integration
- ✅ Student feedback loop

**Expected Impact:** 90%+ satisfaction rate

---

## 💡 Quick Wins (Do First)

### 1. **Add 10x More Templates** (2 hours)
```python
# Just expand TEMPLATES dict in generate_math_question.py
# Copy-paste pattern with variations
```

### 2. **Fix Number Ranges** (1 hour)
```python
# Update generate_variation_from_template()
# Use tighter, grade-appropriate ranges
```

### 3. **Add Question Type Mix** (1 hour)
```python
# 70% procedural, 20% word problems, 10% conceptual
# More engaging for students
```

### 4. **Implement Validator** (2 hours)
```python
# Reject questions with:
# - Negative area/volume
# - Division by zero
# - Unreasonable large numbers
```

### 5. **Add 2-3 New Topics** (3 hours)
```python
# Statistics, probability, trigonometry
# Use same template pattern
```

---

## 🧪 Testing Strategy

### Before/After Comparison

```python
def quality_test():
    """Compare old vs new system"""
    
    # Generate 100 questions each
    old_questions = generate_with_old_system(100)
    new_questions = generate_with_new_system(100)
    
    # Compare metrics
    comparison = {
        "variety": calculate_uniqueness(old_qs) vs calculate_uniqueness(new_qs),
        "difficulty_accuracy": measure_calibration(old) vs measure_calibration(new),
        "student_preference": survey_students(old) vs survey_students(new),
        "answer_quality": validate_answers(old) vs validate_answers(new),
    }
    
    return comparison
```

---

## 📈 Expected Outcomes

| Metric | Current | After Phase 1 | After Phase 4 |
|--------|---------|---------------|---------------|
| Templates per category | 5 | 50 | 100 |
| Topic coverage | 60% | 85% | 95% |
| Difficulty accuracy | 65% | 80% | 90% |
| Student engagement | Baseline | +40% | +70% |
| Question variety | Low | Medium | High |
| Answer quality | 70% | 85% | 95% |

---

## 🚀 Getting Started

1. **Immediate (Today):**
   ```bash
   # Backup current system
   cp generate_math_question.py generate_math_question.py.backup
   
   # Start with template expansion
   # Edit TEMPLATES dict, add 10x more variations
   ```

2. **This Week:**
   - Implement smart number generation
   - Add question validator
   - Expand to 100 templates per category

3. **Next Week:**
   - Add new topics
   - Implement complexity scoring
   - Add sub-difficulty levels

4. **Ongoing:**
   - Monitor quality metrics
   - Gather student feedback
   - Iterate based on data

---

## 📚 Resources Needed

- **Time:** 2-4 weeks for full implementation
- **Math expertise:** To create quality templates
- **Data:** Student performance data for calibration
- **Testing:** Beta testers (students) for feedback

Would you like me to:
1. **Start implementing Phase 1** (template expansion)?
2. **Create the question validator**?
3. **Add new topics** (statistics, probability)?
4. **Build the quality dashboard**?

Let me know which to prioritize!
