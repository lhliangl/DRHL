class DRHLError(RuntimeError):
    """Base error for expected pipeline failures."""


class ConfigError(DRHLError):
    """The pipeline configuration is invalid."""


class DatabaseError(DRHLError):
    """A database snapshot or restore operation failed."""


class CrawlError(DRHLError):
    """A role crawl failed."""


class DetectionError(DRHLError):
    """Active verification could not be completed safely."""

