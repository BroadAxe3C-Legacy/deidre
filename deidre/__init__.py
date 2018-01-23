import inspect
import json
import time
from collections import defaultdict

from faker import Faker
from jsonpointer import resolve_pointer, JsonPointerException

from deidre.providers import RedoxPersonProvider, RedoxAddressProvider, \
    RedoxRandomProvider, RedoxLoremProvider, RedoxCompanyProvider, \
    RedoxPhoneProvider


def load_json(filename):
    """load a json file from the input argument array."""
    with open(filename) as f:
        return json.load(f)


def write_json(filename, src_dict):
    """write a json file from a dict."""
    with open(filename, 'w') as f:
        return json.dump(src_dict, f, indent=2)


def nested_dict():
    return defaultdict(nested_dict)


def redox_faker():
    faker = Faker()
    faker.add_provider(RedoxAddressProvider)
    faker.add_provider(RedoxPersonProvider)
    faker.add_provider(RedoxRandomProvider)
    faker.add_provider(RedoxPhoneProvider)
    faker.add_provider(RedoxCompanyProvider)
    faker.add_provider(RedoxLoremProvider)
    return faker


def fix_schema(data):
    """Fix incorrect json schema elements that don't allow null, but
       have null values in the json documents."""
    if isinstance(data, dict):
        for key, val in data.items():
            if key == 'type':
                if val in ['string', 'number', 'boolean']:
                    data[key] = [val, 'null']
            else:
                fix_schema(val)
    elif isinstance(data, list):
        for element in data:
            fix_schema(element)


def generate_paths(data, path=''):
    """Iterate the json schema file and generate a list of all of the
    XPath-like expression for each primitive value. An asterisk * represents
    an array of items."""
    paths = []
    if isinstance(data, dict):
        if len(data) == 0:
            paths.append(f'{path}')
        else:
            for key, val in data.items():
                if key == 'type':
                    if isinstance(val, list):
                        types = set(val)
                    else:
                        types = {val}
                    if types.isdisjoint({'object', 'array'}):
                        paths.append(f'{path}')
                elif key == 'properties':
                    paths.extend(generate_paths(val, path))
                else:
                    if key == 'items':
                        key = '*'
                    paths.extend(generate_paths(val, f'{path}/{key}'))
    return paths


def is_int(s):
    """Is this string an int? Use for detecting array indexes in paths."""
    try:
        int(s)
        return True
    except ValueError:
        return False


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('%r %2.2f sec (%r, %r) ' % (method.__name__, te - ts,
                                          args, kw,))
        return result

    return timed


def method_name_for_path(mapping, path):
    """Lookup the method name to call on Faker to generate data for
       the indicated path."""
    for element in (x for x in path.split('/') if len(x) > 0):
        if element == '*':
            mapping = mapping.get('items', {})
        else:
            mapping = mapping.get('properties', {}).get(element, {})
    method_name = mapping.get('type', None)
    if method_name == 'identity' \
            and path.endswith('/ID') \
            and not path.startswith('/Meta/'):
        raise ValueError(
            f"method 'identity' is not allowed for ID in '{path}'")
    if method_name in ['object', 'array', 'string', 'null', 'numeric',
                       'boolean', 'integer']:
        raise ValueError(
            f"method '{method_name}' was not redefined for path '{path}'")
    return method_name


def deep_put(data, path, value):
    """Put the value of the path in the data (dict) to the value. If
       intermediate structures (e.g., dicts) don't exist, create them."""
    path_elements = [x for x in path.split('/') if len(x) > 0]
    for idx, element in enumerate(path_elements):
        if idx < len(path_elements) - 1:
            if is_int(path_elements[idx + 1]):
                if data.get(element, None) is None:
                    data[element] = []
                data = data[element]
            elif is_int(element):
                next_data = None
                if int(element) < len(data):
                    next_data = data[int(element)]
                if not next_data:
                    next_data = nested_dict()
                    data.append(next_data)
                data = next_data
            else:
                data = data[element]
        else:
            if isinstance(data, list):
                data.append(value)
            else:
                data[element] = value


def process_path(path, input_dict, output_dict, method_mapping_dict, faker):
    """process a single path"""
    map_method = method_name_for_path(method_mapping_dict, path)
    # print(f'{path} => {map_method}')

    # todo fix
    if not map_method:
        map_method = 'lorem_short'

    map_method_elements = map_method.rstrip(')').split('(')

    method = lookup_method(faker, map_method_elements[0], map_method, path)

    value = None
    param_count = len(inspect.signature(method).parameters)
    if len(map_method_elements[1:]) > param_count:
        raise ValueError('oops')

    set_path_value(path, input_dict, output_dict, map_method_elements,
                   method, param_count, value)


def lookup_method(faker, map_method_element, map_method, path):
    """Lookup the method in Faker for generating the new value(s)"""
    try:
        method = getattr(faker, map_method_element)
    except TypeError as e:
        print(f'error getting map method "{map_method}" for path "{path}"')
        raise e
    except AttributeError as e:
        print(
            f'map method not found "{map_method_element}" for path "{path}"')
        raise e
    return method


def set_path_value(path, input_dict, output_dict, map_method_elements,
                   method, param_count, value):
    """Set the value for a single path"""
    try:
        if '*' in path:
            segments = path.split('/*', 1)
            array_size = len(resolve_pointer(input_dict, segments[0]))
            if array_size == 0:
                set_path_value(segments[0], input_dict, output_dict,
                               map_method_elements, lambda x: x, 1, [])
            else:
                for i in range(array_size):
                    set_path_value(f'/{i}'.join(segments), input_dict,
                                   output_dict,
                                   map_method_elements, method, param_count,
                                   value)
        else:
            # print('processing: ' + path)
            if param_count == 0:
                value = method()
            elif param_count == 1:
                value = method(resolve_pointer(input_dict, path))
            elif len(map_method_elements[1:]) == 1:
                second_arg = resolve_pointer(output_dict,
                                             path[:path.rfind('/') + 1] +
                                             map_method_elements[1])
                value = method(resolve_pointer(input_dict, path), second_arg
                               )
            deep_put(output_dict, path, value)
    except JsonPointerException:
        # todo: bug in source files
        # 1) several /Visit paths, including /Visit/ReferringProvider/IDType
        # 2) missing /Observations/*/Status
        if (not path.startswith('/Visit/')
            and not (path.startswith('/Observations')
                     and path.endswith('/Status'))):
            print(f'path could not be generated: {path}')
        pass


# @timeit
def process_all_paths(faker, input_dict, method_mapping_dict,
                      paths):
    output_dict = nested_dict()
    for path in paths:
        process_path(path, input_dict, output_dict, method_mapping_dict, faker)
    return output_dict
