"""Module for timer to time execution of function"""
import time
import functools
import inspect

def timed(label: str = ""):
    """Decorator for timer"""
    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start
            print(f"{label or func.__name__} took {duration:.4f}s")
            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            print(f"{label or func.__name__} took {duration:.4f}s")
            return result

        return async_wrapper if is_async else sync_wrapper
    return decorator
