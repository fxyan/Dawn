from app import hello, template, year

route_dict = {
    'hello/': hello,
    '': template,
    'mm/<int:year>/<int:month>': year,
}
