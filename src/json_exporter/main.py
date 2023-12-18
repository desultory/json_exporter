#!/usr/bin/env python3

from logging import getLogger, StreamHandler
from argparse import ArgumentParser

from json_exporter import JSONExporter

from zenlib.logging import ColorLognameFormatter


def main():
    argparser = ArgumentParser(prog='json_exporter', description='JSON Exporter for Prometheus')

    argparser.add_argument('-d', '--debug', action='store_true', help='Debug mode.')
    argparser.add_argument('-dd', '--verbose', action='store_true', help='Verbose debug mode.')

    argparser.add_argument('-v', '--version', action='store_true', help='Print the version and exit.')

    argparser.add_argument('-p', '--port', type=int, nargs='?', help='Port to listen on.')
    argparser.add_argument('-a', '--address', type=str, nargs='?', help='Address to listen on.')

    args = argparser.parse_args()

    if args.version:
        from importlib.metadata import version
        print(f"{__package__} {version(__package__)}")
        exit(0)

    logger = getLogger(__package__)

    if args.verbose:
        logger.setLevel(5)
        formatter = ColorLognameFormatter('%(levelname)s | %(name)-42s | %(message)s')
    elif args.debug:
        logger.setLevel(10)
        formatter = ColorLognameFormatter('%(levelname)s | %(name)-42s | %(message)s')
    else:
        logger.setLevel(20)
        formatter = ColorLognameFormatter()

    handler = StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    kwargs = {'logger': logger}

    if args.port:
        kwargs['port'] = args.port
    if args.address:
        kwargs['ip'] = args.address

    exporter = JSONExporter(**kwargs)
    exporter.serve_forever()


if __name__ == '__main__':
    main()
