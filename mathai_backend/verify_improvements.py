"""
Verification script for Phase 1 improvements.
Tests authentication, database, error handling, and validation.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_database():
    """Test database initialization."""
    print("✓ Testing Database Initialization...")
    try:
        from app.database import init_db, engine
        await init_db()
        print("  ✓ Database initialized successfully")
        print(f"  ✓ Database location: data/mathai.db")
        return True
    except Exception as e:
        print(f"  ✗ Database initialization failed: {e}")
        return False


async def test_models():
    """Test database models."""
    print("\n✓ Testing Database Models...")
    try:
        from app.models.db_models import User, Question, Progress
        from app.database import AsyncSessionLocal
        
        # Create test user with unique email
        async with AsyncSessionLocal() as session:
            from datetime import datetime
            import random
            unique_email = f"test{random.randint(1000,9999)}@example.com"
            
            test_user = User(
                email=unique_email,
                username="testuser",
                hashed_password="hashedpassword123",
                grade=8
            )
            session.add(test_user)
            await session.commit()
            print(f"  ✓ Created test user: {test_user.email}")
            
            # Query back
            from sqlalchemy import select
            result = await session.execute(select(User).where(User.email == unique_email))
            user = result.scalar_one_or_none()
            if user:
                print(f"  ✓ Retrieved user: {user.username}")
            
        return True
    except Exception as e:
        print(f"  ✗ Model test failed: {e}")
        return False


def test_auth_utils():
    """Test authentication utilities."""
    print("\n✓ Testing Authentication Utilities...")
    try:
        from app.utils.auth import get_password_hash, verify_password, create_access_token
        
        # Test password hashing (keep it under 72 bytes)
        password = "test123"
        hashed = get_password_hash(password)
        print(f"  ✓ Password hashed successfully")
        
        # Test password verification
        if verify_password(password, hashed):
            print(f"  ✓ Password verification works")
        else:
            print(f"  ✗ Password verification failed")
            return False
        
        # Test JWT token creation
        token = create_access_token({"sub": "test@example.com", "user_id": "123"})
        print(f"  ✓ JWT token created: {token[:20]}...")
        
        return True
    except Exception as e:
        print(f"  ✗ Auth utils test failed: {e}")
        return False


def test_validation():
    """Test input validation."""
    print("\n✓ Testing Input Validation...")
    try:
        from app.models.questions import QuestionRequest, AnswerSubmission, DifficultyLevel, MathTopic
        from pydantic import ValidationError
        
        # Valid request
        valid_request = QuestionRequest(
            grade=8,
            difficulty=DifficultyLevel.MEDIUM,
            topic=MathTopic.ALGEBRA
        )
        print(f"  ✓ Valid question request accepted")
        
        # Invalid grade (should fail)
        try:
            invalid_request = QuestionRequest(
                grade=15,  # Out of range
                difficulty=DifficultyLevel.MEDIUM,
                topic=MathTopic.ALGEBRA
            )
            print(f"  ✗ Invalid grade not caught")
            return False
        except ValidationError:
            print(f"  ✓ Invalid grade rejected correctly")
        
        # Valid answer submission
        valid_submission = AnswerSubmission(
            question_id="550e8400-e29b-41d4-a716-446655440000",
            student_answer="42",
            attempt_number=1
        )
        print(f"  ✓ Valid answer submission accepted")
        
        return True
    except Exception as e:
        print(f"  ✗ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exceptions():
    """Test custom exceptions."""
    print("\n✓ Testing Custom Exceptions...")
    try:
        from app.exceptions import (
            QuestionNotFoundError, ValidationError,
            http_exception_from_mathai_error
        )
        
        # Create exception
        error = QuestionNotFoundError("test-id")
        print(f"  ✓ Custom exception created: {error.message}")
        
        # Convert to HTTP exception
        http_exc = http_exception_from_mathai_error(error)
        print(f"  ✓ HTTP exception created with status: {http_exc.status_code}")
        
        return True
    except Exception as e:
        print(f"  ✗ Exception test failed: {e}")
        return False


def test_env_files():
    """Test environment configuration files."""
    print("\n✓ Testing Environment Configuration...")
    try:
        backend_env = Path(".env.example")
        if backend_env.exists():
            print(f"  ✓ Backend .env.example exists")
        else:
            print(f"  ✗ Backend .env.example missing")
            return False
        
        frontend_env = Path("../mathai_frontend/.env.example")
        if frontend_env.exists():
            print(f"  ✓ Frontend .env.example exists")
        else:
            print(f"  ⚠ Frontend .env.example missing (expected in frontend directory)")
        
        return True
    except Exception as e:
        print(f"  ✗ Environment file test failed: {e}")
        return False


async def main():
    """Run all verification tests."""
    print("="*60)
    print("PHASE 1 IMPROVEMENTS VERIFICATION")
    print("="*60)
    
    results = []
    
    # Run async tests
    results.append(await test_database())
    results.append(await test_models())
    
    # Run sync tests
    results.append(test_auth_utils())
    results.append(test_validation())
    results.append(test_exceptions())
    results.append(test_env_files())
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
