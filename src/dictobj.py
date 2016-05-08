class DictObj(dict):
    """
    Dictionary like object - means you can act like it is dictionary or access
    attributes by dot notation - obj.attr.sub_attr...
    """
    def __init__(self, data=None):
        if data is None:
            data = {}
        super(DictObj, self).__init__(data)  # init dict
        for i, j in self.items():
            if isinstance(j, dict):
                self[i] = DictObj(j)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    @staticmethod
    def recursive_merge(orig, new):
        """
        Recoursively merge two dictionaries

        update `orig` values with `new` but when some item is dictionary,
        merge it recursively, instead of replace - means only scalars are
        replaced

        Parameters
        ----------
        orig: dict
            original values
        new: dict
            new values which replace origs

        Returns
        -------
        dict
            merged data

        Raises
        ------
        ValueError
            when arguments are not dictionaries
        """
        if not isinstance(orig, dict) or not isinstance(new, dict):
            raise ValueError("orig and new data should be dictionaries")

        data = orig.copy()
        data.update(new)  # this replace whole inner dicts
        for i in new:
            # new item to config
            if i not in orig:
                continue
            # replacing dict with dict - do it recursively
            if isinstance(new[i], dict) and isinstance(orig[i], dict):
                data[i] = DictObj.recursive_merge(orig[i], new[i])
        return data


def dictobj(*args, **kwargs):
    """
    create `DictObj` like dict function
    """
    return DictObj(dict(*args, **kwargs))

