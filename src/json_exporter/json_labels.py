"""
JSON label class.
Like a label, but resolves the value from json data
"""

from .labels import Labels


class JSONLabels(Labels):
    """
    JSON Labels class
    """
    def __init__(self, json_data, json_paths={}, **kwargs):
        super().__init__(**kwargs)
        self.data = json_data.copy()
        self.json_paths = json_paths

        # Create empty labels for each json path
        for name in self.json_paths:
            if name not in self:
                self[name] = self[name]

    def __getitem__(self, name):
        """
        Gets an item value based on the json_data and json_paths
        """
        if name not in self.json_paths:
            raise ValueError("JSON path not defined for: %s" % name)

        value = self.data.copy()
        for key in self.json_paths[name].split('.'):
            value = value[key]
        self.logger.debug("[%s]Resolved JSON data from path: %s -> %a" % (name, self.json_paths[name], value))
        return value

