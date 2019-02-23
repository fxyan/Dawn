from app import hello, template

route_dict = {
    '/hello': hello,
    '/': template,
}
