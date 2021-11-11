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

    def send_markdown_message(self, channel, texts, thread_ts=None):
        payload = {
            "channel": channel,
            "blocks": self._get_block(texts),
        }
        if thread_ts:
            payload['thread_ts'] = thread_ts
        self.slack_web_client.chat_postMessage(**payload)

    def send_message(self, channel, message, thread_ts=None):
        payload = {}
        if thread_ts:
            payload['thread_ts'] = thread_ts
        self.slack_web_client.chat_postMessage(channel=channel, text=message, **payload)

    def send_file(self, channel, file_path, thread_ts=None):
        payload = {}
        if thread_ts:
            payload['thread_ts'] = thread_ts
        self.slack_web_client.files_upload(
            channels=channel,
            file=file_path,
            title='Insight',
            **payload
        )
