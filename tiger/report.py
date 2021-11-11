# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation
import re
from gooddata_pandas import GoodPandas
import matplotlib.pyplot as plt


class Report:
    def __init__(self, host, api_key, workspace_id):
        self.gp = GoodPandas(host=host, token=api_key)
        self.frames = self.gp.data_frames(workspace_id)

    @staticmethod
    def parse_request(re_report, request):
        query = re_report.sub('', request)
        query_re = re.compile(r'^(.*) BY (.*)$', re.I)
        query_match = query_re.search(query)
        if query_match:
            return {
                'metrics': re.split(r',\s*', query_match.group(1)),
                'labels': re.split(r',\s*', query_match.group(2)),
            }
        else:
            return None

    def execute(self, metrics, labels):
        columns = dict(
            first_label=labels[0],
            first_metric=metrics[0],
        )
        if len(labels) == 2:
            columns['second_label'] = labels[1]
        if len(metrics) == 2:
            columns['second_metric'] = metrics[1]
        indexed_df = self.frames.indexed(index_by=labels[0], columns=columns)
        return indexed_df

    @staticmethod
    def plot_vis(indexed_df):
        plt.plot(indexed_df['first_label'], indexed_df['first_metric'])
        return plt
