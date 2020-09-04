#!/usr/bin/python
'''
Central Variables Ansible Module
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
module: central_variables
version_added: 2.9.0
short_descriptions: REST API module for device variables on Aruba Central
description: This module provides a mechanism to interact with configuration
             variables for devices managed by Aruba Central. It supports the
             upload of a JSON-based file wherein variables for all/multiple
             devices are defined, organized by device serial number.
options:
    action:
        description:
            - Action to be performed on the variable(s) for the device(s)
        required: true
        type: str
        choices:
            - get (Gets all variables for a single device)
            - get_all (Gets all variables for all devices)
            - create (Creates new, i.e. previously undefined, variables for a
              single device)
            - create_all (Creates new variables for multiple/all devices using
              a JSON file upload)
                - Essentially performs the "create" operation for multiple/all
                  devices
            - update (Updates existing variables as well as creates new
              variables for a single device)
                - Does not remove existing variables that are not defined in
                  this operation
                - Adds new variables that are defined in this operation
            - update_all (Updates variables for multiple/all devices using a
              JSON file upload)
                - Essentially performs the "update" operation for multiple/all
                  devices
            - replace (Replaces existing variables as well as creates new
              variables for a single device)
                - Removes existing variables that are not defined in this
                  operation
                - Adds new variables that are defined in this operation
            - replace_all (Replaces variables for all devices using a JSON
              file upload)
                - Essentially performs the "replace" operation for all devices
            - delete (Removes all variables for a single device)
    device_serial:
        description:
            - Serial number of the device
            - Used with actions "get", "create", "update", "replace",
              and "delete"
        required: false
        type: str
    device_mac:
        description:
            - MAC address of the device
            - Used with actions "create", "update", and "replace"
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
            - Number of items to be skipped before returning the data, which
              is useful for pagination
            - Used optionally as a filter parameter for "get_all"
        required: false
        type: int
        default: 0
    variables:
        description:
            - Dictionary containing variables to be applied to a single device
            - Contains key-value pairs wherein the key is the variable name and
              value is the variable value
            - Used with actions "create", "update", and "replace"
        required: false
        type: dict
    local_file_path:
        description:
            - Full local file path for a JSON file that consist variables for
              all/multiple devices based on device serial number
            - Used with actions "create_all", "update_all", and "replace_all"
        required: false
        type: str

"""
EXAMPLES = """
#Usage Examples
- name: Get variables for a single device
  central_variables:
    action: get
    device_serial: CNXXXXXXXX

- name: Get variables for all(20) devices
  central_variables:
    action: get_all
    limit: 20
    offset: 0

- name: Create/set template variables for all/multiple devices using a JSON file  # NOQA
  central_variables:
    action: create_all
    local_file_path: /home/user/variables.json

- name: Create/set template variables for a single device using device serial
  central_variables:
    action: create
    device_serial: CNXXXXXXXX
    device_mac: aa:aa:aa:bb:bb:bb
    variables:
      zonename: First-Floor
      ssid_name: Employee-test
      vc_name: Instant-AP_VC
      hostname: IAP-1

- name: Update template variables for all/multiple devices using a JSON file
  central_variables:
    action: update_all
    local_file_path: /home/user/variables.json

- name: Update template variables for a single device
  central_variables:
    action: update
    device_serial: CNXXXXXXXX
    device_mac: aa:aa:aa:bb:bb:bb
    variables:
      zonename: Lobby

- name: Replace all or delete some of the template variables for all/multiple devices using a JSON file  # NOQA
  central_variables:
    action: replace_all
    local_file_path: /home/user/variables.json

- name: Replace all or delete some of the template variables for a single device
  central_variables:
    action: replace
    device_serial: CNXXXXXXXX
    device_mac: aa:aa:aa:bb:bb:bb
    variables:
      zonename: Second-Floor
      hostname: IAP-2

- name: Delete all template variables for a single device
  central_variables:
    action: delete
    device_serial: CNXXXXXXXX
"""

import json  # NOQA
from ansible.module_utils.basic import AnsibleModule  # NOQA
from ansible.module_utils.central_http import CentralApi  # NOQA


def error_msg(action):
    '''
    Error handler for errors related to missing playbook parameters for
    variables module
    '''
    result = {"resp": None, "code": 400}
    if action == "get_all" or action == 'delete':
        resp = "Device serial number is not present in the playbook"
    elif action == "set":
        resp = "Device serial number, MAC address, or variable definitions" \
               " are not present in playbook"
    elif action == "set_all":
        resp = "Local file path is not present in the playbook"
    result['resp'] = resp
    return result


def get_variables(central_api, device_serial):
    '''
    Gets all variables for a single device based on the device serial number
    '''
    if device_serial is not None:
        path = "/configuration/v1/devices/" + str(device_serial) +\
               "/template_variables"
        headers = central_api.get_headers(False, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("get_all")


def get_all_variables(central_api, limit, offset):
    '''
    Gets all variables for all devices based on the limit and offset value for
    number of entries in response
    '''
    endpoint = "/configuration/v1/devices/template_variables"
    query_params = {"limit": limit, "offset": offset}
    path = central_api.get_url(endpoint, query_params)
    headers = central_api.get_headers(False, "get")
    result = central_api.get(path=path, headers=headers)
    return result


def set_device_variables(central_api, action, device_serial, device_mac,
                         variables):
    '''
    Modifies variables for a single device  based on device serial number
    and MAC address
    Performs either a create, update, or replace
    '''
    if device_serial is not None and device_mac is not None and\
            variables is not None:
        path = "/configuration/v1/devices/"+str(device_serial) +\
               "/template_variables"
        data = {}
        data["_sys_serial"] = device_serial
        data["_sys_lan_mac"] = device_mac
        for key, val in variables.items():
            data[key] = val
        data = {"variables": data}
        headers = central_api.get_headers(False, "post")
        if action.lower() == 'create':
            result = central_api.post(path=path, headers=headers, data=data)
        elif action.lower() == 'update':
            result = central_api.patch(path=path, headers=headers, data=data)
        elif action.lower() == 'replace':
            result = central_api.put(path=path, headers=headers, data=data)
        return result
    return error_msg("set")


def set_all_variables(central_api, action, local_file_path):
    '''
    Modifies variables for mulitple/all devices by uploading a JSON file
    Performs either a create_all, update_all, or replace_all
    '''
    if local_file_path is not None:
        path = "/configuration/v1/devices/template_variables"
        headers = central_api.get_headers(True, "post")
        if action == 'create_all':
            query_params = {"format": "JSON"}
            path = central_api.get_url(path, query_params)
            result = central_api.post(path=path, headers=headers,
                                      filename=local_file_path)
        elif action == 'update_all':
            result = central_api.patch(path=path, headers=headers,
                                       filename=local_file_path)
        elif action == 'replace_all':
            path = "/configuration/v1/devices/template_variables"
            result = central_api.put(path=path, headers=headers,
                                     filename=local_file_path)
        return result
    return error_msg("set_all")


def delete_variables(central_api, device_serial):
    '''
    Deletes all variables for a single device
    '''
    if device_serial is not None:
        path = "/configuration/v1/devices/" + str(device_serial) +\
               "/template_variables"
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
    device_serial = module.params.get('device_serial')
    device_mac = module.params.get('device_mac')
    limit = module.params.get('limit')
    offset = module.params.get('offset')
    variables = module.params.get('variables')
    local_file_path = module.params.get('local_file_path')

    if action == "get":
        result = get_variables(central_api, device_serial)

    elif action == "get_all":
        result = get_all_variables(central_api, limit, offset)

    elif action == "create" or action == "update" or action == "replace":
        result = set_device_variables(central_api, action, device_serial,
                                      device_mac, variables)

    elif action == "create_all" or action == "update_all"\
            or action == "replace_all":
        result = set_all_variables(central_api, action, local_file_path)

    elif action == "delete":
        result = delete_variables(central_api, device_serial)

    else:
        module.fail_json(changed=False,
                         msg="Unsupported action provided in playbook")

    return result


def main():
    '''
    Central device variable related parameters definitions and response
    handling for module
    '''
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, type='str',
                        choices=["get", "get_all", "create", "create_all",
                                 "update", "update_all", "replace",
                                 "replace_all", "delete"]),
            device_serial=dict(required=False, type='str'),
            device_mac=dict(required=False, type='str'),
            limit=dict(required=False, type='int', default=20),
            offset=dict(required=False, type='int', default=0),
            variables=dict(required=False, type='dict', default={}),
            local_file_path=dict(required=False, type='str', default=None)
            ))

    success_codes = [200, 201]
    exit_codes = [304, 400, 404]
    changed = False
    if "get" not in module.params.get('action').lower():
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
