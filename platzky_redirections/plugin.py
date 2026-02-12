"""Platzky redirections plugin — registers 301 redirect routes from config."""

from collections.abc import Callable
from typing import Any

from flask import redirect
from platzky.engine import Engine
from platzky.plugin.plugin import PluginBase, PluginBaseConfig
from pydantic import BaseModel
from werkzeug.wrappers import Response


class Redirection(BaseModel):
    """A URL redirection mapping a source path to a destination URL."""

    source: str
    destination: str


def parse_redirections(config: dict[str, Any]) -> list[Redirection]:
    """
    Parse and validate redirection configuration.

    Args:
        config: Dictionary mapping source URLs to destination URLs

    Returns:
        List of validated Redirection objects

    Raises:
        ValueError: If URLs are malformed or values are not strings
    """
    non_string_entries = {
        k: v for k, v in config.items() if not isinstance(k, str) or not isinstance(v, str)
    }
    if non_string_entries:
        raise ValueError(f"All keys and values must be strings, got: {non_string_entries}")

    def validate_url(url: str) -> bool:
        """Check that a URL starts with '/' or 'http://' or 'https://'."""
        return url.startswith(("/", "http://", "https://"))

    invalid_urls = [url for url in config.keys() | config.values() if not validate_url(url)]
    if invalid_urls:
        raise ValueError(f"Invalid URLs found: {invalid_urls}")

    return [
        Redirection(source=source, destination=destination)
        for source, destination in config.items()
    ]


def setup_routes(app: Engine, redirections: list[Redirection]) -> None:
    """
    Set up Flask routes for redirections.

    Args:
        app: Flask application instance
        redirections: List of Redirection objects

    Raises:
        ValueError: If route conflicts are detected
    """
    existing_routes: set[str] = set(rule.rule for rule in app.url_map.iter_rules())
    conflicts = [r.source for r in redirections if r.source in existing_routes]
    if conflicts:
        raise ValueError(f"Route conflicts detected: {conflicts}")

    for redirection in redirections:
        func = redirect_with_name(
            redirection.destination,
            code=301,
            name=f"{redirection.source}-{redirection.destination}",
        )
        app.route(rule=redirection.source)(func)


def redirect_with_name(destination: str, code: int, name: str) -> Callable[..., Response]:
    """Create a named redirect function for use as a Flask view."""

    def named_redirect() -> Response:
        """Return a Flask redirect response."""
        return redirect(destination, code)

    named_redirect.__name__ = name
    return named_redirect


class RedirectionsConfig(PluginBaseConfig):
    """Configuration model for the redirections plugin."""


class RedirectionsPlugin(PluginBase[RedirectionsConfig]):
    """Platzky plugin that registers URL redirections as Flask 301 routes."""

    @classmethod
    def get_config_model(cls) -> type[RedirectionsConfig]:
        """Return the config model class for this plugin."""
        return RedirectionsConfig

    def process(self, app: Engine) -> Engine:
        """Parse redirection config and register redirect routes on the app."""
        redirections = parse_redirections(self.config.model_extra or {})
        setup_routes(app, redirections)
        return app
