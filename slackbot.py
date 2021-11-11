#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

import os
import re
import uuid
from flask import Flask
from slackeventsapi import SlackEventAdapter
from tabulate import tabulate
from coinbot import CoinBot
from tiger.report import Report
from tiger.slackclient import SlackClient
from tiger.metadata import Metadata
import yaml


ENDPOINT = 'https://hackaton.anywhere.gooddata.com'
TOKEN = os.environ.get('TIGER_API_TOKEN')

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
# Create an events adapter and register it to an endpoint in the slack app for event ingestion.
slack_events_adapter = SlackEventAdapter(os.environ.get("SLACK_EVENTS_TOKEN"), "/slack/events", app)

# Initialize a Web API client
slack_client = SlackClient()


def read_config_from_file(config_file):
    with open(config_file) as fp:
        return yaml.safe_load(fp)


def flip_coin(channel):
    """Craft the CoinBot, flip the coin and send the message to the channel
    """
    # Create a new CoinBot
    coin_bot = CoinBot()
    slack_client.send_markdown_message(channel, [coin_bot.COIN_START_BLOCK, coin_bot.flip_coin()])


def slap_the_slackbot(channel):
    slack_client.send_markdown_message(channel, ["Zmlkni Slackbote!\n"])


@slack_events_adapter.on("message")
def message(payload):
    print(f"Event: message, payload: {payload}")

    # Get the event data from the payload
    event = payload.get("event", {})

    # Get the text from the event that came through
    text = event.get("text")
    if text:
        text = text.lower()
    channel_id = event.get("channel")

    # Check and see if the activation phrase was in the text of the message.
    # If so, execute the code to flip a coin.
    if "hey sammy, flip a coin" in text:
        # Since the activation phrase was met, get the channel ID that the event
        # was executed on

        # Execute the flip_coin function and send the results of
        # flipping a coin to the channel
        return flip_coin(channel_id)

    if "aaaaaaaaaaaa" in text:
        return slap_the_slackbot(channel_id)


def send_tabulated_result(channel_id, prefix, elements, thread_id):
    slack_client.send_message(
        channel_id,
        prefix + tabulate(elements['data'], headers=elements['headers'], tablefmt='psql'),
        thread_id
    )


def process_report_exec(metadata_client, re_report, report_match, text, channel_id, workspace_id):
    # Init Report(Pandas) SDK
    report_client = Report(ENDPOINT, TOKEN, workspace_id, metadata_client)
    request = report_client.parse_request(re_report, text)
    if request:
        df = report_client.execute(request['metrics'], request['labels'])
        base_path = '/tmp/' + str(uuid.uuid4())
        if report_match.group(1) == 'tab':
            file_path = base_path + '.txt'
            with open(file_path, 'wt') as fd:
                fd.write(tabulate(df, headers='keys', tablefmt='psql', showindex="never"))
        elif report_match.group(1) == 'csv':
            file_path = base_path + '.csv'
            with open(file_path, 'wt') as fd:
                df.to_csv(fd, index=False)
        else:
            file_path = base_path + '.png'
            with open(file_path, 'w+b') as fd:
                plot = report_client.plot_vis(df, request['labels'], request['metrics'])
                plot.savefig(fd)
        slack_client.send_file(channel_id, file_path)
    else:
        slack_client.send_markdown_message(
            channel_id, ['ERROR: invalid execute request, valid is {metric} BY {dimension}\n']
        )


@slack_events_adapter.on("app_mention")
def reply(payload):
    """Parse messages only when the bot is mentioned"""
    print(f"Event: app_mention, payload: {payload}")

    event = payload.get("event", {})
    text = event.get("text")
    if text:
        text = text.lower()
    channel_id = event.get("channel")
    thread_id = event.get("thread_ts", None)
    source_user_id = event.get("user", None)
    hit = False

    # Init metadata SDK
    metadata_client = Metadata(ENDPOINT, TOKEN)

    channels_2ws = read_config_from_file('slack_channels_2ws.yaml')
    if channel_id in channels_2ws:
        workspace_id = channels_2ws[channel_id]
    else:
        slack_client.send_markdown_message(
            channel_id,
            [f"Error: channel ID {channel_id} is not configured as GoodData.CN workspace\n"]
        )
        return

    workspace_ids = metadata_client.get_workspace_ids()
    if workspace_id not in workspace_ids:
        slack_client.send_markdown_message(
            channel_id,
            [f"Error: workspace {workspace_id} configured for channel {channel_id} does not exist\n"]
        )
        return
    metadata_client.workspace_id = workspace_id

    if "list workspaces" in text:
        hit = True
        workspaces = metadata_client.list_workspaces()
        send_tabulated_result(channel_id, 'Workspaces:\n-------\n', workspaces, thread_id)
    if "list data sources" in text:
        hit = True
        data_sources = metadata_client.list_data_sources()
        send_tabulated_result(channel_id, 'Data sources:\n-------\n', data_sources, thread_id)
    if "list labels" in text:
        hit = True
        labels = metadata_client.list_labels()
        send_tabulated_result(channel_id, 'Labels:\n-------\n', labels, thread_id)
    if "list metrics" in text:
        hit = True
        metrics = metadata_client.list_metrics()
        facts = metadata_client.list_facts()
        send_tabulated_result(channel_id, 'Metrics:\n-------\n', metrics, thread_id)
        send_tabulated_result(channel_id, 'Facts:\n-------\n', facts, thread_id)
    if "list insights" in text:
        hit = True
        insights = metadata_client.list_insights()
        send_tabulated_result(channel_id, 'Insights:\n-------\n', insights, thread_id)

    re_report = re.compile(r'^<[^>]+>\s*execute_(tab|csv|vis) ', re.I)
    report_match = re_report.match(text)
    if report_match:
        hit = True
        process_report_exec(metadata_client, re_report, report_match, text, channel_id, workspace_id)

    if not hit:
        slack_client.send_markdown_message(channel_id, [f"Hello, thanks for mentioning me <@{source_user_id}>.\n"])


@app.route("/")
def index():
    return "Hello this is the new version!"
