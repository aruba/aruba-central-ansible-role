#!/usr/bin/python
'''
Central Groups Ansible Module
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
module: central_groups
version_added: 2.9.0
short_descriptions: REST API module for groups on Aruba Central
description: This module provides a mechanism to interact with groups used for
             configuration management of devices on Aruba Central.
options:
    action:
        description:
            - Action to be performed on the group(s)
            - "get_groups" gets names of existing groups
            - "get_group_mode" gets group modes of existing groups
            - "clone" creates a new group by cloning an existing group
            - "update" updates the group password of an existing UI group
            - "create" creates a new group
            - "delete" deletes an existing group
        required: true
        type: str
        choices:
            - get_groups
            - get_group_mode
            - clone
            - update
            - create
            - delete
    group_name:
        description:
            - Name of the group
            - Used with actions "clone", "update", "create", and "delete"
        required: false
        type: str
    group_list:
        description:
            - List of group names
            - At most 20 names can be listed
            - Used with action "get_group_mode"
        required: false
        type: list
    group_attributes:
        description:
            - Group attributes to define group password and a boolean
              determining whether it is a template group or UI group OR
              dictionary containing two booleans to determine the allowable
              templates (wired and/or wireless) for the template group
            - Used with actions "create" and "update"
        required: false
        type: dict
    clone_from_group:
        description:
            - Name of existing group from which the new group is cloned
            - Used with action "clone"
        required: false
        type: str
    limit:
        description:
            - Maximum number of records to be returned
            - Used optionally as a filter parameter for "get_groups"
        required: false
        type: int
        default: 20
    offset:
        description:
            - Number of items to be skipped before returning the data, which
              is useful for pagination
            - Used optionally as a filter parameter for "get_groups"
        required: false
        type: int
        default: 0

"""
EXAMPLES = """
#Usage Examples
- name: Get all the UI and template groups on Central
  central_groups:
    action: get_groups
    limit: 20
    offset: 0

- name: Get groups' configuration modes ("UI" or "template")
  central_groups:
    action: get_group_mode
    group_list:
      - group-name-1
      - group-name-2

- name: Create a new group ("template" for wired, "UI" for wireless)
  central_groups:
    action: create
    group_name: new-test-group
    group_attributes:
      group_password: admin@12345
      template_group:
        wired: True
        wireless: False

- name: Update an existing group (only available for UI groups)
  central_groups:
    action: update
    group_name: new-test-group
    group_attributes:
      group_password: Aruba@2222
      template_group: False

- name: Clone an existing group
  central_groups:
    action: clone
    group_name: new-group
    clone_from_group: new-test-group

- name: Delete a group
  central_groups:
    action: delete
    group_name: new-test-group

"""

import json  # NOQA
from ansible.module_utils.basic import AnsibleModule  # NOQA
from ansible.module_utils.central_http import CentralApi  # NOQA


def error_msg(method):
    '''
    Error handler for errors related to missing playbook parameters for groups
    module
    '''
    result = {"resp": None, "code": 400}
    if method == "create" or method == "update":
        resp = "Group name or Group attributes not present in the playbook"
    elif method == "delete":
        resp = "Group name to be deleted not present in the playbook"
    elif method == "clone":
        resp = "Group name or clone-from-group parameters not present in " \
               "the playbook"
    elif method == "get":
        resp = "List of groups (group_list) not present in the playbook"
    result['resp'] = resp
    return result


def get_groups(central_api, limit, offset):
    '''
    Gets names of existing Central Groups
    '''
    endpoint = "/configuration/v2/groups"
    query_params = {"limit": limit, "offset": offset}
    headers = central_api.get_headers(False, "get")
    path = central_api.get_url(endpoint, query_params)
    result = central_api.get(path=path, headers=headers)
    return result


def get_group_mode(central_api, group_list):
    '''
    Gets group modes of existing Central Groups
    '''
    if group_list is not None:
        groups = central_api.get_list_params(group_list)
        query_params = {"groups": groups}
        headers = central_api.get_headers(False, "get")
        path = central_api.get_url("/configuration/v2/groups/template_info",
                                   query_params)
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("get")


def clone(central_api, group_name, clone_from_group):
    '''
    Creates a new group by cloning an existing group
    '''
    if group_name and clone_from_group is not None:
        path = "/configuration/v2/groups/clone"
        data = {"group": group_name, "clone_group": clone_from_group}
        headers = central_api.get_headers(False, "post")
        result = central_api.post(path=path, headers=headers, data=data)
        return result
    return error_msg("clone")


def create_group(central_api, group_name, group_attributes):
    '''
    Creates a new template or UI group based on group_attributes
    '''
    if group_name and group_attributes is not None:
        path = "/configuration/v2/groups"
        data = {
            "group": group_name,
            "group_attributes": {
                "group_password": group_attributes['group_password'],
                "template_info": {
                    "Wired": group_attributes['template_group']['wired'],
                    "Wireless": group_attributes['template_group']['wireless']
                }}}
        headers = central_api.get_headers(False, "post")
        result = central_api.post(path=path, headers=headers, data=data)
        result['resp'] = json.loads(result['resp'])
        return result
    return error_msg("create")


def update_group(central_api, group_name, group_attributes):
    '''
    Updates an existing UI group to change its password
    '''
    if group_name and group_attributes is not None:
        path = "/configuration/v1/groups/"+str(group_name)
        data = group_attributes
        headers = central_api.get_headers(False, "post")
        result = central_api.patch(path=path, headers=headers, data=data)
        return result
    return error_msg("update")


def delete_group(central_api, group_name):
    '''
    Deletes an existing group
    '''
    if group_name is not None:
        path = "/configuration/v1/groups/"+str(group_name)
        headers = central_api.get_headers(False, "delete")
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
    group_list = module.params.get('group_list')
    group_attributes = module.params.get('group_attributes')
    limit = module.params.get('limit')
    offset = module.params.get('offset')
    clone_from_group = module.params.get('clone_from_group')

    if action == "get_groups":
        result = get_groups(central_api, limit, offset)

    elif action == "get_group_mode":
        result = get_group_mode(central_api, group_list)

    elif action == "clone":
        result = clone(central_api, group_name, clone_from_group)

    elif action == "create":
        result = create_group(central_api, group_name, group_attributes)

    elif action == "update":
        result = update_group(central_api, group_name, group_attributes)

    elif action == "delete":
        result = delete_group(central_api, group_name)

    else:
        module.fail_json(changed=False,
                         msg="Unsupported action provided in playbook")

    return result


def main():
    '''
    Central Groups related parameters definitions and response handling for
    module
    '''
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, type='str', choices=["get_groups",
                                                            "get_group_mode",
                                                            "clone", "update",
                                                            "create",
                                                            "delete"]),
            limit=dict(required=False, type='int', default=20),
            offset=dict(required=False, type='int', default=0),
            group_list=dict(required=False, type='list'),
            group_name=dict(required=False, type='str'),
            group_attributes=dict(required=False, type='dict'),
            clone_from_group=dict(required=False, type='str')
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
