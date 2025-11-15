class ScraperError(Exception):
    """Base class for all scraper-related errors."""

class PageNotLoadedError(ScraperError):
    """Raised when attempting to scrape before loading a page."""

class ElementNotFoundError(ScraperError):
    """Raised when an element cannot be found on the page."""
    def __init__(self, selector: str, url: str):
        super().__init__(
            f"Element not found.\n"
            f"Selector: '{selector}'\n"
            f"URL: {url}\n"
            f"Please verify that the selector is correct and the page structure has not changed."
        )

class ElementParseError(ScraperError):
    """Raised when the scraped element cannot be parsed to a value."""
    def __init__(self, selector: str, value: str, reason: str):
        super().__init__(
            f"Failed to parse element.\n"
            f"Selector: '{selector}'\n"
            f"Value: '{value}'\n"
            f"Reason: {reason}\n"
            f"Check if the element's content matches the expected format or type."
        )
