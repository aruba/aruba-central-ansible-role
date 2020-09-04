# module: central_devices

description: This module provides a mechanism to move devices between groups as well as to obtain configuration information of devices and templates on Aruba Central.

##### ARGUMENTS
```YAML
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
```

##### EXAMPLES
```YAML
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
```
