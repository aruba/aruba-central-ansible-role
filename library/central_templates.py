#!/usr/bin/python
'''
Central Templates Ansible Module
'''
# MIT License
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: central_templates
version_added: 2.9.0
short_descriptions: REST API module for templates on Aruba Central
description: This module provides a mechanism to interact with or upload
             configuration templates that are used for group-level and
             device-level configuration on Aruba Central
options:
    action:
        description:
            - Action to be performed on the template(s)
            - "get_template_text" gets the contents of a template
            - "get_all" gets info on all templates in a group
            - "update" updates attributes of an existing template
            - "create" creates a new template in a group
            - "delete" deletes an existing template from a group
        required: true
        type: str
        choices:
            - get_template_text
            - get_all
            - update
            - create
            - delete
    group_name:
        description:
            - Name of the group
        required: true
        type: str
    template_name:
        description:
            - Name of the template on Aruba Central
            - Used with actions "get_template_text", "create", "update", and
              "delete"
        required: false
        type: str
    device_type:
        description:
            - Type of device for which the template file is applicable
            - Used with action "create"
            - Used optionally with actions "get_all" and "update"
        required: false
        type: str
        choices:
            - IAP
            - ArubaSwitch
            - CX
            - MobilityController
    version:
        description:
            - Firmware version property of template
            - Used with action "create"
            - Used optionally with actions "get_all" and "update"
        required: false
        type: str
        default: ALL
    model:
        description:
            - Model property of template
            - Used with action "create"
            - Used optionally with actions "get_all" and "update"
            - For the "ArubaSwitch" device_type (i.e. AOS-S switches),
              the part number (J number) can be used
                - e.g. 2920, J9727A, etc.
        required: false
        type: str
        default: ALL
    local_file_path:
        description:
            - Full local path of template file to be uploaded
            - For HP Switches, the template text should include the following
              commands to maintain connection with Central:
                - aruba-central enable
                - aruba-central url https://< URL | IP >/ws
            - Used with actions "create" and "update"
        required: false
        type: str
    limit:
        description:
            - Maximum number of records to be returned
            - Used optionally as a filter parameter for "get_all"
        required: false
        type: int
        default: 20
    offset:
        description:
            - Number of items to be skipped before returning the data, which is
              useful for pagination
            - Used optionally as a filter parameter for get_all
        required: false
        type: int
        default: 0

"""
EXAMPLES = """
#Usage Examples
- name: Get all templates in a given group
  central_templates:
    action: get_all
    group_name: new-group
    limit: 20
    offset: 0

- name: Get templates in a given group for a particular device type
  central_templates:
    action: get_all
    group_name: new-group
    device_type: IAP
    limit: 20
    offset: 0
    version: ALL
    model: ALL

- name: Get template text
  central_templates:
    action: get_template_text
    group_name: new-group
    template_name: iap-temp

- name: Upload a new template file and create a new template for a given device type  # NOQA
  central_templates:
    action: create
    group_name: new-group
    template_name: iap-temp
    device_type: IAP
    version: ALL
    model: ALL
    local_file_path: /home/iap_template.txt

- name: Update an existing template
  central_templates:
    action: update
    group_name: new-group
    template_name: iap-temp
    device_type: IAP
    version: ALL
    model: ALL
    local_file_path: /home/modified_iap_template.txt

- name: Delete an existing template
  central_templates:
    action: delete
    group_name: new-group
    template_name: iap-temp

