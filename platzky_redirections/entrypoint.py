from flask import redirect
from gql import gql
from pydantic import BaseModel


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
    return [
        Redirection(source=source, destination=destination)
        for source, destination in config.items()
    ]


def setup_routes(app, redirections):
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


def process(app, config: dict[str, str]) -> object:
    redirections = parse_redirections(config)
    setup_routes(app, redirections)
    return app
