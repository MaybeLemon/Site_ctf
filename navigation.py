def get_nav(app):
    # all_routes = app.url_map._rules
    with app.app_context():
        nav = [
            {'name': 'Главная', 'url': '/'},
            {'name': 'Топ', 'url': '/top'},
            {'name': 'Задания', 'url': '/tasks'},
        ]
    return nav

