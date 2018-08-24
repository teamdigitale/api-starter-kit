"""This script resolves references in a yaml file and dumps it
    removing all of them.

    It expects references are defined in `x-commons` object.
    This object will be removed before serialization.
"""
from __future__ import print_function
from sys import argv, stdout
import yaml
from six.moves.urllib.parse import urldefrag
from six.moves.urllib.request import urlopen
import logging
from collections import defaultdict
from os.path import join

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()


ROOT_NODE = object()
COMPONENTS_MAP = {
    "schema": "schemas",
    "headers": "headers",
    "parameters": "parameters"
}


def deepcopy(item):
    return yaml.safe_load(yaml.safe_dump(item))


def finddict(_dict, keys):
    # log.debug(f"search {keys} in {_dict}")
    p = _dict
    for k in keys:
        p = p[k]
    return p


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


class OpenapiResolver(object):
    """Resolves an OpenAPI v3 spec file replacing
       yaml-references and json-$ref from 
       the web.
    """

    def __init__(self, openapi):
        self.openapi = deepcopy(openapi)
        # Global variables used by the parser.
        self.yaml_cache = {}
        self.yaml_components = defaultdict(dict)

    def resolve(self):
        self.traverse(self.openapi, cb=self.resolve_node)
        return self.openapi

    def traverse(self, node, key=ROOT_NODE, parents=None, cb=print):
        """ Recursively call nested elements."""

        # Trim parents breadcrumb as 4 will suffice.
        parents = parents[-4:] if parents else []

        # Unwind items as a dict or an enumerated list
        # to simplify traversal.
        if isinstance(node, (dict, list)):
            valuelist = node.items() if isinstance(node, dict) else enumerate(node)
            if key is not ROOT_NODE:
                parents.append(key)
            parents.append(node)
            for k, i in valuelist:
                self.traverse(i, k, parents, cb)
            return

        # Resolve HTTP references adding fragments
        # to 'schema', 'headers' or 'parameters'
        if key == '$ref' and node.startswith("http"):
            ancestor, needle = parents[-3:-1]
            # log.info(f"replacing: {needle} in {ancestor} with ref {node}")
            ancestor[needle] = cb(key, node)

            # Use a pre and post traversal functions.
            # - before: append the reference to yaml_components
            # - traverse
            # - after: deepcopy the resulting item in the yaml_components
            #          then replace it with the reference in the specs
            if needle in COMPONENTS_MAP:
                host, fragment = urldefrag(node)
                fragment = fragment.strip("/")
                needle_alias = COMPONENTS_MAP[needle]
                self.yaml_components[needle_alias][fragment] = ancestor[needle]
            if isinstance(ancestor[needle], (dict, list)):
                self.traverse(ancestor[needle], key, parents, cb)
            if needle in COMPONENTS_MAP:
                # Now the node is fully resolved. I can replace it with the
                # Deepcopy
                self.yaml_components[needle_alias][
                    fragment] = deepcopy(ancestor[needle])
                ancestor[needle] = {"$ref": "#" +
                                    join("/components", needle_alias, fragment)}

    def get_yaml_reference(self, f):
        # log.info(f"Downloading {f}")
        host, fragment = urldefrag(f)
        if host not in self.yaml_cache:
            self.yaml_cache[host] = urlopen(host).read()

        f_yaml = yaml.safe_load(self.yaml_cache[host])
        if fragment.strip("/"):
            f_yaml = finddict(
                f_yaml, fragment.strip("/").split("/"))
        return f_yaml

    def resolve_node(self, key, node):
        # log.info(f"Resolving {node}")
        _yaml = self.get_yaml_reference(node)
        return _yaml

    def dump(self, remove_tags=('x-commons',)):
        openapi_tags = ('openapi', 'info',  'servers',
                        'tags', 'paths', 'components')

        # Resolve references in yaml file.
        yaml.Dumper.ignore_aliases = lambda *args: True

        # Dump long lines as "|".
        yaml.representer.BaseRepresenter.represent_scalar = my_represent_scalar

        openapi = deepcopy(self.openapi)

        # If it's not a dict, just dump the standard yaml
        if not isinstance(openapi, dict):
            return yaml.safe_dump(openapi, default_flow_style=False, allow_unicode=True)

        # Eventually remove some tags, eg. containing references and aliases.
        for tag in remove_tags:
            if tag in openapi:
                del openapi[tag]

        # Order yaml keys for a nice
        # dumping.
        yaml_keys = set(openapi.keys())
        first_keys = [x for x in openapi_tags if x in yaml_keys]
        remaining_keys = list(yaml_keys - set(first_keys))
        sorted_keys = first_keys + remaining_keys

        content = ""
        for k in sorted_keys:
            content += yaml.safe_dump(
                {k: openapi[k]}, default_flow_style=False, allow_unicode=True)

        return content


def test_traverse():
    oat = {
        'a': 1,
        'list_of_refs': [
            {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/sort'}
        ],
        'object': {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/sort'}
    }
    resolver = OpenapiResolver(oat)
    ret = resolver.resolve()
    assert(ret == {'a': 1, 'list_of_refs': [{'name': 'sort', 'in': 'query', 'description': 'Sorting order', 'schema': {
           'type': 'string', 'example': '+name'}}], 'object': {'name': 'sort', 'in': 'query', 'description': 'Sorting order', 'schema': {'type': 'string', 'example': '+name'}}})
    print(resolver.dump())


def test_traverse_list():
    oat = [
        {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/sort'}
    ]
    resolver = OpenapiResolver(oat)
    ret = resolver.resolve()
    assert(ret == [{'name': 'sort', 'in': 'query', 'description': 'Sorting order', 'schema': {
           'type': 'string', 'example': '+name'}}])
    print(resolver.dump())


def test_traverse_object():
    oas = {'components': {'parameters': {'limit': {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/limit'},
                                         'sort': {'$ref': 'https://teamdigitale.github.io/openapi/parameters/v3.yaml#/sort'}},
                          'headers': {'X-RateLimit-Limit': {'$ref': 'https://teamdigitale.github.io/openapi/headers/v3.yaml#/X-RateLimit-Limit'},
                                      'Retry-After': {'$ref': 'https://teamdigitale.github.io/openapi/headers/v3.yaml#/Retry-After'}},
                          }}
    resolver = OpenapiResolver(oas)
    ret = resolver.resolve()
    print(resolver.dump())


def test_nested_reference():
    oat = {'400BadRequest': {
        '$ref': 'https://teamdigitale.github.io/openapi/responses/v3.yaml#/400BadRequest'}}
    resolver = OpenapiResolver(oat)
    resolver.resolve()
    assert 'schemas' in resolver.yaml_components
    assert 'Problem' in resolver.yaml_components['schemas']
    print(resolver.dump())


def test_dump():
    oat = {
        'openapi': '3.0.1',
        'x-commons': {},
        'components': {
            'responses': {
                '400BadRequest': {
                    '$ref': 'https://teamdigitale.github.io/openapi/responses/v3.yaml#/400BadRequest'
                }
            }
        }
            
    }
    resolver = OpenapiResolver(oat)
    resolver.resolve()
    assert '400BadRequest:' in resolver.dump()
    assert 'x-commons' not in resolver.dump()


def main(src_file, dst_file):

    with open(src_file) as fh_src, open(dst_file, 'w') as fh_dst:
        ret = yaml.safe_load(fh_src)

        # Resolve nodes.
        # TODO: this behavior could be customized eg.
        #  to strip some kind of nodes.
        resolver = OpenapiResolver(ret)
        resolver.resolve()

        # Serialize file.
        fh_dst.write(resolver.dump())


if __name__ == '__main__':
    try:
        progname, src_file, *dst_file = argv
    except:
        raise SystemExit("usage: src_file.yaml.src dst_file.yaml", argv)

    if not dst_file:
        dst_file = '/dev/stdout'

    main(src_file, dst_file)
