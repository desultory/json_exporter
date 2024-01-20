#!/usr/bin/env python3

from json_exporter import JSONExporter
from zenlib.util import get_kwargs
from prometheus_exporter import DEFAULT_EXPORTER_ARGS


def main():
    kwargs = get_kwargs(package=__package__, description='JSON Exporter for Prometheus',
                        arguments=DEFAULT_EXPORTER_ARGS)

    exporter = JSONExporter(**kwargs)
    exporter.start()


if __name__ == '__main__':
    main()
