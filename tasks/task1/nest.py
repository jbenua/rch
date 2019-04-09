import json
import sys

from itertools import groupby


def group_by_key(items, nest_keys):
    return group_items(items, nest_keys, nest_keys)


def group_items(items, nest_keys, rest_keys):
    if not rest_keys:
        return items
    res = {}
    current_key, *rest = rest_keys
    for (key, values) in groupby(items, lambda x: x.get(current_key)):
        if not key:
            raise KeyError("`%s` is missing in some items" % current_key)
        if rest:
            res[key] = group_items(values, nest_keys, rest)
        else:
            res[key] = list(
                filter(lambda x: x, [{k: v[k] for k in v if k not in nest_keys}
                                     for v in values]))
            if not res[key]:
                return key
    return res


if __name__ == "__main__":
    nest_keys = sys.argv[1:]
    items = json.loads(sys.stdin.read())
    sys.stdout.write(json.dumps(group_by_key(items, nest_keys)))
