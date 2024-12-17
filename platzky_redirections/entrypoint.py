from flask import redirect
from gql import gql
from pydantic import BaseModel
from platzky import Engine

def json_db_get_redirections(self):
    return self.data.get("redirections", {})


def json_file_db_get_redirections(self):
    return json_db_get_redirections(self)


def google_json_db_get_redirections(self):
    return self.data.get("redirections", {})


def graph_ql_db_get_redirections(self):
    redirections = gql(
        """
        query MyQuery{
          redirections(stage: PUBLISHED){
            source
            destination
          }
        }
        """
    )
    return {
        x["source"]: x["destination"]
        for x in self.client.execute(redirections)["redirections"]
    }


class Redirection(BaseModel):
    source: str
    destination: str


def parse_redirections(config: dict[str, str]) -> list[Redirection]:
    """
    Parse and validate redirection configuration.
    
    Args:
        config: Dictionary mapping source URLs to destination URLs
    
    Returns:
        List of validated Redirection objects
    
    Raises:
        ValueError: If URLs are malformed
    """
    def validate_url(url: str) -> bool:
        return url.startswith('/') or url.startswith('http')

    invalid_urls = [url for url in config.keys() | config.values() if not validate_url(url)]
    if invalid_urls:
        raise ValueError(f"Invalid URLs found: {invalid_urls}")

    return [
        Redirection(source=source, destination=destination)
        for source, destination in config.items()
    ]


def setup_routes(app, redirections):
    """
    Set up Flask routes for redirections.
    
    Args:
        app: Flask application instance
        redirections: List of Redirection objects
    
    Raises:
        ValueError: If route conflicts are detected
    """
    existing_routes = set(rule.rule for rule in app.url_map.iter_rules())
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


def redirect_with_name(destination, code, name):
    def named_redirect(*args, **kwargs):
        return redirect(destination, code, *args, **kwargs)

    named_redirect.__name__ = name
    return named_redirect


def process(app: Engine , config: dict[str, str]) -> Engine:
    redirections = parse_redirections(config)
    setup_routes(app, redirections)
    return app
