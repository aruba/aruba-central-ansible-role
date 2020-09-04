# module: central_variables

description: This module provides a mechanism to interact with configuration variables for devices managed by Aruba Central. It supports the upload of a JSON-based file wherein variables for all/multiple devices are defined, organized by device serial number.  

##### ARGUMENTS
```YAML
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
```

##### EXAMPLES
```YAML
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
```
