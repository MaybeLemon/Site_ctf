def get_nav(app):
    # all_routes = app.url_map._rules
    with app.app_context():
        nav = [
            {'name': 'Home', 'url': '/'},
            {'name': 'Tasks', 'url': '/tasks'},
        ]
    return nav

