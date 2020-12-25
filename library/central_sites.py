#!/usr/bin/python
'''
Central Sites Ansible Module
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
module: central_sites
version_added: 2.9.0
short_descriptions: REST API module for sites on Aruba Central
description: This module provides a mechanism to interact with sites used
             for monitoring devices on Aruba Central
options:
    action:
        description:
            - Action to be performed on the site(s)
            - "get" gets details of a particular site
            - "get_multiple_sites" gets number of sites and details of each
              site
            - "create" creates a new site
                - Either geolocation OR "site_address" should be specified,
                  but not both
            - "update" updates the site name and/or location
                - For location, either geolocation OR "site_address" should
                  be specified, but not both
            - "associate" associates devices to a site
            - "unassociate" unassociates devices from a site
            - "delete" deletes a site
        required: true
        type: str
        choices:
            - get
            - get_multiple_sites
            - create
            - update
            - associate
            - unassociate
            - delete
    site_id:
        description:
            - Numerical ID of the site
            - Used with actions "get", "update", "associate", "unassociate",
              and "delete"
        required: false
        type: int
    site_name:
        description:
            - Name of the site
            - Used with actions "create" and "update"
        required: false
        type: str
    calculate_total:
        description:
            - Counts total number of labels
            - Used optionally with action "get_multiple_sites"
        required: false
        type: bool
        default: true
    site_address:
        description:
            - Full street address of the site
            - Mutually exclusive with "geolocation"
        required: false
        type: dict
        options:
            address:
                description:
                    - Address line(s)
                required: true
                type: str
            city:
                description:
                    - City
                required: true
                type: str
            state:
                description:
                    - State
                required: true
                type: str
            country:
                description:
                    - Country
                required: true
                type: str
            zipcode:
                description:
                    - ZIP code
                required: false
                type: str
    geolocation:
        description:
            - Latitude and longitude coordinates of the site
            - Mutually exclusive with "site_address"
        required: false
        type: dict
        options:
            latitude:
                description:
                    - Latitude coordinate
                required: true
                type: str
            longitude:
                description:
                    - Longitude coordinate
                required: true
                type: str
    device_type:
        description:
            - Type of device(s)
            - Used with actions "associate" and "unassociate"
        required: false
        type: str
        choices:
            - IAP
            - SWITCH
            - CONTROLLER
    device_list:
        description:
            - List of device serial numbers
            - A maximum of 5000 device serial numbers are allowed
            - Used with actions "associate" and "unassociate"
        required: false
        type: list
    limit:
        description:
            - Number of records to be returned
            - A maximum of 1000 records can be returned
            - Used optionally as a filter parameter for "get_multiple_sites"
        required: false
        type: int
        default: 100
    offset:
        description:
            - Number of items to be skipped before returning the data, which
              is useful for pagination
            - Used optionally as a filter parameter for "get_multiple_sites"
        required: false
        type: int
        default: 0
    sort:
        description:
            - Sorts output by alphabetical (+site_name) or reverse alphabetical
              (-site_name) order of site name
            - Used optionally with action "get_multiple_sites"
        required: false
        type: str
        default: +site_name
        choices:
            - +site_name
            - -site_name
"""
EXAMPLES = """
#Usage Examples
- name: Get site details for a single site
  central_sites:
    action: get
    site_id: 40

- name: Get site details for multiple sites
  central_sites:
    action: get_multiple_sites
    calculate_total: True
    sort: +site_name
    offset: 0
    limit: 20

- name: Create a new site using site address
  central_sites:
    action: create
    site_name: test-site
    site_address:
      address: 3333 Scott Blvd
      city: Santa Clara
      state: California
      country: United States
      zipcode: 95054

- name: Create a new site using geolocation cordinates
  central_sites:
    action: create
    site_name: test-site
    geolocation:
      latitude: 15.3241334
      longitude: -124.5132145

- name: Update an existing site's name and/or address
  central_sites:
    action: update
    site_id: 42
    site_name: test-site
    site_address:
      address: 3333 Scott Boulevard Building D
      city: Santa Clara
      state: California
      country: United States
      zipcode: 95054

- name: Update an existing site's name and/or geolocation coordinates
  central_sites:
    action: update
    site_id: 43
    site_name: test-site
    geolocation:
      latitude: 18.3241334
      longitude: -122.5132145

- name: Associate devices to a site
  central_sites:
    action: associate
    site_id: 43
    device_type: IAP
    device_list:
      - CNXXXXXXXX
      - CNXXXXXXYY
      - CNXXXXXXZZ

- name: Unassociate devices from a site
  central_sites:
    action: unassociate
    site_id: 43
    device_type: IAP
    device_list:
     - CNXXXXXXXX
     - CNXXXXXXYY

- name: Delete an existing site
  central_sites:
    action: delete
    site_id: 42
"""

import json  # NOQA
from ansible.module_utils.basic import AnsibleModule  # NOQA
from ansible.module_utils.central_http import CentralApi  # NOQA


def error_msg(reason):
    '''
    Error handler for errors related to missing playbook parameters in sites
    module
    '''
    result = {"resp": None, "code": 400}
    if reason == "get_site" or reason == "delete":
        resp = "Side ID is not present in the playbook"
    elif reason == "site_info":
        resp = ("Either geolocation or site address can be used for creating"
                " or updatiing a site, not both.")
    elif reason == "create_site":
        resp = ("Check if site name and either geolocation or site address are"
                " present in the playbook.")
    elif reason == "update_site":
        resp = ("Check if site name and a valid site ID, along with either"
                " geolocation or site address, are present in the playbook.")
    elif reason == "association":
        resp = ("Site ID, device type, or device list not present in the"
                " playbook.")

    result['resp'] = resp
    return result


def get_site(central_api, site_id):
    '''
    Gets details of a particular site, by site ID
    '''
    if site_id is not None:
        path = "/central/v2/sites/" + str(site_id)
        headers = central_api.get_headers(False, "get")
        result = central_api.get(path=path, headers=headers)
        return result
    return error_msg("get_site")


def get_multiple_sites(central_api, filters):
    '''
    Gets site information for multiple sites, with optional filters to
    filter the output
    '''
    endpoint = "/central/v2/sites"
    query_params = filters
    path = central_api.get_url(endpoint, query_params)
    headers = central_api.get_headers(False, "get")
    result = central_api.get(path=path, headers=headers)
    return result


def create_site(central_api, data):
    '''
    Creates a new site with site name and site address/geolocation. If
    successful, returns the site ID of the newly created site
    '''
    if data and data['site_name'] is not None:
        path = "/central/v2/sites"
        headers = central_api.get_headers(False, "get")
        result = central_api.post(path=path, data=data, headers=headers)
        return result
    return error_msg("create_site")


def update_site(central_api, site_id, data):
    '''
    Updates or modifies site name and/or site address/geolocation
    '''
    if site_id is not None and data['site_name'] is not None:
        path = "/central/v2/sites/"+str(site_id)
        headers = central_api.get_headers(False, "get")
        result = central_api.patch(path=path, data=data, headers=headers)
        return result
    return error_msg("update_site")


def delete_site(central_api, site_id):
    '''
    Deletes an existing site by site ID
    '''
    if site_id is not None:
        path = "/central/v2/sites/"+str(site_id)
        headers = central_api.get_headers(False, "get")
        result = central_api.delete(path=path, headers=headers)
        return result
    return error_msg("delete")


def site_association(central_api, action, site_id, device_type, device_list):
    '''
    Associates/unassociates devices to/from a site by the specified list of
    device serial numbers and the site ID
    '''
    if site_id is not None and device_type is not None and device_list\
            is not None:
        path = "/central/v2/sites/associations"
        headers = central_api.get_headers(False, "post")
        data = {"site_id": site_id, "device_type": device_type,
                "device_ids": device_list}
        if action == "associate":
            result = central_api.post(path=path, headers=headers, data=data,)
        elif action == "unassociate":
            result = central_api.delete(path=path, headers=headers, data=data)
        return result
    return error_msg("association")


def api_call(module):
    '''
    Uses playbook parameters to determine type of API request to be made
    '''
    central_api = CentralApi(module)
    action = module.params.get('action').lower()
    site_id = module.params.get('site_id')
    site_name = module.params.get('site_name')
    site_address = module.params.get('site_address')
    geolocation = module.params.get('geolocation')
    device_list = module.params.get('device_list')
    filters = {"calculate_total": module.params.get('calculate_total'),
               "limit": module.params.get('limit'),
               "offset": module.params.get('offset'),
               "sort": module.params.get('sort')}
    device_type = module.params.get('device_type')

    if action == "get":
        result = get_site(central_api, site_id)

    elif action == "get_multiple_sites":
        result = get_multiple_sites(central_api, filters)

    elif action == 'delete':
        result = delete_site(central_api, site_id)

    elif action == "associate" or action == "unassociate":
        result = site_association(central_api, action, site_id, device_type,
                                  device_list)

    elif action == 'create' or action == 'update':
        data = {}
        site_dict = {"site_name": site_name}
        addr_dict = {"site_address": site_address}
        geo_dict = {"geolocation": geolocation}
        if geolocation is not None and site_address is not None:
            result = error_msg("site_info")
            module.exit_json(changed=False, msg=result['resp'],
                             response_code=result['code'])
        elif site_address is not None:
            data = dict(list(site_dict.items()) + list(addr_dict.items()))
        elif geolocation is not None:
            data = dict(list(site_dict.items()) + list(geo_dict.items()))
        if action == "create":
            result = create_site(central_api, data)
        elif action == "update":
            result = update_site(central_api, site_id, data)

    else:
        module.fail_json(changed=False, msg="Unsupported action provided in"
                                            " playbook")

    return result


def main():
    '''
    Central sites-related parameter definitions and response handling for
    module
    '''
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, type='str',
                        choices=["get", "get_multiple_sites", "create",
                                 "delete", "update", "associate",
                                 "unassociate"]),
            site_id=dict(required=False, type='int'),
            site_name=dict(required=False, type='str'),
            site_address=dict(required=False, type='dict', default=None,
                              options=dict(
                                  address=dict(require=True, type='str'),
                                  city=dict(require=True, type='str'),
                                  state=dict(require=True, type='str'),
                                  country=dict(require=True, type='str'),
                                  zipcode=dict(require=False, type='str',
                                               default='')
                               )),
            geolocation=dict(required=False, type='dict', default=None,
                             options=dict(
                                 latitude=dict(require=False, type='str'),
                                 longitude=dict(require=False, type='str')
                              )),
            calculate_total=dict(required=False, type='bool', default=True),
            limit=dict(required=False, type='int', default=100),
            offset=dict(required=False, type='int', default=0),
            sort=dict(required=False, type='str', default="+site_name"),
            device_list=dict(required=False, type='list', default=None),
            device_type=dict(required=False, type='str',
                             choices=["SWITCH", "IAP",
                                      "CONTROLLER"]),
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
