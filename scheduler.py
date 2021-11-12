#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation
import uuid

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import os
import csv

from tiger.metadata import Metadata
from tiger.report import Report
from tiger.slackclient import SlackClient

ENDPOINT = 'https://hackaton.anywhere.gooddata.com'
TOKEN = os.environ.get('TIGER_API_TOKEN')
WORKSPACE_ID = 'demo'
TARGET_CHANNEL_ID = 'C02M4PF2R8C'
THRESHOLD = 1000000
DATA_SOURCE_ID = 'pg_staging-demo'

# Initialize a Web API client
slack_client = SlackClient()
metadata_client = Metadata(ENDPOINT, TOKEN)
metadata_client.workspace_id = WORKSPACE_ID


def alert():
    print("Alert processing START. The time is: %s" % datetime.now())
    report_client = Report(ENDPOINT, TOKEN, WORKSPACE_ID, metadata_client)
    df = report_client.execute(
        [{'id': 'metric/revenue', 'short_id': 'revenue', 'title': 'Revenue'}],
        [{'id': 'label/customers.region', 'short_id': 'customers.region', 'title': 'Region'}]
    )
    print(f'Upload notification - invalid caches for DS {DATA_SOURCE_ID}')
    metadata_client.invalid_caches(DATA_SOURCE_ID)

    print(f'Execute report ...')
    base_path = '/tmp/' + str(uuid.uuid4())
    file_path = base_path + '.csv'
    with open(file_path, 'wt') as fd:
        df.to_csv(fd, index=False)

    print(f'Evaluate alerts ...')
    with open(file_path) as fp:
        data = csv.reader(fp)
        i = 1
        for row in data:
            if i > 1:
                if float(row[1]) > THRESHOLD:
                    msg = f'Region {row[0]} achieved {THRESHOLD} revenue, congratz!\n'
                    print(msg)
                    slack_client.send_markdown_message(
                        TARGET_CHANNEL_ID, [msg]
                    )
    print("Alert processing END. The time is: %s" % datetime.now())


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Europe/Prague")
    scheduler.add_job(alert, 'interval', seconds=30)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass