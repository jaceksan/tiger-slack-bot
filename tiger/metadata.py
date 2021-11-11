# -*- coding: utf-8 -*-
# (C) 2021 GoodData Corporation

import gooddata_metadata_client
from gooddata_metadata_client.api import organization_model_controller_api


class Metadata:
    def __init__(self, host, api_key):
        configuration = gooddata_metadata_client.Configuration(
            host=host,
            api_key=api_key,
            api_key_prefix="Bearer"
        )
        with gooddata_metadata_client.ApiClient(configuration) as api_client:
            self.api_instance = organization_model_controller_api.OrganizationModelControllerApi(api_client)

    def list_workspaces(self):
        result = self.api_instance.get_entity_workspaces()
        workspaces = ""
        for workspace in result['data']:
            workspaces += f"- id={workspace['id']} name={workspace['attributes']['name']} " + \
                          f"parent_workspace_id={workspace['relationships']['parent']['data']['id']}\n"
        return workspaces
