# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

from gooddata_metadata_client.api import organization_model_controller_api, workspace_object_controller_api
from gooddata_sdk import GoodDataApiClient


class Metadata:
    def __init__(self, host, api_key):
        client = GoodDataApiClient(host=host, token=api_key)
        md_client = client.metadata_client
        self.org_model = organization_model_controller_api.OrganizationModelControllerApi(md_client)
        self.workspace_model = workspace_object_controller_api.WorkspaceObjectControllerApi(md_client)
        self.workspace_id = None

    def get_workspace_ids(self):
        result = self.org_model.get_all_entities_workspaces(_check_return_type=False)
        return [w['id'] for w in result.data]

    def list_workspaces(self):
        result = self.org_model.get_all_entities_workspaces(include=['workspaces'], _check_return_type=False)
        data = [
            [element['attributes']['name'], element['id']]
            for element in result.data
        ]
        return {
            'headers': ['Name', 'Id'],
            'data': data
        }

    def list_data_sources(self):
        result = self.org_model.get_all_entities_data_sources(_check_return_type=False)
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
        result = self.workspace_model.get_all_entities_labels(self.workspace_id, _check_return_type=False)
        return self._get_entities_basic(result, 'label/')

    def list_metrics(self):
        result = self.workspace_model.get_all_entities_facts(self.workspace_id, _check_return_type=False)
        return self._get_entities_basic(result, 'metric/')

    def list_facts(self):
        result = self.workspace_model.get_all_entities_metrics(self.workspace_id, _check_return_type=False)
        return self._get_entities_basic(result, 'fact/')

    def list_insights(self):
        result = self.workspace_model.get_all_entities_visualization_objects(self.workspace_id, _check_return_type=False)
        return self._get_entities_basic(result)

    def get_label_title_by_id(self, label_id):
        result = self.workspace_model.get_entity_labels(self.workspace_id, label_id)
        return result.data['attributes']['title']

    def get_fact_title_by_id(self, fact_id):
        result = self.workspace_model.get_entity_facts(self.workspace_id, fact_id)
        return result.data['attributes']['title']

    def get_metric_title_by_id(self, metric_id):
        result = self.workspace_model.get_entity_metrics(self.workspace_id, metric_id)
        return result.data['attributes']['title']
