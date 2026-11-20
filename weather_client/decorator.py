import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timing(function: Callable[P, R]) -> Callable[P, R]:

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start_time
            print(f"{function.__name__} took {elapsed:.4f} seconds")

    return wrapper


def retry(
    times: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:

    if times < 1:
        raise ValueError("times must be at least 1")
    if delay < 0:
        raise ValueError("delay cannot be negative")
    if not exceptions:
        raise ValueError("exceptions cannot be empty")

    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(times):
                try:
                    return function(*args, **kwargs)
                except exceptions:
                    if attempt == times - 1:
                        raise
                    time.sleep(delay)

        return wrapper

    return decorator
