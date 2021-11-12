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
            labels = self.add_titles(
                labels,
                self.metadata_client.get_label_title_by_id,
                re.compile(r'[^.a-z0-9_-]+', re.I)
            )
            metrics = self.add_titles(
                [m for m in metrics if m['id'].startswith('metric/')],
                self.metadata_client.get_metric_title_by_id,
                re.compile(r'[^.a-z0-9_-]+', re.I)
            ) + self.add_titles(
                [m for m in metrics if m['id'].startswith('fact/')],
                self.metadata_client.get_fact_title_by_id,
                re.compile(r'[^.a-z0-9_-]+', re.I)
            )
            return {
                'metrics': metrics,
                'labels': labels,
            }
        else:
            return None

    @staticmethod
    def add_titles(entities, get_title_func, re_sanitize=None):
        for entity in entities:
            try:
                # Regex to workaround local identifier issue
                title = get_title_func(entity['short_id'])
            except Exception as e:
                print(f'add_titles: {str(e)}')
                if '(404)' in str(e):
                    raise MetadataNotFound(entity)
            else:
                if re_sanitize:
                    title = re_sanitize.sub('_', title)
                entity['title'] = title
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
        plt.close()
        ax = plt.gca()
        print(f"Plot-df: {indexed_df}")
        print(f"Y-Metric-1: {metrics[0]['title']}")
        indexed_df.plot(kind='line', x=labels[0]['title'], y=metrics[0]['title'], ax=ax)
        if len(metrics) == 2:
            print(f"Y-Metric-2: {metrics[1]['title']}")
            indexed_df.plot(kind='line', x=labels[0]['title'], y=metrics[1]['title'], ax=ax)
        return plt


class MetadataNotFound(Exception):
    def __init__(self, entity):
        self.entity = entity
        super().__init__(f"Entity {entity['id']} ({entity['title']}) does not exist in Metadata")
