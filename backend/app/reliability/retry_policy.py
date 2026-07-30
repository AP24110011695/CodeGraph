import abc
import math
from typing import Optional

class RetryPolicy(abc.ABC):
    @abc.abstractmethod
    def get_delay(self, attempt: int) -> Optional[float]:
        """Return the delay in seconds for the next retry, or None if retries are exhausted."""
        pass

class FixedRetryPolicy(RetryPolicy):
    def __init__(self, max_attempts: int, delay_seconds: float):
        self.max_attempts = max_attempts
        self.delay_seconds = delay_seconds

    def get_delay(self, attempt: int) -> Optional[float]:
        if attempt >= self.max_attempts:
            return None
        return self.delay_seconds

class LinearRetryPolicy(RetryPolicy):
    def __init__(self, max_attempts: int, base_delay: float):
        self.max_attempts = max_attempts
        self.base_delay = base_delay

    def get_delay(self, attempt: int) -> Optional[float]:
        if attempt >= self.max_attempts:
            return None
        return self.base_delay * attempt

class ExponentialRetryPolicy(RetryPolicy):
    def __init__(self, max_attempts: int, initial_delay: float, multiplier: float = 2.0, max_delay: float = 3600.0):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.multiplier = multiplier
        self.max_delay = max_delay

    def get_delay(self, attempt: int) -> Optional[float]:
        if attempt >= self.max_attempts:
            return None
        delay = self.initial_delay * math.pow(self.multiplier, attempt - 1)
        return min(delay, self.max_delay)
