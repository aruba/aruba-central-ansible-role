#!/usr/bin/python
'''
Central Devices Ansible Module
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
module: central_devices
version_added: 2.9.0
short_descriptions: REST API module for devices on Aruba Central
description: This module provides a mechanism to interact with devices to
             perform device-pertinent operations
options:
    action:
        description:
            - Action to be performed on the device(s)

            - "get_device_group" gets the name of the group that a device
              belongs to

            - "get_running_config" gets last known running-config of a device
              as multipart/form-data

            - "get_config_details" gets configuration details for a device
              belonging to a template group
                - Applicable only to devices in template groups
                - Gets the following details:
                    - Central-side configuration
                    - Device running configuration
                    - Configuration error details
                    - Template error details and status of device

            - "get_template_info" gets template(s) info for a list of devices
                - Applicable only to devices in template groups
                - For each device, gets the following details:
                    - Name of group that the device and template belong to
                    - Name of template on Central
                    - Hash code of template
                    - Device type for which template is applicable
                    - Device model for which template is applicable
                    - Device firmware versions for which the template is
                      applicable

            - "get_templates_for_groups" gets template(s) info for devices in
              qualified groups
                - Applicable only to devices in template groups
                - For each device that belongs to the qualified groups,
                  gets the same info as "get_template_info" action
                - Can (and perhaps should) be used with EITHER
                  "include_groups" OR "exclude_groups"
                    - If neither is specified, all groups are qualified
                - "include_groups" is used to specify a list of qualified
                  groups
                - "exclude_groups" is used to specify that all groups except
                  for the mentioned groups are qualified

            - "get_templates_using_hash" gets template(s) info for devices
              that are using the qualified template(s)
                - Applicable only to devices in template groups
                - For each device using a qualified template (as specified by
                  template hash), gets the same info as "get_template_info"
                  action
                - Can (and perhaps should) be used with "exclude_hash"
                    - If "exclude_hash" is true, all templates are qualified
                      except the one with the given hash
                    - If "exclude_hash" is false, only the template with the
                      given hash is qualified

            - "get_variablised_switch_template" gets the variablised template
              for an AOS-S switch as multipart/form-data
                - Returns both the template and the variables information

            - "set_switch_ssh_connection" sets an AOS-S switch's SSH username
              and password

            - "move_devices" moves devices (specified as a list of serial
              numbers) to a group
        required: true
        type: str
        choices:
            - get_device_group
            - get_running_config
            - get_config_details
            - get_template_info
            - get_templates_for_groups
            - get_templates_using_hash
            - get_variablised_switch_template
            - set_switch_ssh_connection
            - move_devices
    group_name:
        description:
            - Name of the group
            - Used with action "move_devices"
        required: false
        type: str
    device_serial:
        description:
            - Serial number of the device
            - Used with actions "get_device_group", "get_running_config",
              "get_config_details", "get_variablised_switch_template",
              and "set_switch_ssh_connection"
        required: false
        type: str
    device_type:
        description:
            - Type of device for which the template is applicable
            - Used with actions "get_templates_for_groups" and
              "get_templates_using_hash"
        required: false
        type: str
        choices:
            - IAP
            - ArubaSwitch
            - CX
            - MobilityController
    device_serial_list:
        description:
            - List of device serial numbers
            - Used with actions "move_devices" and "get_template_info"
            - When moving an IAP, all APs in a cluster will be moved to
              the specified group if the serial number of conductor AP is
              provided in this list; serial number(s) of member IAP(s) will
              be ignored
        required: false
        type: list
    full_details:
        description:
            - Used with action "get_config_details" action to determine
              whether the action retrieves a summary of device configuration
              info or the comprehensive details of device configuration info
            - Specify as true only if the detailed response of a device's
              configuration info is required, as passing true might result
              in slower API response and performance
        required: false
        type: bool
        default: false
    include_groups:
        description:
            - List of groups for which "get_templates_for_groups" will include
            - Used with action "get_templates_for_groups"
            - Mutually exclusive with "exclude_groups"
        required: false
        type: list
    exclude_groups:
        description:
            - List of group names for which "get_templates_for_groups" will
              exclude
            - Used with action "get_templates_for_groups"
            - Mutually exclusive with "include_groups"
        required: false
        type: list
    template_hash:
        description:
            - Hash string of template for which "get_templates_using_hash"
              either includes or excludes
            - Used with action "get_templates_using_hash"
            - Behavior (inclusion or exclusion) determined by "exclude_hash"
              parameter
        required: false
        type: str
    exclude_hash:
        description:
            - Determines behavior of "get_templates_using_hash"
            - Used with action "get_templates_using_hash"
        required: false
        type: bool
        default: false
    limit:
        description:
            - Maximum number of records to be returned
            - Used optionally as a filter parameter for
            "get_templates_for_groups" and "get_templates_using_hash"
        required: false
        type: int
        default: 20
    offset:
        description:
            - Number of items to be skipped before returning the data, which
              is useful for pagination
            - Used optionally as a filter parameter for
              "get_templates_for_groups" and "get_templates_using_hash"
        required: false
        type: int
        default: 0
    sw_username:
        description:
            - Switch username to establish SSH connection to AOS-S switch
            - Used with action "set_switch_ssh_connection"
        required: false
        type: str
    sw_password:
        description:
            - Switch password to establish SSH connection to AOS-S switch
            - Used with action "set_switch_ssh_connection"
        required: false
        type: str

"""
EXAMPLES = """
#Usage Examples
- name: Move devices to a group
  central_devices:
    action: move_devices
    group_name: new-group
    device_serial_list:
      - CNXXXXXXXX
      - CNXXXXXXYY

- name: Get group name to which a device belongs
  central_devices:
    action: get_device_group
    device_serial: CNXXXXXXXX

- name: Get the last known running configuration of a device
  central_devices:
    action: get_running_config
    device_serial: CNXXXXXXXX

- name: Get configuration details of a device (only for devices in template groups)  # NOQA
  central_devices:
    action: get_config_details
    device_serial: CNXXXXXXXX
    full_details: False

- name: Get template info for listed devices
  central_devices:
    action: get_template_info
    device_serial_list:
      - CNXXXXXXXX
      - CNXXXXXXYY
      - CNXXXXXXZZ

- name: Get template info for devices in all groups
  central_devices:
    action: get_templates_for_groups
    limit: 20
    offset: 0
    device_type: IAP

- name: Get template info for devices in all groups, except specified groups  # NOQA
  central_devices:
    action: get_templates_for_group
    limit: 20
    offset: 0
    exclude_groups:
      - group-name-1
      - group-name-2
    device_type: IAP

- name: Get template info for devices in specified groups
  central_devices:
    action: get_templates_for_groups
    limit: 20
    offset: 0
    include_groups:
      - group-name-1
      - group-name-2
    device_type: IAP

- name: Get template info for devices using given template hash (Only allowed for users having all_groups access or admin)  # NOQA
  central_devices:
    action: get_templates_using_hash
    template_hash: f6f4d3cxxxxxxxxxxxxxxxxxxxxxxx
    limit: 20
    offset: 0
    exclude_hash: False
    device_type: IAP

- name: Get template body and variables info for an Aruba Switch
  central_devices:
    action: get_variablised_switch_template
    device_serial: CNXXXXXXXX

- name: Set SSH username and password for an Aruba Switch
  central_devices:
    action: set_switch_ssh_connection
    device_serial: CNXXXXXXXX
    sw_username: test@test.com
    sw_password: test@123
"""

import json  # NOQA
from ansible.module_utils.basic import AnsibleModule  # NOQA
from ansible.module_utils.central_http import CentralApi  # NOQA


def error_msg(action):
    '''
    Error handler for errors related to missing playbook parameters for
    devices module
    '''
    lst = ["device_group", "running_cfg", "cfg_details", "sw_template"]
    result = {"resp": None, "code": 400}
    if action in lst:
        resp = "Device serial number is not present in the playbook"
    elif action == "move_devices" or action == 'template_info':
        resp = "Group name or device serial number list is not present in" \
               " the playbook"
    elif action in lst:
        resp = "Device serial number is not present in the playbook"
    elif action == "templates_for_group" or action == "templates_using_hash":
        resp = "Device type is not present in the playbook"
    elif action == "sw_ssh":
        resp = "Device serial number, switch username, or switch password is" \
               " not present in playbook"
    result['resp'] = resp
    return result


def move_devices(central_api, group_name, device_serial_list):
    '''
    Moves devices (specified as a list of serial numbers) to a group
    '''
    if group_name is not None and device_serial_list is not None:
        path = "/configuration/v1/devices/move"
        headers = central_api.get_headers(False, "post")
        data = {"group": group_name, "serials": device_serial_list}
        result = central_api.post(path=path, headers=headers, data=data)
        return result
    return error_msg("move_devices")


def get_device_group(central_api, device_serial):
    '''
    Gets name of the group that a device belongs to
    '''
    if device_serial is not None:
        path = "/configuration/v1/devices/"+str(device_serial)+"/group"
        headers = central_api.get_headers(False, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("device_group")


def get_running_config(central_api, device_serial):
    '''
    Gets last known running configuration of a device (as multipart/form-data)
    '''
    if device_serial is not None:
        path = "/configuration/v1/devices/"+str(device_serial)+"/configuration"
        headers = central_api.get_headers(True, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("running_cfg")


def get_config_details(central_api, device_serial, full_details):
    '''
    Gets configuration details for a device (only applies to devices in
    template groups) as follows:
    - Central-side configuration
    - Device running configuration
    - Configuration error details
    - Template error details and status of device
    '''
    if device_serial is not None:
        endpoint = "/configuration/v1/devices/" + str(device_serial) +\
                   "/config_details"
        query_params = {"details": full_details}
        path = central_api.get_url(endpoint, query_params)
        headers = central_api.get_headers(True, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("cfg_details")


def get_template_meta_info(central_api, device_serial_list):
    '''
    Gets template information for each device in a list of devices as follows:
    - Name of group to which the device and template belong
    - Name of the template on Central
    - Template hash code
    - Device type for which the template is being used
    - Device model for which the template is being used
    - Device version for which the template is being used
    '''
    if device_serial_list is not None:
        endpoint = "/configuration/v1/devices/template"
        query_params = {"device_serials":
                        central_api.get_list_params(device_serial_list)}
        path = central_api.get_url(endpoint, query_params)
        headers = central_api.get_headers(False, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("template_info")


def get_templates_for_groups(central_api, **kwargs):
    '''
    Gets template information for devices in qualified groups.
    For each device belonging to a qualified group, gets the following info:
    - Name of group to which the device and template belong
    - Name of the template on Central
    - Template hash code
    - Device type for which the template is being used
    - Device model for which the template is being used
    - Device version for which the template is being used
    '''
    if kwargs['device_type'] is not None:
        all_groups = True
        endpoint = "/configuration/v1/devices/groups/template"
        key = "exclude_groups"
        groups = []
        if kwargs['exclude_groups']:
            groups = central_api.get_list_params(kwargs['exclude_groups'])
        elif kwargs['include_groups']:
            key = "include_groups"
            groups = central_api.get_list_params(kwargs['include_groups'])
            all_groups = False
        query_params = {"limit": kwargs['limit'], "offset": kwargs['offset'],
                        key: groups, "all_groups": all_groups,
                        "device_type": kwargs['device_type']}
        path = central_api.get_url(endpoint, query_params)
        headers = central_api.get_headers(False, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("templates_for_group")


def get_templates_using_hash(central_api, template_hash, **kwargs):
    '''
    Gets template information for devices using qualified templates.
    Template qualification is determined by the given template_hash and the
    "exclude_hash" parameter.
    - If "exclude_hash" is true, all templates are qualified except the one
      with the given hash
    - If "exclude_hash" is false, only the template with the specified hash
      is qualified
    For each device using the qualified template(s), gets the following info:
    - Name of group to which the device and template belong
    - Name of the template on Central
    - Template hash code
    - Device type for which the template is being used
    - Device model for which the template is being used
    - Device version for which the template is being used
    '''
    if kwargs['device_type'] is not None:
        endpoint = "/configuration/v1/devices/"+str(template_hash)+"/template"
        query_params = {"limit": kwargs['limit'], "offset": kwargs['offset'],
                        "exclude_hash": json.dumps(kwargs['exclude_hash']),
                        "device_type": kwargs['device_type']}
        path = central_api.get_url(endpoint, query_params)
        headers = central_api.get_headers(False, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("templates_using_hash")


def get_variablised_switch_template(central_api, device_serial):
    '''
    Gets both the template body and variables information for an AOS-S switch
    as multipart/form-data
    '''
    if device_serial is not None:
        path = "/configuration/v1/devices/" + str(device_serial) +\
               "/variablised_template"
        headers = central_api.get_headers(True, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("sw_template")


def set_switch_ssh_connection(central_api, device_serial, sw_username,
                              sw_password):
    '''
    Sets the username and password for an AOS-S switch's SSH connection
    '''
    if device_serial is not None and sw_username is not None and\
            sw_password is not None:
        path = "/configuration/v1/devices/" + str(device_serial) +\
               "/ssh_connection"
        headers = central_api.get_headers(False, "post")
        data = {"username": sw_username, "password": sw_password}
        result = central_api.post(path=path, headers=headers, data=data)
        return result
    return error_msg("sw_ssh")


def api_call(module):
    '''
    Uses playbook parameters to determine type of API request to be made
    '''
    central_api = CentralApi(module)
    action = module.params.get('action').lower()
    group_name = module.params.get('group_name')
    include_groups = module.params.get('include_groups')
    exclude_groups = module.params.get('exclude_groups')
    device_type = module.params.get('device_type')
    full_details = module.params.get('full_details')
    device_serial_list = module.params.get('device_serial_list')
    template_hash = module.params.get('template_hash')
    exclude_hash = module.params.get('exclude_hash')
    limit = module.params.get('limit')
    offset = module.params.get('offset')
    device_serial = module.params.get('device_serial')
    sw_username = module.params.get('sw_username')
    sw_password = module.params.get('sw_password')

    if action == "move_devices":
        result = move_devices(central_api, group_name, device_serial_list)

    elif action == "get_device_group":
        result = get_device_group(central_api, device_serial)

    elif action == "get_running_config":
        result = get_running_config(central_api, device_serial)

    elif action == "get_config_details":
        result = get_config_details(central_api, device_serial, full_details)

    elif action == "get_template_info":
        result = get_template_meta_info(central_api, device_serial_list)

    elif action == "get_templates_for_groups":
        result = get_templates_for_groups(central_api=central_api,
                                          device_type=device_type,
                                          limit=limit,
                                          include_groups=include_groups,
                                          offset=offset,
                                          exclude_groups=exclude_groups)

    elif action == "get_templates_using_hash":
        result = get_templates_using_hash(central_api=central_api,
                                          device_type=device_type,
                                          limit=limit,
                                          template_hash=template_hash,
                                          offset=offset,
                                          exclude_hash=exclude_hash)

    elif action == "get_variablised_switch_template":
        result = get_variablised_switch_template(central_api, device_serial)

    elif action == "set_switch_ssh_connection":
        result = set_switch_ssh_connection(central_api, device_serial,
                                           sw_username, sw_password)

    else:
        module.fail_json(changed=False,
                         msg="Unsupported action provided in playbook")

    return result


def main():
    '''
    Central devices-related parameter definitions and response handling for
    module
    '''
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, type='str',
                        choices=["get_device_group", "get_running_config",
                                 "get_config_details", "get_template_info",
                                 "get_templates_for_groups",
                                 "get_templates_using_hash",
                                 "get_variablised_switch_template",
                                 "set_switch_ssh_connection",
                                 "move_devices"]),
            group_name=dict(required=False, type='str'),
            limit=dict(required=False, type='int', default=20),
            offset=dict(required=False, type='int', default=0),
            device_serial=dict(required=False, type='str'),
            device_serial_list=dict(required=False, type='list'),
            include_groups=dict(required=False, type='list', default=[]),
            exclude_groups=dict(required=False, type='list', default=[]),
            template_hash=dict(required=False, type='str'),
            exclude_hash=dict(required=False, type='bool', default=False),
            full_details=dict(required=False, type='bool', default=False),
            sw_username=dict(required=False, type='str'),
            sw_password=dict(required=False, type='str'),
            device_type=dict(required=False, type='str',
                             choices=["IAP", "CX", "ArubaSwitch",
                                      "MobilityController"])
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
