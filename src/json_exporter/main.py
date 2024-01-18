#!/usr/bin/env python3

from json_exporter import JSONExporter
from zenlib.util import init_logger, init_argparser, process_args


def main():
    logger = init_logger(__package__)
    argparser = init_argparser(prog=__package__, description='JSON Exporter for Prometheus')

    argparser.add_argument('-p', '--port', type=int, nargs='?', help='Port to listen on.')
    argparser.add_argument('-a', '--address', type=str, nargs='?', help='Address to listen on.')

    args = process_args(argparser, logger=logger)

    kwargs = {'logger': logger}

    if args.port:
        kwargs['listen_port'] = args.port
    if args.address:
        kwargs['listen_ip'] = args.address

    exporter = JSONExporter(**kwargs)
    exporter.start()


if __name__ == '__main__':
    main()
