
def create_model_class(name, fields):
    """This function creates model classes for api testing from the class name
    and a dictionary of fields."""
    def __init__(self, **kwargs):
        done = set()
        unexpected = []
        for entry, value in kwargs.items():
            if entry not in self.fields:
                unexpected.append(entry)
            setattr(self, entry, value)
            done.add(entry)
        missing = []
        for entry, value in self.fields.items():
            if entry not in done:
                if value is True:
                    # A required field
                    missing.append(entry)
                else:
                    # An optional field, set to None
                    setattr(self, entry, None)

        error_message = ''
        if unexpected:
            error_message = 'Unexpected fields "{}" for type {}'.format(', '.join(unexpected), name)
        if missing:
            error_message += 'Expected fields "{}" for type {}'.format(', '.join(missing), name)
        if error_message:
            raise Exception(error_message)

    def __repr__(self):
        data = []
        try:
            if "name" in fields and self.name is not None:
                data.append('name={!r}'.format(self.name))
        except AttributeError:
            # Can happen if an exception occurs in __init__
            pass
        try:
            if "id" in fields and self.id is not None:
                data.append('id={!r}'.format(self.id))
        except AttributeError:
            # Can happen if an exception occurs in __init__
            pass
        try:
            if "title" in fields and self.title is not None:
                data.append('title={!r}'.format(self.title))
        except AttributeError:
            # Can happen if an exception occurs in __init__
            pass

        return '{}({})'.format(name, ', '.join(data))

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        for field in self.fields:
            if field == 'id' and getattr(self, 'id', None) is None or getattr(other, 'id', None) is None:
                # This enables manually constructed model objects to be compared to those with an id
                continue
            if getattr(self, field) != getattr(other, field):
                return False
        return True

    body = {'__eq__': __eq__, '__init__': __init__, '__repr__': __repr__, "fields": fields}
    return type(name, (object,), body)
