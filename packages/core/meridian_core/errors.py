class MeridianError(Exception):
    """Base user-safe Meridian exception."""


class ConfigurationError(MeridianError):
    pass


class SearchProviderError(MeridianError):
    pass


class QuotaExceededError(MeridianError):
    pass


class RateLimitError(MeridianError):
    pass
