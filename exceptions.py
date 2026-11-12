class AssetError(Exception):
    """Base exception for expected asset-related errors."""


class AssetNotFoundError(AssetError):
    """Raised when an active asset cannot be found."""


class DuplicateAssetError(AssetError):
    """Raised when a database uniqueness rule is violated."""
