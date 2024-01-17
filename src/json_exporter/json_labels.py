"""
JSON label class.
Like Labels, but resolves the value from json data.
"""

from prometheus_exporter import Labels


class JSONLabels(Labels):
    """
    JSON Labels class

    Each JSONLabels must be defined with JSON Data and JSON Paths.
    The JSON data is the data used to pull data from.
    The JSON Paths is a dictionary of label names, where the value
    is the path to the data in the JSON data, separated by periods.
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
        """ Gets an item value based on the json_data and json_paths """
        if name not in self.json_paths:
            raise ValueError("JSON path not defined for: %s" % name)

        value = self.data.copy()
        for key in self.json_paths[name].split('.'):
            try:
                value = value[key]
            except KeyError:
                self.logger.warning("Unable to resolve JSON path: %s" % self.json_paths[name])
                self.logger.debug("JSON data: %a" % self.data)
        self.logger.debug("[%s]Resolved JSON data from path: %s -> %a" % (name, self.json_paths[name], value))
        return value

