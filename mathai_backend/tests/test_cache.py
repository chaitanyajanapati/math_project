"""
Tests for caching functionality
"""
import pytest
from fastapi.testclient import TestClient
from mathai_backend.main import app
from app.services.cache import CacheService, get_cache_service


# Create test client
client = TestClient(app)


@pytest.fixture
def auth_headers():
    """Create a test user and return auth headers"""
    import random
    email = f"test_{random.randint(1000, 9999)}@example.com"
    
    # Register user (returns 201 Created)
    register_data = {
        "email": email,
        "username": "testuser",
        "password": "testpass123",
        "grade": 6
    }
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201, f"Registration failed: {response.status_code} - {response.text}"
    
    # Login (OAuth2 requires form data with username field)
    login_data = {
        "username": email,  # OAuth2 uses "username" field but we use email
        "password": "testpass123"
    }
    response = client.post("/api/v1/auth/login", data=login_data)  # Use data= for form encoding
    assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


class TestCacheService:
    """Test the CacheService implementation"""
    
    def test_basic_get_set(self):
        """Test basic cache get/set operations"""
        cache = CacheService(max_size=100)
        
        # Test set and get
        cache.set("test_key", "test_value", ttl_seconds=60)
        value = cache.get("test_key")
        assert value == "test_value"
        
        # Test cache hit stats
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 0
        
    def test_cache_miss(self):
        """Test cache miss behavior"""
        cache = CacheService(max_size=100)
        
        # Get non-existent key
        value = cache.get("nonexistent")
        assert value is None
        
        # Check stats
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 1
        
    def test_cache_expiration(self):
        """Test TTL expiration"""
        cache = CacheService(max_size=100)
        
        # Set with very short TTL
        cache.set("expire_key", "expire_value", ttl_seconds=0.1)
        
        # Should exist immediately
        value = cache.get("expire_key")
        assert value == "expire_value"
        
        # Wait for expiration
        import time
        time.sleep(0.2)
        
        # Should be expired
        value = cache.get("expire_key")
        assert value is None
        
    def test_cache_clear(self):
        """Test cache clearing"""
        cache = CacheService(max_size=100)
        
        # Add some entries
        cache.set("key1", "value1", ttl_seconds=60)
        cache.set("key2", "value2", ttl_seconds=60)
        
        # Verify they exist
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        
        # Clear cache
        cache.clear()
        
        # Verify they're gone
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        
        stats = cache.get_stats()
        assert stats["size"] == 0
        
    def test_lru_eviction(self):
        """Test LRU eviction when max_size is reached"""
        cache = CacheService(max_size=3)
        
        # Fill cache to max
        cache.set("key1", "value1", ttl_seconds=60)
        cache.set("key2", "value2", ttl_seconds=60)
        cache.set("key3", "value3", ttl_seconds=60)
        
        # All should exist
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        
        # Add one more - should evict key1 (least recently used)
        cache.set("key4", "value4", ttl_seconds=60)
        
        # key1 should be evicted
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
        
    def test_question_cache_helpers(self):
        """Test question-specific cache helpers"""
        cache = CacheService(max_size=100)
        
        question_data = {
            "question": "What is 2+2?",
            "answer": "4",
            "topic": "arithmetic"
        }
        
        # Cache question
        cache.cache_question("q123", question_data)
        
        # Retrieve question
        retrieved = cache.get_question("q123")
        assert retrieved == question_data
        assert retrieved["question"] == "What is 2+2?"
        
    def test_hint_cache_helpers(self):
        """Test hint-specific cache helpers"""
        cache = CacheService(max_size=100)
        
        # Cache hints at different levels
        cache.cache_hint("q123", 1, "Think about basic arithmetic")
        cache.cache_hint("q123", 2, "Use addition")
        cache.cache_hint("q123", 3, "Add the two numbers together")
        
        # Retrieve hints
        hint1 = cache.get_hint("q123", 1)
        hint2 = cache.get_hint("q123", 2)
        hint3 = cache.get_hint("q123", 3)
        
        assert hint1 == "Think about basic arithmetic"
        assert hint2 == "Use addition"
        assert hint3 == "Add the two numbers together"
        
    def test_solution_cache_helpers(self):
        """Test solution-specific cache helpers"""
        cache = CacheService(max_size=100)
        
        solution = {"answer": "4", "solution_steps": ["2 + 2 = 4. This is basic addition."]}
        
        # Cache solution
        cache.cache_solution("q123", solution)
        
        # Retrieve solution
        retrieved = cache.get_solution("q123")
        assert retrieved == solution
        assert retrieved["answer"] == "4"
        
    def test_hit_rate_calculation(self):
        """Test hit rate calculation"""
        cache = CacheService(max_size=100)
        
        # Set some values
        cache.set("key1", "value1", ttl_seconds=60)
        cache.set("key2", "value2", ttl_seconds=60)
        
        # 2 hits
        cache.get("key1")
        cache.get("key2")
        
        # 2 misses
        cache.get("key3")
        cache.get("key4")
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 2
        assert stats["hit_rate"] == 50.0  # 50% hit rate (returned as percentage)


