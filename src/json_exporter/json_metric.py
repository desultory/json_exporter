"""
JSON prometheus metric class
"""

from prometheus_exporter import Metric


class JSONMetric(Metric):
    """
    JSON prometheus metric class.
    """
    def __init__(self, name, json_data, json_path, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.data = json_data
        self.json_path = json_path

    def _get_value(self):
        """ Get value based on json request """
        data = self.data.copy()
        for portion in self.json_path.split('.'):
            data = data.get(portion)
        return data

    def __getattribute__(self, name):
        """ Get value based on json request """
        if name == 'value' and hasattr(self, 'data'):
            return self._get_value()

        return super().__getattribute__(name)
