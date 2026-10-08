from __future__ import annotations

import functools
import inspect
import logging
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def log_call(event: str) -> Callable[[F], F]:
    logger = logging.getLogger("telegram_documentaries")

    def decorator(func: F) -> F:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                logger.info("event=%s", event)
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    logger.exception("event=%s error", event)
                    raise

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info("event=%s", event)
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.exception("event=%s error", event)
                raise

        return wrapper  # type: ignore[return-value]

    return decorator
