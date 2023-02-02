# module: central_groups

description: This module provides a mechanism to interact with groups used for configuration management of devices on Aruba Central.

##### ARGUMENTS

```YAML
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
```

##### EXAMPLES

```YAML
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
```
