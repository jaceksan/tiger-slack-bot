# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation
import re
from typing import Optional

import pandas as pd
from pandas.plotting._matplotlib.style import get_standard_colors
import matplotlib.axes
from gooddata_pandas import GoodPandas
import matplotlib.pyplot as plt
from tiger.constants import ENDPOINT, TOKEN
from tiger.metadata import Metadata

plt.rcParams["figure.figsize"] = [19.8, 10.8]
plt.rcParams.update({'font.size': 18})


class Report:
    def __init__(self, workspace_id, metadata_client: Metadata):
        self.gp = GoodPandas(ENDPOINT, TOKEN)
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
            # Regex to workaround local identifier issue
            title = get_title_func(entity['short_id'])
            if re_sanitize:
                title = re_sanitize.sub('_', title)
            entity['title'] = title
        return entities

    def execute(self, metrics, labels):
        columns = {}
        for i in range(1, len(labels)):
            columns[labels[i]['title']] = labels[i]['id']
        for i in range(len(metrics)):
            columns[metrics[i]['title']] = metrics[i]['id']
        indexed_df = self.frames.indexed(index_by=labels[0]['id'], columns=columns)
        return indexed_df

    @staticmethod
    def plot_bar(data: pd.DataFrame, xaxis_title: str):
        plt.close()
        ax = data.plot.bar(rot=0)
        ax.set_xlabel(xlabel=xaxis_title)
        return ax

    @staticmethod
    def plot_line(
        data: pd.DataFrame,
        xaxis_title: str,
        spacing: float = 0.1,
        **kwargs
    ) -> Optional[matplotlib.axes.Axes]:
        """Plot multiple Y axes on the same chart with same x axis.

        Args:
            data: dataframe which contains x and y columns
            xaxis_title: title of X axis
            spacing: spacing between the plots
            **kwargs: keyword arguments to pass to data.plot()

        Returns:
            a matplotlib.axes.Axes object returned from data.plot()
        """
        # Get default color style from pandas - can be changed to any other color list
        y = data.columns
        colors = get_standard_colors(num_colors=len(y))

        if "legend" not in kwargs:
            kwargs["legend"] = False  # prevent multiple legends

        # Reset plt
        plt.close()

        # First axis
        ax = data.plot(x=None, y=y[0], color=colors[0], **kwargs)
        ax.set_xlabel(xlabel=xaxis_title)
        ax.set_ylabel(ylabel=y[0])
        lines, labels = ax.get_legend_handles_labels()

        for i in range(1, len(y)):
            # Multiple y-axes
            ax_new = ax.twinx()
            ax_new.spines["right"].set_position(("axes", 1 + spacing * (i - 1)))
            data.plot(
                ax=ax_new, x=None, y=y[i], color=colors[i % len(colors)], **kwargs
            )
            ax_new.set_ylabel(ylabel=y[i])

            # Proper legend position
            line, label = ax_new.get_legend_handles_labels()
            lines += line
            labels += label

        ax.legend(lines, labels, loc=0)
        return ax


class MetadataNotFound(Exception):
    def __init__(self, entity):
        self.entity = entity
        super().__init__(f"Entity {entity['id']} ({entity['title']}) does not exist in Metadata")
