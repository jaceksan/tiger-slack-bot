# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

import os
from slack import WebClient


class SlackClient:
    def __init__(self):
        self.slack_web_client = WebClient(token=os.environ.get("SLACK_API_TOKEN"))

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

    def send_markdown_message(self, channel, texts):
        payload = {
            "channel": channel,
            "blocks": self._get_block(texts),
        }
        self.slack_web_client.chat_postMessage(**payload)
