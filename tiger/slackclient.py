# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

import os
from slack import WebClient


class SlackClient:
    def __init__(self):
        self.slack_web_client = WebClient(token=os.environ.get("SLACK_API_TOKEN"))
        self._bots_info = self.slack_web_client.bots_info()
        print(f"Bots info: {self._bots_info.data}")

    @staticmethod
    def _get_block(texts):
        return [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    text
                ),
            }
        } for text in texts]

    def send_markdown_message(self, channel, texts, thread_ts=None):
        payload = {
            "channel": channel,
            "blocks": self._get_block(texts),
        }
        if thread_ts:
            payload['thread_ts'] = thread_ts
        self.slack_web_client.chat_postMessage(**payload)

    def send_message(self, channel, message):
        self.slack_web_client.chat_postMessage(channel=channel, text=message)

    def bot_user_id(self):
        self._bots_info.get("user_id", None)
