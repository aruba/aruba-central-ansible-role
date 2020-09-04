# module: central_sites

description: This module provides a mechanism to interact with sites used for monitoring devices on Aruba Central. 

##### ARGUMENTS
```YAML
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
```

##### EXAMPLES
```YAML
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
```
