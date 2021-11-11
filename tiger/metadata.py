# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

from gooddata_metadata_client.api import organization_model_controller_api
from gooddata_sdk import GoodDataApiClient


class Metadata:
    def __init__(self, host, api_key):
        client = GoodDataApiClient(host=host, token=api_key)
        md_client = client.metadata_client
        self.org_model = organization_model_controller_api.OrganizationModelControllerApi(md_client)

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