"""

import json  # NOQA
from ansible.module_utils.basic import AnsibleModule  # NOQA
from ansible.module_utils.central_http import CentralApi  # NOQA


def error_msg(action):
    '''
    Error handler for errors related to missing playbook parameters in
    templates module
    '''
    result = {"resp": None, "code": 400}
    if action == "get_template_text" or action == "delete":
        resp = "Template name is not present in the playbook"
    if action == "create" or action == "update":
        resp = "Template name, device type, or local file path is not" \
               " present in the playbook"
    result['resp'] = resp
    return result


def get_all_templates(central_api, group_name, **kwargs):
    '''
    Used to get info on all templates in a group
    '''
    endpoint = "/configuration/v1/groups/" + str(group_name) + "/templates"
    query_params = {}
    headers = central_api.get_headers(False, "get")
    for key, val in kwargs.items():
        if val is not None:
            query_params[key] = val
    path = central_api.get_url(endpoint, query_params)
    result = central_api.get(path=path, headers=headers)
    return result


def get_template_text(central_api, group_name, template_name):
    '''
    Used to get template text, which is the group configuration for applicable
    devices
    '''
    if template_name is not None:
        path = "/configuration/v1/groups/" + str(group_name) + "/templates/" +\
               str(template_name)
        headers = central_api.get_headers(True, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("get_template_text")


def create_update_template(central_api, group_name, template_name, **kwargs):
    '''
    Used to upload and create a new group template for various devices, as
    well as change attributes for an existing template
    '''
    if None not in kwargs.values() and template_name is not None:
        endpoint = "/configuration/v1/groups/"+str(group_name)+"/templates"
        query_params = {"name": template_name,
                        "device_type": kwargs['device_type'],
                        "version": kwargs['version'], "model": kwargs['model']}
        headers = central_api.get_headers(True, "post")
        path = central_api.get_url(endpoint, query_params)
        filepath = kwargs['file']
        if kwargs['action'] == "create":
            result = central_api.post(path=path, headers=headers,
                                      filename=filepath)
        elif kwargs['action'] == "update":
            result = central_api.patch(path=path, headers=headers,
                                       filename=filepath)
        return result
    return error_msg("create")


def delete_template(central_api, group_name, template_name):
    '''
    Used to delete an existing template from an existing group
    '''
    if template_name is not None:
        headers = central_api.get_headers(False, "delete")
        path = "/configuration/v1/groups/" + str(group_name) + "/templates/"\
               + str(template_name)
        result = central_api.delete(path=path, headers=headers)
        return result
    return error_msg("delete")


def api_call(module):
    '''
    Uses playbook parameters to determine type of API request to be made
    '''
    central_api = CentralApi(module)
    action = module.params.get('action').lower()
    group_name = module.params.get('group_name')
    template_name = module.params.get('template_name')
    limit = module.params.get('limit')
    offset = module.params.get('offset')
    device_type = module.params.get('device_type')
    version = module.params.get('version')
    model = module.params.get('model')
    local_file_path = module.params.get('local_file_path')

    if action == "get_template_text":
        result = get_template_text(central_api, group_name, template_name)

    elif action == "get_all":
        result = get_all_templates(central_api=central_api,
                                   group_name=group_name,
                                   limit=limit, offset=offset,
                                   template=template_name,
                                   device_type=device_type, version=version,
                                   model=model)

    elif action == "create" or action == "update":
        result = create_update_template(central_api=central_api,
                                        group_name=group_name,
                                        template_name=template_name,
                                        device_type=device_type,
                                        version=version, model=model,
                                        action=action,
                                        file=local_file_path)

    elif action == "delete":
        result = delete_template(central_api, group_name, template_name)

    else:
        module.fail_json(changed=False, msg="Unsupported or no action provided"
                                            " in playbook")

    return result


def main():
    '''
    Central-template-related parameters definitions and response handling for
    module
    '''
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, type='str',
                        choices=["get_template_text", "get_all", "update",
                                 "create", "delete"]),
            group_name=dict(required=True, type='str'),
            limit=dict(required=False, type='int', default=20),
            offset=dict(required=False, type='int', default=0),
            template_name=dict(required=False, type='str'),
            device_type=dict(required=False, type='str',
                             choices=["IAP", "ArubaSwitch", "CX",
                                      "MobilityController"]),
            version=dict(required=False, type='str', default="ALL"),
            model=dict(required=False, type='str', default="ALL"),
            local_file_path=dict(required=False, type='path', default=None)
        ))
    success_codes = [200, 201]
    exit_codes = [304, 400, 404]
    changed = False
    if "get" not in module.params.get('action'):
        changed = True
    result = api_call(module)

    try:
        result['resp'] = json.loads(result['resp'])
    except (TypeError, ValueError):
        pass

    if result['code'] and result['code'] in success_codes:
        module.exit_json(changed=changed, msg=result['resp'],
                         response_code=result['code'])
    elif result['code'] and result['code'] in exit_codes:
        module.exit_json(changed=False, msg=result['resp'],
                         response_code=result['code'])
    else:
        module.fail_json(changed=False, msg=result['resp'],
                         response_code=result['code'])


if __name__ == '__main__':
    main()
