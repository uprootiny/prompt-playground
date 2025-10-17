"""
Response caching for prompt playground
Reduces costs and latency for repeated prompts
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CachedResponse:
    """Cached LLM response"""
    prompt: str
    provider: str
    model: str
    response: str
    timestamp: float
    input_tokens: int
    output_tokens: int
    cost: float
    latency: float


class ResponseCache:
    """
    In-memory cache for LLM responses

    Features:
    - TTL-based expiration
    - LRU eviction when max size reached
    - Cache hit/miss metrics
    - Content-addressed storage (hash-based keys)
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, CachedResponse] = {}
        self.access_times: Dict[str, float] = {}  # For LRU
        self.hits = 0
        self.misses = 0

    def _make_key(
        self,
        prompt: str,
        provider: str,
        model: str,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate cache key from request parameters"""
        key_data = {
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "system_prompt": system_prompt or "",
        }
        key_json = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_json.encode()).hexdigest()

    def get(
        self,
        prompt: str,
        provider: str,
        model: str,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ) -> Optional[CachedResponse]:
        """
        Get cached response if available and not expired

        Returns None if not found or expired
        """
        key = self._make_key(prompt, provider, model, temperature, system_prompt)

        if key not in self.cache:
            self.misses += 1
            return None

        cached = self.cache[key]
        age = time.time() - cached.timestamp

        # Check if expired
        if age > self.ttl_seconds:
            logger.debug(f"Cache expired for key {key[:8]}... (age={age:.0f}s)")
            del self.cache[key]
            del self.access_times[key]
            self.misses += 1
            return None

        # Update access time for LRU
        self.access_times[key] = time.time()
        self.hits += 1

        logger.info(f"Cache hit for {provider}/{model} (age={age:.0f}s)")
        return cached

    def put(
        self,
        prompt: str,
        provider: str,
        model: str,
        response: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        latency: float,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ):
        """Add response to cache"""
        key = self._make_key(prompt, provider, model, temperature, system_prompt)

        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        cached_response = CachedResponse(
            prompt=prompt,
            provider=provider,
            model=model,
            response=response,
            timestamp=time.time(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency=latency,
        )

        self.cache[key] = cached_response
        self.access_times[key] = time.time()

        logger.debug(f"Cached response for {provider}/{model} (cache_size={len(self.cache)})")

    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.access_times:
            return

        # Find oldest access
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])

        logger.debug(f"Evicting LRU entry {lru_key[:8]}...")
        del self.cache[lru_key]
        del self.access_times[lru_key]

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.access_times.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        # Calculate cost savings
        total_cost_saved = sum(c.cost for c in self.cache.values()) * self.hits

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl_seconds,
            "estimated_cost_saved": total_cost_saved,
        }

    def cleanup_expired(self):
        """Remove expired entries"""
        now = time.time()
        expired_keys = [
            key for key, cached in self.cache.items()
            if now - cached.timestamp > self.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired entries")

        return len(expired_keys)
