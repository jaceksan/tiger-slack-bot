#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

import os
import re
import time
import tempfile
import traceback
import threading
from flask import Flask
from slackeventsapi import SlackEventAdapter
from tabulate import tabulate
from coinbot import CoinBot
from tiger.slackclient import SlackClient
from tiger.metadata import Metadata
import yaml
from tiger.history import answer_from_history
from tiger.report_exec import process_report_exec


ENDPOINT = 'https://bettermee.anywhere.gooddata.com'
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
    slack_client.send_markdown_message(channel, ["Shut up, Slackbot!\n"])


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


def send_tabulated_result(channel_id, prefix, elements, thread_id, use_file=False):
    if use_file:
        with tempfile.NamedTemporaryFile(mode="w+b", suffix="txt") as fp:
            msg = prefix + tabulate(elements['data'], headers=elements['headers'], tablefmt='psql')
            fp.write(msg.encode('utf-8'))
            fp.seek(0)
            slack_client.send_file(channel_id, fp, 'result.txt', thread_ts=thread_id)
    else:
        slack_client.send_message(
            channel_id,
            "```" + prefix + tabulate(elements['data'], headers=elements['headers'], tablefmt='psql') + "```",
            thread_id
        )


def generate_help(text, channel_id, thread_id):
    if "help exec" in text:
        help_hints = [
            ":speech_balloon: Thank you for asking, here is detailed doc about `exec_(tab,csv,vis)`:\n\n" +
            "* Usage: `exec_*` metric1, metric2 BY label1, label2\n" +
            "\t* You can use only 1 metric / 1 label\n" +
            "\t* metric/label must be in form of ID with prefix, e.g. label/date.month or fact/order_lines.price\n" +
            "* Use `list labels/metrics` to get IDs\n" +
            "* Types:\n" +
            "\t* `tab` - pretty printed table\n" +
            "\t* `csv` - CSV file as attachment\n" +
            "\t* `xls` - Excel file as attachment\n" +
            "\t* `vis` - chart rendered by `matplotlib`\n" +
            ":raised_hands:\n"
        ]
        slack_client.send_markdown_message(channel_id, help_hints, thread_id)
    else:
        help_hints = [
            ":speech_balloon: Thank you for asking, there are few hints I can help you with:\n\n" +
            "* `list workspaces` \n" +
            "* `list data sources`\n" +
            "* `list labels`\n" +
            "* `list metrics`\n" +
            "* `list insights`\n" +
            "* `execute_tab`/`execute_csv`/`execute_vis|sea` - returns table, csv or vizualization\n\n" +
            " use `help exec` to learn more about it"
            ":raised_hands:\n"
        ]
        slack_client.send_markdown_message(channel_id, help_hints, thread_id)


def handle_lists(metadata_client, text, channel_id, thread_id, as_file_flag):
    hit = False
    if "list workspaces" in text:
        hit = True
        workspaces = metadata_client.list_workspaces()
        send_tabulated_result(channel_id, 'Workspaces:\n-------\n', workspaces, thread_id, as_file_flag)
    if "list data sources" in text:
        hit = True
        data_sources = metadata_client.list_data_sources()
        send_tabulated_result(channel_id, 'Data sources:\n-------\n', data_sources, thread_id, as_file_flag)
    if "list labels" in text:
        hit = True
        labels = metadata_client.list_labels()
        send_tabulated_result(channel_id, 'Labels:\n-------\n', labels, thread_id, as_file_flag)
    if "list metrics" in text:
        hit = True
        metrics = metadata_client.list_metrics()
        facts = metadata_client.list_facts()
        send_tabulated_result(channel_id, 'Metrics:\n-------\n', metrics, thread_id, as_file_flag)
        send_tabulated_result(channel_id, 'Facts:\n-------\n', facts, thread_id, as_file_flag)
    if "list insights" in text:
        hit = True
        insights = metadata_client.list_insights()
        send_tabulated_result(channel_id, 'Insights:\n-------\n', insights, thread_id, as_file_flag)
    return hit


def get_workspace_id(metadata_client, channel_id):
    channels_2ws = read_config_from_file('slack_channels_2ws.yaml')
    if channel_id in channels_2ws:
        workspace_id = channels_2ws[channel_id]
    else:
        slack_client.send_markdown_message(
            channel_id,
            [f"Error: channel ID {channel_id} is not configured as GoodData.CN workspace\n"]
        )
        return None

    workspace_ids = metadata_client.get_workspace_ids()
    if workspace_id not in workspace_ids:
        slack_client.send_markdown_message(
            channel_id,
            [f"Error: workspace {workspace_id} configured for channel {channel_id} does not exist\n"]
        )
        return None
    return workspace_id


@slack_events_adapter.on("app_mention")
def reply(payload):
    """Parse messages only when the bot is mentioned"""
    ts = time.time()
    print(f"Event: app_mention, ts: {ts} payload: {payload}")

    event = payload.get("event", {})
    text = event.get("text")
    if text:
        text = text.lower()
    channel_id = event.get("channel")
    thread_id = event.get("thread_ts", None)
    source_user_id = event.get("user", None)
    hit = False

    try:
        answered, history_msg = answer_from_history(source_user_id, text)
        if history_msg:
            slack_client.send_message(channel_id, history_msg, thread_id)
        if answered:
            return

        # Init metadata SDK
        metadata_client = Metadata(ENDPOINT, TOKEN)

        workspace_id = get_workspace_id(metadata_client, channel_id)
        if not workspace_id:
            return
        metadata_client.workspace_id = workspace_id

        help_re = re.compile(r'^<[^>]+> help')
        if help_re.match(text):
            hit = True
            generate_help(text, channel_id, thread_id)

        as_file_flag = "as file" in text
        if "list " in text:
            hit = handle_lists(metadata_client, text, channel_id, thread_id, as_file_flag) or hit

        re_report = re.compile(r'^<[^>]+>\s*execute_(tab|csv|xls|vis) ', re.I)
        report_match = re_report.match(text)
        if report_match:
            hit = True
            slack_client.send_markdown_message(
                channel_id,
                [f"You report execution was accepted and queued, please, wait for result.\n"]
            )
            t_id = threading.Thread(
                target=process_report_exec,
                args=(metadata_client, slack_client, re_report, report_match, text, channel_id, workspace_id),
                daemon=True
            )
            t_id.start()
#            process_report_exec(metadata_client, re_report, report_match, text, channel_id, workspace_id)

        if not hit:
            slack_client.send_markdown_message(channel_id, [f"Hello, thanks for mentioning me <@{source_user_id}>.\n"])
    except Exception:
        print(traceback.format_exc())
        slack_client.send_markdown_message(channel_id, [f"Something went wrong user <@{source_user_id}>, fix me\n"])

    print(f"Event: app_mention, ts: {ts} - Finished")


@app.route("/")
def index():
    return "Hello this is the new version!"
