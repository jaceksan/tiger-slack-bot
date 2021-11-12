# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation
import re
from gooddata_pandas import GoodPandas
import matplotlib.pyplot as plt

from tiger.metadata import Metadata


class Report:
    def __init__(self, host, api_key, workspace_id, metadata_client: Metadata):
        self.gp = GoodPandas(host=host, token=api_key)
        self.frames = self.gp.data_frames(workspace_id)
        self.metadata_client = metadata_client

    def parse_request(self, re_report, request):
        query = re_report.sub('', request)
        query_re = re.compile(r'^(.*) BY (.*)$', re.I)
        query_match = query_re.search(query)
        if query_match:
            metrics = [
                {'id': m, 'short_id': m.replace('metric/', '').replace('fact/', '')}
                for m in re.split(r',\s*', query_match.group(1))
            ]
            labels = [
                {'id': ls, 'short_id': ls.replace('label/', '')}
                for ls in re.split(r',\s*', query_match.group(2))
            ]
            labels = self.add_titles(labels, self.metadata_client.get_label_title_by_id)
            metrics = self.add_titles(
                [m for m in metrics if m['id'].startswith('metric/')],
                self.metadata_client.get_metric_title_by_id
            ) + self.add_titles(
                [m for m in metrics if m['id'].startswith('fact/')],
                self.metadata_client.get_fact_title_by_id
            )
            return {
                'metrics': metrics,
                'labels': labels,
            }
        else:
            return None

    @staticmethod
    def add_titles(entities, get_title_func):
        for entity in entities:
            entity['title'] = get_title_func(entity['short_id'])
        return entities

    def execute(self, metrics, labels):
        columns = {
            labels[0]['title']: labels[0]['id']
        }
        if len(labels) == 2:
            columns[labels[1]['title']] = labels[1]['id']

        columns[metrics[0]['title']] = metrics[0]['id']
        if len(metrics) == 2:
            columns[metrics[1]['title']] = metrics[1]['id']
        indexed_df = self.frames.indexed(index_by=labels[0]['id'], columns=columns)
        return indexed_df

    @staticmethod
    def plot_vis(indexed_df, labels, metrics):
        ax = plt.gca()
        indexed_df.plot(kind='line', x=labels[0]['title'], y=metrics[0]['title'], ax=ax)
        if len(metrics) == 2:
            indexed_df.plot(kind='line', x=labels[0]['title'], y=metrics[1]['title'], ax=ax)
        return plt
