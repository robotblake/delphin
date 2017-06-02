import argparse
import csv
import os
import sys
import time

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
    return session.create_client('athena')

def submit_query(client, database, output, query):
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': database},
        ResultConfiguration={'OutputLocation': output},
    )
    return response['QueryExecutionId']

def wait_for_completion(client, query_id):
    while True:
        response = client.get_query_execution(QueryExecutionId=query_id)
        state = response['QueryExecution']['Status']['State']
        if state == 'FAILED':
            reason = response['QueryExecution']['Status']['StateChangeReason']
            raise RuntimeError('Query failed: %s'.format(reason))
        elif state == 'CANCELLED':
            raise RuntimeError('Query canceled')
        elif state == 'SUCCEEDED':
            break
        else:
            time.sleep(10)

def get_rows(client, query_id):
    response = client.get_query_results(QueryExecutionId=query_id)
    while True:
        for row in response['ResultSet']['Rows']:
            yield [field['VarCharValue'] for field in row['Data']]
        if 'NextToken' in response:
            response = client.get_query_results(QueryExecutionId=query_id, NextToken=response['NextToken'])
        else:
            break

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

        query_id = submit_query(client, opts.database, opts.output, query)

        wait_for_completion(client, query_id)

        csvout = csv.writer(sys.stdout)
        for row in get_rows(client, query_id):
            csvout.writerow(row)
