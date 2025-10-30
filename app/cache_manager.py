import time
from pymemcache.client.base import Client
from pymemcache import serde

CACHE_KEY = "recent_notifications"

# Global cache client - will be lazy-loaded
_cache_client = None


def get_cache_client():
    """Get or create the cache client with retry logic."""
    global _cache_client
    
    if _cache_client is None:
        # Try different hosts: localhost for local dev, memcached for Docker
        hosts_to_try = [("localhost", 11211), ("memcached", 11211)]
        
        for host, port in hosts_to_try:
            try:
                print(f"Attempting to connect to memcached at {host}:{port}")
                temp_client = Client((host, port), serde=serde.pickle_serde)
                # Test the connection
                temp_client.set("_health_check", "ok", expire=5)
                print(f"Successfully connected to memcached at {host}:{port}")
                _cache_client = temp_client
                break
            except Exception as e:
                print(f"Failed to connect to {host}:{port}: {e}")
                continue
        
        # If no connection worked, use mock client
        if _cache_client is None:
            print("Could not connect to any memcached instance, using in-memory fallback")
            _cache_client = MockCacheClient()
    
    return _cache_client


class MockCacheClient:
    """Fallback client when memcached is unavailable."""
    def __init__(self):
        self._storage = {}
        
    def get(self, key):
        return self._storage.get(key)
        
    def set(self, key, value, expire=0):
        self._storage[key] = value
        return True


def store_notification(message: str):
    """Store a notification message in the cache.

    Keeps only the last 5 messages.
    """
    try:
        cache = get_cache_client()
        messages = cache.get(CACHE_KEY) or []
        # Ensure we always work with a list
        if not isinstance(messages, list):
            messages = [messages]
        messages.append(message)
        if len(messages) > 5:
            messages = messages[-5:]  # Keep only the last 5 messages
        cache.set(CACHE_KEY, messages, expire=3600)  # Cache for 1 hour
    except Exception as e:
        print(f"Error storing notification: {e}")
        # Reset cache client to force fallback on next call
        global _cache_client
        _cache_client = MockCacheClient()
        _cache_client.set(CACHE_KEY, [message], expire=3600)


def get_recent_notifications():
    """Retrieve recent notification messages from the cache."""
    try:
        cache = get_cache_client()
        messages = cache.get(CACHE_KEY) or []
        if not isinstance(messages, list):
            messages = [messages]
        return messages
    except Exception as e:
        print(f"Error getting recent notifications: {e}")
        # Reset cache client to force fallback on next call
        global _cache_client
        _cache_client = MockCacheClient()
        return []