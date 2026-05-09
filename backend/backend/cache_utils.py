from functools import wraps
from django.core.cache import cache
from django.conf import settings
from rest_framework.response import Response


def _cache_enabled():
    """Check if the global cache is enabled (CACHE_TTL > 0)."""
    return getattr(settings, 'CACHE_TTL', 300) > 0


def cache_response(timeout=None, key_prefix=None):
    """Decorator for DRF view methods to cache GET responses per-user.

    Caching is skipped entirely when settings.CACHE_TTL <= 0 (useful for tests).

    Usage:
        @cache_response(timeout=300)
        def get(self, request):
            ...

        @cache_response(timeout=60)
        def list(self, request, *args, **kwargs):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if request.method != 'GET':
                return func(self, request, *args, **kwargs)

            if not _cache_enabled():
                return func(self, request, *args, **kwargs)

            ttl = timeout if timeout is not None else getattr(settings, 'CACHE_TTL', 300)
            prefix = key_prefix or type(self).__name__
            key = (
                f"api_cache:u{request.user.id}:"
                f"{prefix}:{request.get_full_path()}"
            )

            cached = cache.get(key)
            if cached is not None:
                return Response(cached)

            response = func(self, request, *args, **kwargs)
            if response.status_code == 200:
                cache.set(key, response.data, ttl)
            return response
        return wrapper
    return decorator


def clear_api_cache():
    """Clear the entire API cache. Use sparingly (e.g., on model mutations)."""
    cache.clear()
