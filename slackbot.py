#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

import os
from flask import Flask
from slackeventsapi import SlackEventAdapter
from coinbot import CoinBot
from tiger.slackclient import SlackClient
from tiger.metadata import Metadata

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
# Create an events adapter and register it to an endpoint in the slack app for event ingestion.
slack_events_adapter = SlackEventAdapter(os.environ.get("SLACK_EVENTS_TOKEN"), "/slack/events", app)

# Initialize a Web API client
slack_client = SlackClient()

# Init metadata SDK
metadata_client = Metadata('https://hackaton.anywhere.gooddata.com', os.environ.get('TIGER_API_TOKEN'))

HEROKU_PORT = os.getenv('PORT', 3000)


def flip_coin(channel):
    """Craft the CoinBot, flip the coin and send the message to the channel
    """
    # Create a new CoinBot
    coin_bot = CoinBot()
    slack_client.send_markdown_message(channel, [coin_bot.COIN_START_BLOCK, coin_bot.flip_coin()])


def slap_the_slackbot(channel):
    slack_client.send_markdown_message(channel, ["Zmlkni Slackbote!\n"])


# When a 'message' event is detected by the events adapter, forward that payload
# to this function.
@slack_events_adapter.on("message")
def message(payload):
    """Parse the message event, and if the activation string is in the text,
    simulate a coin flip and send the result.
    """
    print(f"Event: message, payload: {payload}")

    # Get the event data from the payload
    event = payload.get("event", {})

    # Get the text from the event that came through
    text = event.get("text")
    if text:
        text = text.lower()
    channel_id = event.get("channel")
    source_user_id = event.get("user", None)
    thread_ts = event.get("thread_ts", None)

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

    if text.startswith('tiger_bot: list_workspaces'):
        slack_client.send_markdown_message(
            channel_id,
            [metadata_client.list_workspaces()],
            thread_ts=thread_ts
        )

    if text.startswith('tiger_bot: list data sources'):
        slack_client.send_message(channel_id, metadata_client.list_data_sources(), thread_ts)


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

    if "list workspaces" in text:
        hit = True
        slack_client.send_markdown_message(
            channel_id,
            [metadata_client.list_workspaces()],
            thread_ts=thread_id
        )
    if "list data sources" in text:
        hit = True
        slack_client.send_message(channel_id, metadata_client.list_data_sources(), thread_id)

    if not hit:
        slack_client.send_markdown_message(channel_id, [f"Hello, thanks for mentioning me <@{source_user_id}>.\n"])


@app.route("/")
def index():
    return "Hello this is the new version!"
