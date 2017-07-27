__version__ = '0.0.1'
from copy import deepcopy


class UpdateHelper(object):
    def apply_action_to_obj(self, action, obj):
        target, command, *params = action
        parent, key = self._get_nested(obj, target)
        handler = getattr(self, '_' + command.lstrip('$'))
        handler(parent, key, *params)

    def _get_nested(self, obj, target):
        parent = obj
        tokens = target.split(".")
        for token in tokens[:-1]:
            if token not in parent:
                parent[token] = {}
            parent = parent[token]
        return parent, tokens[-1]

    def _add(self, parent, key, n):
        parent[key] += n

    def _mul(self, parent, key, n):
        parent[key] *= n

    def _set(self, parent, key, value):
        parent[key] = value

    def _unset(self, parent, key):
        del parent[key]

    def _shift(self, parent, key):
        parent[key] = parent[key][1:]

    def _unshift(self, parent, key, values):
        parent[key] = values + parent[key]

    def _splice(self, parent, key, splice_spec):
        start = splice_spec.get('start')
        if start == 0:
            left = []
        else:
            left = parent[key][:start]
        right = parent[key][start + splice_spec.get('delete_count', 0):]
        parent[key] = left + splice_spec.get('new_items', []) + right

    def _merge(self, parent, key, new_items):
        for k, v in new_items.items():
            parent[key][k] = v

    def _push(self, parent, key, new_items):
        parent[key] += new_items

    def _pop(self, parent, key):
        parent[key] = parent[key][:-1]

    def _omit(self, parent, key, keys_to_omit):
        parent[key] = {k: v for k, v in parent[key].items()
                       if k not in keys_to_omit}

    def _addToSet(self, parent, key, values):
        for value in values:
            if value not in parent[key]:
                parent[key].append(value)

    def _rename(self, parent, key, rename_spec):
        prev_name, next_name = rename_spec
        parent[key][next_name] = parent[key][prev_name]
        del parent[key][prev_name]


update_helper = UpdateHelper()


def update(obj, actions, copy=False):
    if copy:
        obj = deepcopy(obj)
    for action in actions:
        update_helper.apply_action_to_obj(action, obj)
    return obj
