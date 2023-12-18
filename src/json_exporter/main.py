#!/usr/bin/env python3

from json_exporter import JSONExporter

from logging import getLogger, StreamHandler
from zenlib.logging import ColorLognameFormatter


def main():
    logger = getLogger(__name__)
    handler = StreamHandler()
    handler.setFormatter(ColorLognameFormatter('%(levelname)s | %(name)-42s | %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(20)

    exporter = JSONExporter(logger=logger)
    exporter.serve_forever()


if __name__ == '__main__':
    main()
