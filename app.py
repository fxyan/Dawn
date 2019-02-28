from dawn import Dawn, Response


app = Dawn(__name__)


def hello(request):
    # c = [1, 2]
    # print(c[7])
    return Response(['hello world'])


def year(request, year, month):
    print(request)
    return Response(['hello world {}, {}'.format(year, month)])


def template(request):
    name = 'CC'
    return app.render_templates('index.html', name=name)


if __name__ == '__main__':
    app.run()