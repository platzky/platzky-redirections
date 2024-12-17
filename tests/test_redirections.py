from typing import Any, Dict


from platzky.platzky import create_app_from_config, Config


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
                "plugins": [
                    {"name": "redirections", "config": {"/page/test": "/page/test2"}}
                ],
            },
        },
    }
    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)
    response = app_with_plugin.test_client().get("/page/test", follow_redirects=False)
    assert response.status_code == 301
    assert response.location == "/page/test2"
