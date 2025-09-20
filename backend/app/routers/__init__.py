# app/routers/__init__.py
from .webpages import router as webpages_router
from .scrapes import router as scrapes_router

__all__ = ["webpages_router", "scrapes_router"]