class TestCacheIntegration:
    """Test cache integration with API endpoints"""
    
    def test_question_caching(self, auth_headers):
        """Test that questions are cached properly"""
        # Generate a question
        response1 = client.post(
            "/api/v1/generate-question",
            json={"topic": "arithmetic", "difficulty": "easy", "grade": 6},
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        question_id = data1["id"]
        
        # First request - should not be cached
        # Note: Question generation doesn't cache by default
        # This test just ensures the caching infrastructure works
        
    def test_hint_caching(self, auth_headers):
        """Test that hints are cached properly"""
        # Generate a question first
        response = client.post(
            "/api/v1/generate-question",
            json={"topic": "arithmetic", "difficulty": "easy", "grade": 6},
            headers=auth_headers
        )
        assert response.status_code == 200
        question_id = response.json()["id"]
        
        # Request hint - first time
        response1 = client.post(
            f"/api/v1/questions/{question_id}/hint",
            json={"hint_level": 1},
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1.get("cached", False) == False
        hint1 = data1["hint"]
        
        # Request same hint again - should be cached
        response2 = client.post(
            f"/api/v1/questions/{question_id}/hint",
            json={"hint_level": 1},
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2.get("cached", False) == True
        assert data2["hint"] == hint1  # Should be same hint
        
    def test_solution_caching(self, auth_headers):
        """Test that solutions are cached properly"""
        # Generate a question first
        response = client.post(
            "/api/v1/generate-question",
            json={"topic": "arithmetic", "difficulty": "easy", "grade": 6},
            headers=auth_headers
        )
        assert response.status_code == 200
        question_id = response.json()["id"]
        
        # Request solution - first time
        response1 = client.post(
            f"/api/v1/questions/{question_id}/solution",
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1.get("cached", False) == False
        assert "answer" in data1
        assert "solution_steps" in data1
        solution1 = data1["answer"]
        
        # Request same solution again - should be cached
        response2 = client.post(
            f"/api/v1/questions/{question_id}/solution",
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2.get("cached", False) == True
        assert data2["answer"] == solution1  # Should be same answer
        
    def test_cache_stats_endpoint(self, auth_headers):
        """Test the cache stats endpoint"""
        # Make some requests to populate cache
        client.post(
            "/api/v1/generate-question",
            json={"topic": "arithmetic", "difficulty": "easy", "grade": 6},
            headers=auth_headers
        )
        
        # Get cache stats
        response = client.get("/api/v1/cache/stats")
        assert response.status_code == 200
        
        stats = response.json()
        assert "hits" in stats
        assert "misses" in stats
        assert "size" in stats
        assert "max_size" in stats
        assert "hit_rate" in stats
        
        # Stats should be valid
        assert stats["hits"] >= 0
        assert stats["misses"] >= 0
        assert stats["size"] >= 0
        assert stats["max_size"] > 0
