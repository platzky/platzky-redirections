from typing import Any, Dict

import pytest
from platzky.platzky import Config, create_app_from_config

from platzky_redirections.plugin import parse_redirections, setup_routes, Redirection


def test_plugin_loader():
    data_with_plugin: Dict[str, Any] = {
        "APP_NAME": "testingApp",
        "SECRET_KEY": "secret",
        "USE_WWW": False,
        "BLOG_PREFIX": "/",
        "TRANSLATION_DIRECTORIES": ["/some/fake/dir"],
        "DB": {
            "TYPE": "json",
            "DATA": {
                "site_content": {"pages": []},
                "plugins": [{"name": "redirections", "config": {"/page/test": "/page/test2"}}],
            },
        },
    }
    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)
    response = app_with_plugin.test_client().get("/page/test", follow_redirects=False)
    assert response.status_code == 301
    assert response.location == "/page/test2"


def test_parse_redirections_rejects_non_string_values():
    with pytest.raises(ValueError, match="All keys and values must be strings"):
        parse_redirections({"/source": 123})


def test_parse_redirections_rejects_invalid_urls():
    with pytest.raises(ValueError, match="Invalid URLs found"):
        parse_redirections({"not-a-url": "/destination"})


def test_setup_routes_rejects_conflicting_routes():
    config: Dict[str, Any] = {
        "APP_NAME": "testingApp",
        "SECRET_KEY": "secret",
        "USE_WWW": False,
        "BLOG_PREFIX": "/",
        "TRANSLATION_DIRECTORIES": ["/some/fake/dir"],
        "DB": {"TYPE": "json", "DATA": {"site_content": {"pages": []}, "plugins": []}},
    }
    app = create_app_from_config(Config.model_validate(config))
    with pytest.raises(ValueError, match="Route conflicts detected"):
        setup_routes(app, [Redirection(source="/static/<path:filename>", destination="/other")])
