# module: central_templates

description: This module provides a mechanism to interact with or upload configuration templates that are used for group-level and device-level configuration on Aruba Central.

##### ARGUMENTS
```YAML
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
```

##### EXAMPLES
```YAML
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
```
