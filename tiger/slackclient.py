# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

import os
import tempfile
from tabulate import tabulate
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

    def send_file(self, channel, file_path, file_name, thread_ts=None):
        payload = {}
        if thread_ts:
            payload['thread_ts'] = thread_ts
        self.slack_web_client.files_upload(
            channels=channel,
            file=file_path,
            title=file_name,
            **payload
        )

    def send_tabulated_result(self, channel_id, prefix, elements, thread_id, use_file=False):
        if use_file:
            with tempfile.NamedTemporaryFile(mode="w+b", suffix="txt") as fp:
                msg = prefix + tabulate(elements['data'], headers=elements['headers'], tablefmt='psql')
                fp.write(msg.encode('utf-8'))
                fp.seek(0)
                self.send_file(channel_id, fp, 'result.txt', thread_ts=thread_id)
        else:
            self.send_message(
                channel_id,
                "```" + prefix + tabulate(elements['data'], headers=elements['headers'], tablefmt='psql') + "```",
                thread_id
            )
