"""Custom exceptions for pricing analysis services."""


class PricingAnalysisException(Exception):
    """Base exception for pricing analysis errors."""
    pass


class KeepaAPIError(PricingAnalysisException):
    """Raised when Keepa API call fails."""
    pass


class TokenLimitExceededError(PricingAnalysisException):
    """Raised when Keepa API token limit is exceeded."""
    pass


class ExchangeRateNotFoundError(PricingAnalysisException):
    """Raised when no active exchange rate is found."""
    pass


class ProductNotAvailableError(PricingAnalysisException):
    """Raised when product is not available for purchase."""
    pass


class AnalysisConfigNotFoundError(PricingAnalysisException):
    """Raised when no active analysis config is found."""
    pass
