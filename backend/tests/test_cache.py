"""
Tests for response caching
"""

import pytest
import time
from cache import ResponseCache, CachedResponse


class TestResponseCache:
    """Test response caching functionality"""

    @pytest.fixture
    def cache(self):
        """Create cache with short TTL for testing"""
        return ResponseCache(max_size=10, ttl_seconds=2)

    def test_cache_put_and_get(self, cache):
        """Test basic put and get"""
        cache.put(
            prompt="What is 2+2?",
            provider="openai",
            model="gpt-4",
            response="2+2 equals 4",
            input_tokens=10,
            output_tokens=5,
            cost=0.001,
            latency=0.5,
        )

        cached = cache.get(
            prompt="What is 2+2?",
            provider="openai",
            model="gpt-4",
        )

        assert cached is not None
        assert cached.response == "2+2 equals 4"
        assert cached.input_tokens == 10
        assert cached.output_tokens == 5
        assert cached.cost == 0.001

    def test_cache_miss(self, cache):
        """Test cache miss"""
        cached = cache.get(
            prompt="Unknown prompt",
            provider="openai",
            model="gpt-4",
        )

        assert cached is None
        assert cache.misses == 1
        assert cache.hits == 0

    def test_cache_hit_stats(self, cache):
        """Test cache hit statistics"""
        # Add entry
        cache.put(
            prompt="test",
            provider="openai",
            model="gpt-4",
            response="response",
            input_tokens=5,
            output_tokens=10,
            cost=0.01,
            latency=0.1,
        )

        # Get it twice
        cache.get("test", "openai", "gpt-4")
        cache.get("test", "openai", "gpt-4")

        assert cache.hits == 2
        assert cache.misses == 0

    def test_cache_different_parameters(self, cache):
        """Test cache distinguishes different parameters"""
        cache.put(
            prompt="test",
            provider="openai",
            model="gpt-4",
            response="response1",
            input_tokens=5,
            output_tokens=10,
            cost=0.01,
            latency=0.1,
            temperature=0.7,
        )

        cache.put(
            prompt="test",
            provider="openai",
            model="gpt-4",
            response="response2",
            input_tokens=5,
            output_tokens=10,
            cost=0.01,
            latency=0.1,
            temperature=0.9,  # Different temperature
        )

        # Should get different responses for different temperatures
        cached1 = cache.get("test", "openai", "gpt-4", temperature=0.7)
        cached2 = cache.get("test", "openai", "gpt-4", temperature=0.9)

        assert cached1.response == "response1"
        assert cached2.response == "response2"

    def test_cache_ttl_expiration(self, cache):
        """Test TTL expiration"""
        cache.put(
            prompt="test",
            provider="openai",
            model="gpt-4",
            response="response",
            input_tokens=5,
            output_tokens=10,
            cost=0.01,
            latency=0.1,
        )

        # Should be cached
        cached = cache.get("test", "openai", "gpt-4")
        assert cached is not None

        # Wait for expiration
        time.sleep(2.1)

        # Should be expired
        cached = cache.get("test", "openai", "gpt-4")
        assert cached is None

    def test_cache_lru_eviction(self):
        """Test LRU eviction when max size reached"""
        cache = ResponseCache(max_size=3, ttl_seconds=100)

        # Fill cache
        for i in range(3):
            cache.put(
                prompt=f"prompt{i}",
                provider="openai",
                model="gpt-4",
                response=f"response{i}",
                input_tokens=5,
                output_tokens=10,
                cost=0.01,
                latency=0.1,
            )

        # Access first one to make it recently used
        cache.get("prompt0", "openai", "gpt-4")

        # Add one more (should evict prompt1, the least recently used)
        cache.put(
            prompt="prompt3",
            provider="openai",
            model="gpt-4",
            response="response3",
            input_tokens=5,
            output_tokens=10,
            cost=0.01,
            latency=0.1,
        )

        # Check that prompt1 was evicted
        assert cache.get("prompt0", "openai", "gpt-4") is not None
        assert cache.get("prompt1", "openai", "gpt-4") is None
        assert cache.get("prompt2", "openai", "gpt-4") is not None
        assert cache.get("prompt3", "openai", "gpt-4") is not None

    def test_cache_clear(self, cache):
        """Test cache clear"""
        # Add entries
        for i in range(5):
            cache.put(
                prompt=f"prompt{i}",
                provider="openai",
                model="gpt-4",
                response=f"response{i}",
                input_tokens=5,
                output_tokens=10,
                cost=0.01,
                latency=0.1,
            )

        assert len(cache.cache) == 5

        cache.clear()

        assert len(cache.cache) == 0
        assert len(cache.access_times) == 0

    def test_cache_stats(self, cache):
        """Test cache statistics"""
        # Add some entries
        for i in range(3):
            cache.put(
                prompt=f"prompt{i}",
                provider="openai",
                model="gpt-4",
                response=f"response{i}",
                input_tokens=10,
                output_tokens=20,
                cost=0.01,
                latency=0.1,
            )

        # Get some hits and misses
        cache.get("prompt0", "openai", "gpt-4")
        cache.get("prompt0", "openai", "gpt-4")
        cache.get("unknown", "openai", "gpt-4")

        stats = cache.get_stats()

        assert stats['size'] == 3
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_rate'] == pytest.approx(66.67, rel=0.1)
        assert 'estimated_cost_saved' in stats

    def test_cache_system_prompt_differentiation(self, cache):
        """Test that system prompts are distinguished"""
        cache.put(
            prompt="test",
            provider="openai",
            model="gpt-4",
            response="response1",
            input_tokens=5,
            output_tokens=10,
            cost=0.01,
            latency=0.1,
            system_prompt="You are a helpful assistant",
        )

        cache.put(
            prompt="test",
            provider="openai",
            model="gpt-4",
            response="response2",
            input_tokens=5,
            output_tokens=10,
            cost=0.01,
            latency=0.1,
            system_prompt="You are a code expert",
        )

        # Should get different responses
        cached1 = cache.get("test", "openai", "gpt-4", system_prompt="You are a helpful assistant")
        cached2 = cache.get("test", "openai", "gpt-4", system_prompt="You are a code expert")

        assert cached1.response == "response1"
        assert cached2.response == "response2"

    def test_cleanup_expired(self, cache):
        """Test cleanup of expired entries"""
        # Add entries
        for i in range(3):
            cache.put(
                prompt=f"prompt{i}",
                provider="openai",
                model="gpt-4",
                response=f"response{i}",
                input_tokens=5,
                output_tokens=10,
                cost=0.01,
                latency=0.1,
            )

        assert len(cache.cache) == 3

        # Wait for expiration
        time.sleep(2.1)

        # Cleanup
        removed = cache.cleanup_expired()

        assert removed == 3
        assert len(cache.cache) == 0
