"""
Label class, used by both Metrics and Exporters
"""

from zenlib.logging import loggify


@loggify
class Labels(dict):
    def __init__(self, dict_items={}, **kwargs):
        """ Create a new Labels object from a dictionary """
        self.update(dict_items)

    def __setitem__(self, key, value):
        self._check_label(key, value)
        super().__setitem__(key, value)

    def update(self, new_labels):
        """ Updates the labels with the new labels """
        for key, value in new_labels.items():
            self[key] = value
            self.logger.debug("Added label %s=%s", key, value)

    def _check_label(self, name: str, value: str):
        """ Check that the label name and value are valid """
        # Check that the label name is a string
        if not isinstance(name, str):
            raise TypeError('Label names must be strings')

        # Check that the label name is not already defined
        if name in self:
            raise ValueError("Label is already defined: %s" % name)
        # Check that the label value is a string
        if not isinstance(value, str):
            raise TypeError('Label values must be strings')
