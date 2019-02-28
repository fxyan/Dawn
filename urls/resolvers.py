import re
from .converters import get_converter

_PATH_RE = re.compile(
    r'<(?P<converter>[^/:]+):(?P<parameter>\w+)>'
)


def _route_regex(route):
    """

    :param route: 未经正则处理的路由
    :return: 对应的经过转换器处理的正则路由和对应的字典
    """
    original_route = route
    part = ['^']
    converters = {}
    while True:
        match = _PATH_RE.search(route)
        if not match:
            part.append(re.escape(route))
            break
        part.append(re.escape(route[:match.start()]))
        route = route[match.end():]
        parameter = match.group('parameter')
        if not parameter.isidentifier():
            raise Exception('URL route {} parameter isidentifier'.format(original_route))
        raw_converter = match.group('converter')
        if raw_converter is None:
            print('raw_converter', raw_converter)
            raw_converter = 'str'
        try:
            converter = get_converter(raw_converter)
            print('converters', converter)
        except KeyError as e:
            raise KeyError('URL route {} converter is invalid '.format(original_route))
        converters[parameter] = converter
        part.append('(?P<' + parameter + '>' + converter.regex + ')')
    print(converters)
    part.append('$')
    return ''.join(part), converters


def re_route(url_route, route_dict):
    """
    遍历注册的路由字典，通过_route_regex函数进行正则表达式转换，进行匹配

    :param url_route: 访问的路由
    :param route_dict: 注册的路由字典
    :return: 匹配到的路由和对应的参数字典
    """
    for route in route_dict:
        deal_route = '/' + route
        deal_route, converters = _route_regex(deal_route)
        deal_route = re.compile(deal_route)
        match = deal_route.search(url_route)
        if match is not None:
            kwargs = match.groupdict()
            for key, value in kwargs.items():
                kwargs[key] = converters[key].to_python(value)
            print(kwargs)
            return route, kwargs
    return None, {}

