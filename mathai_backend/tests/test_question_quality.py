"""Test question generation quality and coverage."""

import sys
from pathlib import Path

# Add AI models to path
sys.path.insert(0, str(Path(__file__).parents[2] / "mathai_ai_models"))

from generate_math_question import generate_question
from progressive_hints import generate_progressive_hints
from solution_explainer import enhance_solution_steps
import pytest


class TestQuestionGeneration:
    """Test question generation across topics and difficulties."""
    
    @pytest.mark.parametrize("topic", [
        "algebra", "geometry", "arithmetic", "statistics", 
        "probability", "trigonometry", "number_theory", "calculus"
    ])
    @pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
    def test_generate_question_all_topics(self, topic, difficulty):
        """Test question generation for all topic/difficulty combinations."""
        question, _, _, _ = generate_question(
            grade=8,
            difficulty=difficulty,
            topic=topic
        )
        
        assert question, f"Failed to generate {difficulty} {topic} question"
        assert len(question) > 10, "Question too short"
        assert any(c.isalnum() for c in question), "Question has no content"
    
    def test_question_variety(self):
        """Test that generated questions vary."""
        questions = set()
        for _ in range(10):
            q, _, _, _ = generate_question(8, "medium", "algebra")
            questions.add(q)
        
        # Should have at least 5 unique questions out of 10
        assert len(questions) >= 5, "Not enough question variety"
    
    def test_grade_appropriate_numbers(self):
        """Test that number ranges match grade level."""
        # Grade 3 should have smaller numbers
        q3, _, _, _ = generate_question(3, "easy", "arithmetic")
        nums3 = [int(n) for n in __import__('re').findall(r'\d+', q3)]
        
        # Grade 10 should have larger numbers  
        q10, _, _, _ = generate_question(10, "medium", "arithmetic")
        nums10 = [int(n) for n in __import__('re').findall(r'\d+', q10)]
        
        if nums3 and nums10:
            assert max(nums3) < max(nums10), "Grade scaling not working"


class TestProgressiveHints:
    """Test 3-tier progressive hint system."""
    
    def test_all_three_tiers_generated(self):
        """Test that all 3 hint tiers are generated."""
        question = "Solve for x: 3x + 7 = 22"
        tier1, tier2, tier3 = generate_progressive_hints(question, "algebra")
        
        assert tier1 and len(tier1) > 5, "Tier 1 hint missing"
        assert tier2 and len(tier2) > 5, "Tier 2 hint missing"
        assert tier3 and len(tier3) > 5, "Tier 3 hint missing"
        
        # Tiers should be different
        assert tier1 != tier2 != tier3, "Hints are not progressive"
    
    def test_hints_have_proper_icons(self):
        """Test that hints have the expected emoji markers."""
        question = "Find the area of a circle with radius 5 cm"
        tier1, tier2, tier3 = generate_progressive_hints(question, "geometry")
        
        assert "💡" in tier1, "Tier 1 missing conceptual icon"
        assert "📋" in tier2, "Tier 2 missing strategic icon"
        assert "🔧" in tier3, "Tier 3 missing procedural icon"
    
    @pytest.mark.parametrize("topic", ["algebra", "geometry", "arithmetic"])
    def test_hints_for_different_topics(self, topic):
        """Test hint generation works for all topics."""
        questions = {
            "algebra": "Solve: 2x + 5 = 15",
            "geometry": "Find area of square with side 8 cm",
            "arithmetic": "Calculate: 25 + 17 × 3"
        }
        
        tier1, tier2, tier3 = generate_progressive_hints(questions[topic], topic)
        assert all([tier1, tier2, tier3]), f"Hints failed for {topic}"


class TestSolutionExplainer:
    """Test detailed solution explanations."""
    
    def test_enhance_solution_steps(self):
        """Test that solution steps are enhanced with explanations."""
        steps = [
            "1. Subtract 7 from both sides: 3x = 15",
            "2. Divide both sides by 3: x = 5"
        ]
        
        enhanced = enhance_solution_steps(steps, "Solve: 3x + 7 = 22", "algebra")
        
        assert len(enhanced) == 2, "Wrong number of enhanced steps"
        
        for e in enhanced:
            assert "step" in e, "Missing step content"
            assert "why" in e, "Missing why explanation"
            assert "concept" in e, "Missing concept"
            # warning is optional
    
    def test_explanations_are_meaningful(self):
        """Test that explanations contain useful content."""
        steps = ["1. Distribute: 3(x - 2) = 3x - 6"]
        enhanced = enhance_solution_steps(steps, "Test", "algebra")
        
        why = enhanced[0]["why"]
        concept = enhanced[0]["concept"]
        
        assert len(why) > 10, "Why explanation too short"
        assert len(concept) > 5, "Concept explanation too short"
        assert "💡" in concept, "Concept missing icon"


class TestQuestionQuality:
    """Test question quality metrics."""
    
    def test_questions_are_well_formed(self):
        """Test that questions have proper punctuation."""
        q, _, _, _ = generate_question(7, "medium", "algebra")
        
        # Should end with ? or .
        assert q.endswith(('?', '.')), "Question missing end punctuation"
    
    def test_no_placeholder_text(self):
        """Test that questions don't contain placeholder text."""
        for _ in range(5):
            q, _, _, _ = generate_question(6, "easy", "arithmetic")
            
            bad_words = ['TODO', 'placeholder', 'example', 'XXX']
            assert not any(word in q for word in bad_words), f"Placeholder found in: {q}"
    
    def test_complexity_logging(self, capfd):
        """Test that complexity scoring logs are generated."""
        generate_question(9, "hard", "algebra")
        
        captured = capfd.readouterr()
        assert "[question-gen]" in captured.out, "Missing generation log"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
