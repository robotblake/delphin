import argparse
import csv
import os
import sys

import botocore.session
import sqlparse

DELPHIN_ROOT = os.path.dirname(os.path.abspath(__file__))

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output',
                        help='s3 path to output query results to (required)')
    parser.add_argument('-e', '--execute', default='-',
                        help='query to execute (required)')
    parser.add_argument('-d', '--database', default='default',
                        help='database to run query against (default: "default")')
    return parser

def get_client():
    session = botocore.session.get_session()
    session.set_config_variable('data_path', os.path.join(DELPHIN_ROOT, 'data'))
    return session.create_client('athena')

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = get_parser()
    opts = parser.parse_args(args)

    if not opts.output:
        parser.error('missing required argument: --output')

    if opts.execute == '-':
        execute = sys.stdin.read()
    else:
        execute = opts.execute

    client = get_client()

    for query in sqlparse.split(execute):
        if not query:
            continue

        result = client.run_query(
            Query=query,
            OutputLocation=opts.output,
            QueryExecutionContext={'Database': opts.database},
        )

        waiter = client.get_waiter('query_completed')
        waiter.wait(QueryExecutionId=result['QueryExecutionId'])

        paginator = client.get_paginator('get_query_results')
        iterator = paginator.paginate(QueryExecutionId=result['QueryExecutionId'])

        csvout = csv.writer(sys.stdout)
        for row in iterator.search('ResultSet.ResultRows[].Data'):
            csvout.writerow(row)
