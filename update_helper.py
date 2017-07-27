__version__ = '0.0.1'
import collections
from copy import deepcopy


class UpdateHelper(object):
    def apply_action_to_obj(self, action, obj):
        target, command, *params = action
        prev_val, key, setter, deleter = self._get_nested(obj, target)
        if command == '$unset':
            deleter(key)
        else:
            handler = getattr(self, '_' + command.lstrip('$'))
            next_val = handler(prev_val, *params)
            setter(key, next_val)

    def _get_nested(self, obj, target):
        parent = obj
        tokens = target.split(".")
        key = tokens[0]
        for token in tokens[:-1]:
            try:
                parent = self._get_attr_or_item(obj=parent, key=token)
            except KeyError:
                next_parent = {}
                try:
                    parent[token] = next_parent
                except TypeError:
                    setattr(parent, token, next_parent)
                parent = next_parent
        key = tokens[-1]
        if isinstance(parent, collections.abc.MutableMapping):
            def setter(key, value): parent[key] = value
            def deleter(key): del parent[key] # noqa
            prev_value = parent.get(key)
        else:
            def setter(key, value): setattr(parent, key, value)
            def deleter(key): del parent.key # noqa
            prev_value = getattr(parent, key, None)
        return prev_value, key, setter, deleter

    def _get_attr_or_item(self, obj=None, key=None):
        if isinstance(key, str) and key.endswith('()'):
            return self._get_attr_or_item(obj, key[:-2])()
        for type_ in ['sequence', 'mapping', 'mapping_view', 'attr']:
            try:
                return getattr(self, '_get_from_' + type_)(obj, key)
            except:
                pass
        raise KeyError(key)

    def _get_from_sequence(self, obj=None, key=None):
        if isinstance(obj, collections.abc.Sequence):
            return obj[int(key)]
        raise Exception("Not a sequence")

    def _get_from_mapping(self, obj=None, key=None):
        if isinstance(obj, collections.abc.Mapping):
            return obj[key]
        raise Exception("Not a mapping")

    def _get_from_mapping_view(self, obj=None, key=None):
        if isinstance(obj, collections.abc.MappingView):
            return list(obj)[int(key)]
        raise Exception("Not a mapping_view")

    def _get_from_attr(self, obj=None, key=None):
        if hasattr(obj, key):
            return getattr(obj, key)
        raise Exception("Does not have attr")

    def _add(self, prev_val, n): return prev_val + n

    def _mul(self, prev_val, n): return prev_val * n

    def _set(self, prev_val, value): return value

    def _shift(self, prev_val): return prev_val[1:]

    def _unshift(self, prev_val, values): return values + prev_val

    def _splice(self, prev_val, splice_spec):
        start = splice_spec.get('start')
        if start == 0:
            left = []
        else:
            left = prev_val[:start]
        right = prev_val[start + splice_spec.get('delete_count', 0):]
        return left + splice_spec.get('new_items', []) + right

    def _merge(self, prev_val, new_items):
        next_val = {**prev_val}
        for k, v in new_items.items():
            next_val[k] = v
        return next_val

    def _push(self, prev_val, new_items): return prev_val + new_items

    def _pop(self, prev_val): return prev_val[:-1]

    def _omit(self, prev_val, keys_to_omit):
        return {k: v for k, v in prev_val.items() if k not in keys_to_omit}

    def _addToSet(self, prev_val, values):
        next_val = [*prev_val]
        for value in values:
            if value not in next_val:
                next_val.append(value)
        return next_val

    def _rename(self, prev_val, rename_spec):
        next_val = {**prev_val}
        prev_name, next_name = rename_spec
        next_val[next_name] = next_val[prev_name]
        del next_val[prev_name]
        return next_val


update_helper = UpdateHelper()


def update(obj, actions, copy=False):
    if copy:
        obj = deepcopy(obj)
    for action in actions:
        update_helper.apply_action_to_obj(action, obj)
    return obj
