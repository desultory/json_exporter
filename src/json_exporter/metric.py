"""
Basic prometheus metric class
"""

from enum import Enum

from zenlib.logging import loggify

from .labels import Labels


class MetricTypes(Enum):
    """
    Prometheus metric types
    """
    COUNTER = 'counter'
    GAUGE = 'gauge'
    UNTYPED = 'untyped'


@loggify
class Metric:
    """
    A class used to represent a prometheus metric.
    Labels can be added to the metric by passing a dictionary as the labels argument.
    The value defaults to 0.
    """
    metrics = {}

    def __init__(self, name, value=0, metric_type='untyped', help=None, labels=Labels(), *args, **kwargs):
        """
        Initialize the metric
        """
        if name in self.metrics:
            raise ValueError("Metric name already exists: %s" % name)

        self.name = name
        self.type = metric_type
        self.help = help
        self.labels = Labels(labels, logger=self.logger, _log_init=False)
        self.value = value
        self.metrics[name] = self

    def __setattr__(self, name, value):
        """
        Turn spaces in the name into underscores.
        Set the metric type based on the MetricTypes enum.
        Ensure that labels are a dictionary.
        """
        if name == 'name':
            value = value.replace(' ', '_')
        if name == 'type':
            value = MetricTypes[value.upper()]
        if name == 'value':
            if not isinstance(value, (int, float)):
                raise TypeError('Value must be an integer or float')

        super().__setattr__(name, value)

    def _build_label_str(self):
        """ Iterates over the labels and builds the label string """
        for name, value in self.labels.items():
            yield f'{name}="{value}"'

    def _get_label_str(self):
        """ Returns the label string based on the built compontents """
        return ",".join(self._build_label_str())

    def __str__(self):
        """
        String representation of the metric
        """
        if self.help:
            out_str = f'# HELP {self.name} {self.help}\n'
        else:
            out_str = ''

        out_str += f'# TYPE {self.name} {self.type.value}\n{self.name}'

        if self.labels:
            out_str = f"{out_str}{{{self._get_label_str()}}}"

        out_str += f' {self.value}'
        return out_str
