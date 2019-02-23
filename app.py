from dawn import Dawn, Response


app = Dawn(__name__)


def hello(request):
    return Response(['hello world'])


def template(request):
    name = 'CC'
    return app.render_templates('index.html', name=name)


if __name__ == '__main__':
    app.run()