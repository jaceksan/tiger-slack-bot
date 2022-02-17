# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

from gooddata_sdk import GoodDataSdk
import gooddata_metadata_client.apis as metadata_apis


class Metadata:
    def __init__(self, host, api_key):
        sdk = GoodDataSdk.create(host, api_key)
        self.entities_api = metadata_apis.EntitiesApi(sdk._client.metadata_client)
        self.actions_api = metadata_apis.ActionsApi(sdk._client.metadata_client)
        self.workspace_id = None

    def get_workspace_ids(self):
        result = self.entities_api.get_all_entities_workspaces(_check_return_type=False, size=100)
        return [w['id'] for w in result.data]

    def list_workspaces(self):
        result = self.entities_api.get_all_entities_workspaces(include=['workspaces'], _check_return_type=False, size=100)
        data = [
            [element['attributes']['name'], element['id']]
            for element in result.data
        ]
        return {
            'headers': ['Name', 'Id'],
            'data': data
        }

    def list_data_sources(self):
        result = self.entities_api.get_all_entities_data_sources(_check_return_type=False, size=100)
        data = [
            [element['attributes']['name'], element['attributes']['type'], element['attributes']['url'], element['id']]
            for element in result.data
        ]
        return {
            'headers': ['Name', 'Type', 'Url', 'Id'],
            'data': data
        }

    @staticmethod
    def _get_entities_basic(result, entity_prefix=''):
        data = [
            [element['attributes']['title'], entity_prefix + element['id']]
            for element in result.data
        ]
        return {
            'headers': ['Title', 'Id'],
            'data': data
        }

    def list_labels(self):
        result = self.entities_api.get_all_entities_labels(self.workspace_id, _check_return_type=False, size=100)
        return self._get_entities_basic(result, 'label/')

    def list_metrics(self):
        result = self.entities_api.get_all_entities_metrics(self.workspace_id, _check_return_type=False, size=100)
        return self._get_entities_basic(result, 'metric/')

    def list_facts(self):
        result = self.entities_api.get_all_entities_facts(self.workspace_id, _check_return_type=False, size=100)
        return self._get_entities_basic(result, 'fact/')

    def list_insights(self):
        result = self.entities_api.get_all_entities_visualization_objects(
            self.workspace_id, _check_return_type=False, size=100
        )
        return self._get_entities_basic(result)

    def get_label_title_by_id(self, label_id):
        result = self.entities_api.get_entity_labels(self.workspace_id, label_id)
        return result.data['attributes']['title']

    def get_fact_title_by_id(self, fact_id):
        result = self.entities_api.get_entity_facts(self.workspace_id, fact_id)
        return result.data['attributes']['title']

    def get_metric_title_by_id(self, metric_id):
        result = self.entities_api.get_entity_metrics(self.workspace_id, metric_id)
        return result.data['attributes']['title']

    def invalid_caches(self, data_source_id):
        self.actions_api.register_upload_notification(data_source_id)