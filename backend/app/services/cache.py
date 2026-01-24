import logging
import redis
import os
import hashlib
from typing import Optional, Dict, Any
import json


class CacheService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")

        if not redis_url:
            logging.info("Redis URL not configured - caching disabled")
            self.client = None
            self.enabled = False
        else:
            try:
                # creating TCP connection pool
                self.client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.client.ping()
                self.enabled = True
                logging.info("redis cache connected")
            except Exception as e:
                logging.warning(f"Redis connection failed: {e} - caching disabled")
                self.client = None
                self.enabled = False

    def _generate_key(self, prefix: str, data: str) -> str:
        hash_obj = hashlib.md5(data.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

    # Get cached analysis for an error log
    def get_analysis(self, error_log: str) -> Optional[Dict]:
        if not self.enabled:
            return None

        try:
            key = self._generate_key("analysis", error_log)
            cached = self.client.get(key)

            if cached:
                logging.info("Cache hit for analysis")
                return json.loads(cached)

            logging.info("Cache miss the analysis")
            return None

        except Exception as e:
            logging.warning(f"Cache get error: {e}")
            return None

    # Cache an analysis result
    # 24 hours default time
    def set_analysis(self, error_log: str, analysis: dict, ttl: int = 86400):
        if not self.enabled:
            return None

        try:
            key = self._generate_key("analysis", error_log)
            self.client.set(
                key, json.dumps(analysis), ex=ttl
            )  # nx = True  1h total time to live
            logging.info(f"Cached analysis (TTL: {ttl}s)")

        except Exception as e:
            logging.info(f"Cache set error: {e}")

    # when get_analysis failed it uses get_search with parsed string
    def get_search_results(self, query: str) -> Optional[Dict]:
        """
        Get cached search results
        """
        if not self.enabled:
            return None

        try:
            key = self._generate_key("search", query)
            cached = self.client.get(key)

            if cached:
                logging.info(f"Cache HIT for search")
                return json.loads(cached)

            return None

        except Exception as e:
            logging.info(f"Cache get error: {e}")
            return None

    def set_search_results(
        self,
        query: str,
        results: Dict,
        ttl: int = 86400,  # 2 hours default time to leave
    ):
        """
        Cache search results
        """
        if not self.enabled:
            return

        try:
            key = self._generate_key("search", query)
            self.client.set(key, json.dumps(results), ex=ttl)
            logging.info(f"Cached search results (TTL: {ttl}s)")

        except Exception as e:
            logging.info(f"Cache set error: {e}")

    def get_stats(self) -> Dict:
        """
        Get cache statistics
        """
        if not self.enabled:
            return {"enabled": False, "message": "Caching is disabled"}

        try:
            info = self.client.info("stats")
            return {
                "enabled": True,
                "total_keys": self.client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0)
                / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1),
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}
