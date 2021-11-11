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

    def list_workspaces(self):
        result = self.org_model.get_all_entities_workspaces(_check_return_type=False)
        workspaces = ""
        for workspace in result.data:
            workspace_id = workspace['id']
            workspace_name = workspace['attributes']['name']
            workspace_parent_id = ''
            if 'relationships' in workspace:
                workspace_parent_id = workspace['relationships']['parent']['data']['id']
            workspaces += f"- id={workspace_id} name={workspace_name} parent_workspace_id={workspace_parent_id}\n"
        return workspaces

    def list_data_sources(self):
        result = self.org_model.get_all_entities_data_sources(_check_return_type=False)
        ds_lines = [
            f"\tName:{ds['attributes']['name']} - Type:{ds['attributes']['type']} - Id: {ds['id']}"
            for ds in result.data
        ]
        ds_output = "\n".join(ds_lines)
        return f"Registered data sources:\n{ds_output}"

    @staticmethod
    def _get_entity_basic_lines(result):
        lines = [
            f"\tName:{element['attributes']['title']} - Id: {element['id']}"
            for element in result.data
        ]
        return "\n".join(lines)

    def list_labels(self, workspace_id):
        result = self.workspace_model.get_all_entities_labels(workspace_id, _check_return_type=False)
        return f"Labels:\n{self._get_entity_basic_lines(result)}"

    def list_metrics(self, workspace_id):
        result = self.workspace_model.get_all_entities_facts(workspace_id, _check_return_type=False)
        facts = self._get_entity_basic_lines(result)
        result = self.workspace_model.get_all_entities_metrics(workspace_id, _check_return_type=False)
        metrics = self._get_entity_basic_lines(result)
        return f"Facts:\n{facts}\n\nMetrics:{metrics}"
