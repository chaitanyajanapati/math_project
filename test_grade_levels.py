#!/usr/bin/env python3
"""
Test script to demonstrate grade-appropriate question generation
"""

import sys
from pathlib import Path

# Add AI models path
PROJECT_ROOT = Path(__file__).parent
MODEL_PATH = PROJECT_ROOT / "mathai_ai_models"
sys.path.insert(0, str(MODEL_PATH))

from generate_math_question import generate_question

def test_grade_scaling():
    """Test that questions scale appropriately with grade level"""
    
    print("=" * 70)
    print("TESTING GRADE-APPROPRIATE QUESTION GENERATION")
    print("=" * 70)
    print()
    
    test_cases = [
        # (grade, difficulty, topic, description)
        (3, 'easy', 'arithmetic', 'Elementary: Simple addition/subtraction'),
        (5, 'medium', 'arithmetic', 'Elementary: Multi-digit operations'),
        (7, 'easy', 'algebra', 'Middle School: Basic equations'),
        (8, 'medium', 'algebra', 'Middle School: Multi-step equations'),
        (9, 'medium', 'geometry', 'Middle School: Volume & surface area'),
        (10, 'hard', 'geometry', 'High School: Advanced geometry'),
        (11, 'hard', 'algebra', 'High School: Quadratic equations'),
        (12, 'hard', 'algebra', 'High School: Systems of equations'),
    ]
    
    for grade, difficulty, topic, description in test_cases:
        print(f"📚 {description}")
        print(f"   Grade {grade} | {difficulty.capitalize()} | {topic.capitalize()}")
        print(f"   ", end="", flush=True)
        
        try:
            question, _, _, _ = generate_question(grade, difficulty, topic)
            print(f"✓ {question}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print()
    
    print("=" * 70)
    print("Test complete! Questions should progressively increase in complexity.")
    print("=" * 70)

if __name__ == "__main__":
    test_grade_scaling()
