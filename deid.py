"""Deidre Deid Script.
Usage:
  runner.py --schemas=<file> --mappings=<file> --input=<dir> --output=<dir>
  runner.py (-h | --help)
  runner.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --schemas=<file>  JSON Schema file
  --mappings=<file>  JSON Schema-Mapping file
  --input=<dir> Directory to read files from
  --output=<dir> Directory to write files into

"""

import re
import sys
from os import listdir
from os.path import isfile, join

from docopt import docopt
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from deidre import *


def main(args):
    schemas = {}
    mappings = {}

    for filename in args['--schemas'].split(','):
        schema_dict = load_json(filename)
        fix_schema(schema_dict)
        # print(json.dumps(schema_dict, indent=2))

        datamodel = re.findall(r"/(\w+)-", filename)[0]
        print(f'processing DataModel Schema "{datamodel}"')
        schemas[datamodel] = schema_dict

    for filename in args['--mappings'].split(','):
        mapping_dict = load_json(filename)

        datamodel = re.findall(r"/(\w+)-", filename)[0]
        print(f'processing DataModel Mapping "{datamodel}"')
        mappings[datamodel] = mapping_dict

    if sorted(schemas.keys()) != sorted(mappings.keys()):
        print(f'schemas {schemas.keys()} and '
              f'mappings {mappings.keys()} do not match')
        exit(0)

    faker = redox_faker()

    input_path = args['--input']
    count = 0
    emoji = ['\U0001F648', '\U0001F649', '\U0001F64A']

    print(
        f"count: {len([name for name in listdir(input_path) if isfile(join(input_path, name))])}")

    print('Processing files: ')
    for f in listdir(input_path):
        if not (isfile(join(input_path, f)) and f.endswith('.json')):
            continue

        filepath = f'{input_path}/{f}'
        # print(f'processing: {filepath}')
        input_dict = load_json(f'{filepath}')
        datamodel = input_dict.get('Meta', {}).get('DataModel', '').lower()

        schema = schemas.get(datamodel)
        if not schema:
            print(f'Datamodel "{datamodel}" '
                  f'could not be found in schemas for {filepath}')
            continue

        mapping = mappings.get(datamodel)
        if not mapping:
            print(f'Datamodel "{datamodel}" '
                  f'could not be found in mappings for {filepath}.')
            continue

        try:
            validate(input_dict, schema)
        except ValidationError as e:
            print(f'Validation error "{filename}" {e}')
            continue

        paths = generate_paths(schema)

        output_dict = process_all_paths(faker, input_dict, mapping,
                                        paths)

        output_filename = f"{args['--output']}/" \
                          f"{f.replace('.json', '_deid.json')}"
        write_json(output_filename, output_dict)
        count += 1
        print(emoji[count % 2], end='')
        sys.stdout.flush()
        if count % 100 == 0:
            print(f"\U0001F389{count}\U0001F389")
        # print(f"done: {output_filename}")
    print('')
    sys.stdout.flush()


if __name__ == '__main__':
    main(docopt(__doc__, version='Deidre Deid 0.1'))
