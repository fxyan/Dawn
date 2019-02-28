class IntConverter:
    regex = '[0-9]+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return str(value)


class StrConverter:
    regex = '[^/]+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)


DEFAULT_CONVERTERS = {
    'int': IntConverter(),
    'str': StrConverter(),
}

REGISTERED_CONVERTERS = {}


def register_converter(converter, type_name):
    REGISTERED_CONVERTERS[type_name] = converter()


def get_converters():
    converters = {}
    converters.update(DEFAULT_CONVERTERS)
    converters.update(REGISTERED_CONVERTERS)
    return converters


def get_converter(converter):
    return get_converters()[converter]
