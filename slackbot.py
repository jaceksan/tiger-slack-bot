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

    # Get the event data from the payload
    event = payload.get("event", {})

    # Get the text from the event that came through
    text = event.get("text").lower()
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

    if text.startswith('tiger_bot: list_workspaces'):
        slack_client.send_markdown_message(
            channel_id,
            [metadata_client.list_workspaces()]
        )


@slack_events_adapter.on("app_mention")
def reply(payload):
    """Parse messages only when the bot is mentioned"""
    event = payload.get("event", {})
    text = event.get("text")
    channel_id = event.get("channel")

    return slack_client.send_markdown_message(channel_id, ["Hello, thanks for mentioning me.\n"])


@app.route("/")
def index():
    return "Hello this is the new version!"
