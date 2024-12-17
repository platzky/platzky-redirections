from flask import Flask
from platzky_redirections.entrypoint import Redirection, parse_redirections, setup_routes, redirect_with_name, process

def test_redirections_are_parsed_correctly(self):
    config = {'/old-path': '/new-path'}
    redirections = parse_redirections(config)
    self.assertEqual(len(redirections), 1)
    self.assertEqual(redirections[0].source, '/old-path')
    self.assertEqual(redirections[0].destiny, '/new-path')

def test_redirections_are_empty_for_empty_config(self):
    config = {}
    redirections = parse_redirections(config)
    self.assertEqual(len(redirections), 0)

def test_routes_are_set_up_correctly(self):
    app = Flask(__name__)
    redirections = [Redirection(source='/old-path', destiny='/new-path')]
    setup_routes(app, redirections)
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    self.assertIn('/old-path', rules)

def test_redirect_with_name_sets_correct_name(self):
    func = redirect_with_name('/new-path', 301, 'redirect_func')
    self.assertEqual(func.__name__, 'redirect_func')

def test_process_sets_up_app_correctly(self):
    app = Flask(__name__)
    config = {'/old-path': '/new-path'}
    processed_app = process(app, config)
    rules = [rule.rule for rule in processed_app.url_map.iter_rules()]
    self.assertIn('/old-path', rules)
