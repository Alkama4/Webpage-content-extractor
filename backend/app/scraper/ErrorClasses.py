class ScraperError(Exception):
    """Base class for all scraper-related errors."""

class PageNotLoadedError(ScraperError):
    """Raised when attempting to scrape before loading a page."""

class ElementNotFoundError(ScraperError):
    """Raised when an element cannot be found on the page."""
    def __init__(self, selector: str, url: str):
        super().__init__(f"Could not find an element with the selector '{selector}' from the url: {url}")

class ElementParseError(ScraperError):
    """Raised when the scraped element cannot be parsed to a value."""
    def __init__(self, selector: str, value: str, reason: str):
        super().__init__(f"Parsing failed for the element found with the following locator '{selector}' with value '{value}': {reason}")