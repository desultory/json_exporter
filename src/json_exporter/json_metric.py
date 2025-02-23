from prometheus_exporter import Metric


class JSONMetric(Metric):
    """ JSON prometheus metric class. """
    def __init__(self, name, json_data, json_path, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.data = json_data
        self.json_path = json_path

    def _value(self):
        """ Get value based on json request """
        if data := self.data:
            data = data.copy()
            for portion in self.json_path.split('.'):
                if d := data.get(portion):
                    data = d
                else:
                    self.logger.debug("Data: %s", data)
                    return self.logger.warning("JSON path not found: %s", self.json_path)
            return data
