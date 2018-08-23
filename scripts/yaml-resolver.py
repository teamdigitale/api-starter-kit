"""This script resolves references in a yaml file and dumps it
    removing all of them.

    It expects references are defined in `x-commons` object.
    This object will be removed before serialization.
"""
from __future__ import print_function
from sys import argv
import yaml
from six.moves.urllib.parse import urldefrag
from six.moves.urllib.request import urlopen
import logging
from collections import defaultdict
from os.path import join

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# Global variables used by the parser.
yaml_cache = {}
yaml_components = defaultdict(dict)

ROOT_NODE = object()
COMPONENTS_MAP = {
    "schema": "schemas",
    "headers": "headers",
    "parameters": "parameters"
}


def deepcopy(item):
    return yaml.load(yaml.dump(item))


def traverse(node, key=ROOT_NODE, parents=None, cb=print):
    """ Recursively call nested elements."""
    parents = parents[-4:] if parents else []
    if isinstance(node, (dict, list)):
        valuelist = node.items() if isinstance(node, dict) else enumerate(node)
        if key is not ROOT_NODE:
            parents.append(key)
        parents.append(node)
        for k, i in valuelist:
            traverse(i, k, parents, cb)
        return
    # Resolve HTTP references adding fragments
    # to 'schema', 'headers' or 'parameters'
    if key == '$ref' and node.startswith("http"):
        ancestor, needle = parents[-3:-1]
        # log.info(f"replacing: {needle} in {ancestor} with ref {node}")
        ancestor[needle] = cb(key, node)

        if needle in ('schema', 'headers', 'parameters'):
            host, fragment = urldefrag(node)
            fragment = fragment.strip("/")
            needle_alias = COMPONENTS_MAP[needle]
            yaml_components[needle_alias][fragment] = ancestor[needle]
        if isinstance(ancestor[needle], (dict, list)):
            traverse(ancestor[needle], key, parents, cb)
        if needle in ('schema', 'headers', 'parameters'):
            # Now the node is fully resolved. I can replace it with the
            # Deepcopy
            yaml_components[needle_alias][
                fragment] = deepcopy(ancestor[needle])
            ancestor[needle] = {"$ref": "#" +
                                join("/components", needle_alias, fragment)}


def test_traverse():
    oat = {
        'a': 1,
        'list_of_refs': [
            {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/sort'}
        ],
        'object': {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/sort'}
    }
    traverse(oat, cb=resolve_node)
    assert(oat == {'a': 1, 'list_of_refs': [{'name': 'sort', 'in': 'query', 'description': 'Sorting order', 'schema': {
           'type': 'string', 'example': '+name'}}], 'object': {'name': 'sort', 'in': 'query', 'description': 'Sorting order', 'schema': {'type': 'string', 'example': '+name'}}})
    print(oat)


def test_traverse_list():
    oat = [
        {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/sort'}
    ]
    traverse(oat, cb=resolve_node)
    assert(oat == [{'name': 'sort', 'in': 'query', 'description': 'Sorting order', 'schema': {
           'type': 'string', 'example': '+name'}}])
    print(oat)


def test_traverse_object():
    oas = {'components': {'parameters': {'limit': {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/limit'},
                                         'sort': {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/sort'}},
                          'headers': {'X-RateLimit-Limit': {'$ref': 'https://teamdigitale.github.io/openapi/headers/v3.yaml#/X-RateLimit-Limit'},
                                      'Retry-After': {'$ref': 'https://teamdigitale.github.io/openapi/headers/v3.yaml#/Retry-After'}},
                          }}
    traverse(oas, cb=resolve_node)
    print(yaml.dump(oas, default_flow_style=0))


def test_nested_reference():
    oat = {'400BadRequest': {
        '$ref': 'https://teamdigitale.github.io/openapi/responses/v3.yaml#/400BadRequest'}}
    traverse(oat, cb=resolve_node)
    assert 'schemas' in yaml_components
    assert 'Problem' in yaml_components['schemas']
    print(yaml.dump(oat, default_flow_style=0))


def get_yaml_reference(f, yaml_cache=None):
    # log.info(f"Downloading {f}")
    host, fragment = urldefrag(f)
    if host not in yaml_cache:
        yaml_cache[host] = urlopen(host).read()

    f_yaml = yaml.load(yaml_cache[host])
    if fragment.strip("/"):
        f_yaml = finddict(f_yaml, fragment.strip("/").split("/"))
    return f_yaml


def finddict(_dict, keys):
    # log.debug(f"search {keys} in {_dict}")
    p = _dict
    for k in keys:
        p = p[k]
    return p


def resolve_node(key, node):
    # log.info(f"Resolving {node}")
    _yaml = get_yaml_reference(node, yaml_cache=yaml_cache)
    return _yaml


def should_use_block(value):
    for c in u"\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


def my_represent_scalar(self, tag, value, style=None):
    if should_use_block(value):
        style = '|'
    else:
        style = self.default_style

    node = yaml.representer.ScalarNode(tag, value, style=style)
    if self.alias_key is not None:
        self.represented_objects[self.alias_key] = node
    return node


def main(src_file, dst_file):
    # Resolve references in yaml file.
    yaml.Dumper.ignore_aliases = lambda *args: True

    # Dump long lines as "|".
    yaml.representer.BaseRepresenter.represent_scalar = my_represent_scalar

    with open(src_file) as fh_src, open(dst_file, 'w') as fh_dst:
        ret = yaml.load(fh_src)

        # Resolve nodes.
        # TODO: this behavior could be customized eg.
        #  to strip some kind of nodes.
        traverse(ret, cb=resolve_node)

        # Remove x-commons containing references and aliases.
        if 'x-commons' in ret:
            del ret['x-commons']

        # Order yaml keys for a nice
        # dumping.
        yaml_keys = set(ret.keys())
        first_keys = [x for x in (
            'openapi', 'info',  'servers', 'tags', 'paths', 'components') if x in yaml_keys]
        remaining_keys = list(yaml_keys - set(first_keys))
        sorted_keys = first_keys + remaining_keys

        for k in sorted_keys:
            content = yaml.dump(
                {k: ret[k]}, default_flow_style=False, allow_unicode=True)
            fh_dst.write(content)


if __name__ == '__main__':
    try:
        progname, src_file, dst_file = argv
    except:
        raise SystemExit("usage: src_file.yaml.src dst_file.yaml", argv)

    main(src_file, dst_file)
