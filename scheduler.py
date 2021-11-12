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

# Initialize a Web API client
slack_client = SlackClient()
metadata_client = Metadata(ENDPOINT, TOKEN)
metadata_client.workspace_id = WORKSPACE_ID


def tick():
    report_client = Report(ENDPOINT, TOKEN, WORKSPACE_ID, metadata_client)
    df = report_client.execute(
        [{'id': 'metric/revenue', 'short_id': 'revenue', 'title': 'Revenue'}],
        [{'id': 'label/customers.region', 'short_id': 'customers.region', 'title': 'Region'}]
    )
    base_path = '/tmp/' + str(uuid.uuid4())
    file_path = base_path + '.csv'
    with open(file_path, 'wt') as fd:
        df.to_csv(fd, index=False)

    data = csv.reader(file_path)
    print(data)
    print("Tick. The time is: %s" % datetime.now())


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Europe/Prague")
    scheduler.add_job(tick, 'interval', seconds=30)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass