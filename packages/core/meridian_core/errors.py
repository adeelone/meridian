class MeridianError(Exception):
    pass


class ConfigurationError(MeridianError):
    pass


class SearchProviderError(MeridianError):
    pass


class QuotaExceededError(MeridianError):
    pass


class RateLimitError(MeridianError):
    pass
