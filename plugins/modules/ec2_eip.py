#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: ec2_eip
version_added: 5.0.0
short_description: manages EC2 elastic IP (EIP) addresses.
description:
  - This module can allocate or release an EIP.
  - This module can associate/disassociate an EIP with instances or network interfaces.
  - This module was originally added to C(community.aws) in release 1.0.0.
options:
  device_id:
    description:
      - The id of the device for the EIP.
      - Can be an EC2 Instance id or Elastic Network Interface (ENI) id.
      - When specifying an ENI id, O(in_vpc) must be V(true).
      - The C(instance_id) alias was removed in release 6.0.0.
    required: false
    type: str
  public_ip:
    description:
      - The IP address of a previously allocated EIP.
      - When O(state=present) and device is specified, the EIP is associated with the device.
      - When O(state=absent) and device is specified, the EIP is disassociated from the device.
    aliases: [ ip ]
    type: str
  state:
    description:
      - When O(state=present), allocate an EIP or associate an existing EIP with a device.
      - When O(state=absent), disassociate the EIP from the device and optionally release it.
    choices: ['present', 'absent']
    default: present
    type: str
  in_vpc:
    description:
      - Allocate an EIP inside a VPC or not.
      - Required if specifying an ENI with O(device_id).
    default: false
    type: bool
  reuse_existing_ip_allowed:
    description:
      - Reuse an EIP that is not associated to a device (when available), instead of allocating a new one.
    default: false
    type: bool
  release_on_disassociation:
    description:
      - Whether or not to automatically release the EIP when it is disassociated.
    default: false
    type: bool
  private_ip_address:
    description:
      - The primary or secondary private IP address to associate with the Elastic IP address.
    type: str
  allow_reassociation:
    description:
      -  Specify this option to allow an Elastic IP address that is already associated with another
         network interface or instance to be re-associated with the specified instance or interface.
    default: false
    type: bool
  tag_name:
    description:
      - When O(reuse_existing_ip_allowed=true), supplement with this option to only reuse
        an Elastic IP if it is tagged with O(tag_name).
    type: str
  tag_value:
    description:
      - Supplements O(tag_name) but also checks that the value of the tag provided in O(tag_name) matches O(tag_value).
    type: str
  public_ipv4_pool:
    description:
      - Allocates the new Elastic IP from the provided public IPv4 pool (BYOIP)
        only applies to newly allocated Elastic IPs, isn't validated when O(reuse_existing_ip_allowed=true).
    type: str
  update_reverse_dns_record:
    description: Whether to update the reverse DNS record of ec2 Elastic IP Address (eip)
    required: false
    type: bool
  allocation_id:
    description: The allocation ID of ec2 EIP.
    required: false
    type: str
  domain_name:
    description: The domain name to modify for the IP address.
    required: false
    type: str
  dry_run:
    description:
      - Checks whether you have the required permissions for the action, without actually making the request, and provides an error response.
      - If you have the required permissions, the error response is DryRunOperation. Otherwise, it is UnauthorizedOperation.
    required: false
    type: bool
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.tags
  - amazon.aws.boto3

author:
  - "Rick Mendes (@rickmendes) <rmendes@illumina.com>"
notes:
  - There may be a delay between the time the EIP is assigned and when
    the cloud instance is reachable via the new address. Use wait_for and
    pause to delay further playbook execution until the instance is reachable,
    if necessary.
  - This module returns multiple changed statuses on disassociation or release.
    It returns an overall status based on any changes occurring. It also returns
    individual changed statuses for disassociation and release.
  - Support for O(tags) and O(purge_tags) was added in release 2.1.0.
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: associate an elastic IP with an instance
  amazon.aws.ec2_eip:
    device_id: i-1212f003
    ip: 93.184.216.119

- name: associate an elastic IP with a device
  amazon.aws.ec2_eip:
    device_id: eni-c8ad70f3
    ip: 93.184.216.119

- name: associate an elastic IP with a device and allow reassociation
  amazon.aws.ec2_eip:
    device_id: eni-c8ad70f3
    public_ip: 93.184.216.119
    allow_reassociation: true

- name: disassociate an elastic IP from an instance
  amazon.aws.ec2_eip:
    device_id: i-1212f003
    ip: 93.184.216.119
    state: absent

- name: disassociate an elastic IP with a device
  amazon.aws.ec2_eip:
    device_id: eni-c8ad70f3
    ip: 93.184.216.119
    state: absent

- name: allocate a new elastic IP and associate it with an instance
  amazon.aws.ec2_eip:
    device_id: i-1212f003

- name: allocate a new elastic IP without associating it to anything
  amazon.aws.ec2_eip:
    state: present
  register: eip

- name: output the IP
  ansible.builtin.debug:
    msg: "Allocated IP is {{ eip.public_ip }}"

- name: provision new instances with ec2
  amazon.aws.ec2:
    keypair: mykey
    instance_type: c1.medium
    image: ami-40603AD1
    wait: true
    group: webserver
    count: 3
  register: ec2

- name: associate new elastic IPs with each of the instances
  amazon.aws.ec2_eip:
    device_id: "{{ item }}"
  loop: "{{ ec2.instance_ids }}"

- name: allocate a new elastic IP inside a VPC in us-west-2
  amazon.aws.ec2_eip:
    region: us-west-2
    in_vpc: true
  register: eip

- name: output the IP
  ansible.builtin.debug:
    msg: "Allocated IP inside a VPC is {{ eip.public_ip }}"

- name: allocate eip - reuse unallocated ips (if found) with FREE tag
  amazon.aws.ec2_eip:
    region: us-east-1
    in_vpc: true
    reuse_existing_ip_allowed: true
    tag_name: FREE

- name: allocate eip - reuse unallocated ips if tag reserved is nope
  amazon.aws.ec2_eip:
    region: us-east-1
    in_vpc: true
    reuse_existing_ip_allowed: true
    tag_name: reserved
    tag_value: nope

- name: allocate new eip - from servers given ipv4 pool
  amazon.aws.ec2_eip:
    region: us-east-1
    in_vpc: true
    public_ipv4_pool: ipv4pool-ec2-0588c9b75a25d1a02

- name: allocate eip - from a given pool (if no free addresses where dev-servers tag is dynamic)
  amazon.aws.ec2_eip:
    region: us-east-1
    in_vpc: true
    reuse_existing_ip_allowed: true
    tag_name: dev-servers
    public_ipv4_pool: ipv4pool-ec2-0588c9b75a25d1a02

- name: allocate eip from pool - check if tag reserved_for exists and value is our hostname
  amazon.aws.ec2_eip:
    region: us-east-1
    in_vpc: true
    reuse_existing_ip_allowed: true
    tag_name: reserved_for
    tag_value: "{{ inventory_hostname }}"
    public_ipv4_pool: ipv4pool-ec2-0588c9b75a25d1a02

- name: Modify reverse DNS record of EIP
  amazon.aws.ec2_eip:
    update_reverse_dns: true
    allocation_id: eipalloc-00a61ec1234567890
    domain_name: example.com
"""

RETURN = r"""
allocation_id:
  description: Allocation id of the elastic ip.
  returned: on success
  type: str
  sample: eipalloc-51aa3a6c
public_ip:
  description: An elastic ip address.
  returned: on success
  type: str
  sample: 52.88.159.209
"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AnsibleEC2Error
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import allocate_address as allocate_ip_address
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import associate_address
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_addresses
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_instances
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_network_interfaces
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import disassociate_address
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ensure_ec2_tags
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import release_address
from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_specifications
from ansible_collections.amazon.aws.plugins.module_utils.transformation import ansible_dict_to_boto3_filter_list


def find_address(
    ec2, public_ip: Optional[str], device_id: Optional[str], is_instance
) -> Optional[Dict[str, Union[str, List[Dict[str, str]]]]]:
    """Find an existing Elastic IP address"""
    filters = None

    if not public_ip and not device_id:
        return None

    if public_ip:
        params = {"PublicIps": [public_ip]}
    else:
        if is_instance:
            filters = [{"Name": "instance-id", "Values": [device_id]}]
        else:
            filters = [{"Name": "network-interface-id", "Values": [device_id]}]
        params = {"Filters": filters}

    result = None
    addresses = describe_addresses(ec2, **params)
    if addresses:
        if len(addresses) > 1:
            raise AnsibleEC2Error(f"Found more than one address using args {params} Addresses found: {addresses}")
        result = addresses[0]
    return result


def address_is_associated_with_device(
    ec2,
    address: Optional[Dict[str, str]],
    device_id: str,
    is_instance: bool = True,
) -> Optional[str]:
    """Check if the elastic IP is currently associated with the device and return the association Id"""
    public_ip = None if not address else address.get("PublicIp")
    result = find_address(ec2, public_ip, device_id, is_instance)
    association_id = None
    if result:
        instance_id = result.get("InstanceId") if is_instance else result.get("NetworkInterfaceId")
        if instance_id == device_id:
            association_id = result.get("AssociationId")
    return association_id


def allocate_address(
    client,
    check_mode: bool,
    search_tags: Optional[Dict[str, str]],
    domain: Optional[str],
    reuse_existing_ip_allowed: bool,
    tags: Optional[Dict[str, str]],
    public_ipv4_pool: Optional[bool] = None,
) -> Tuple[Dict[str, str], bool]:
    """Allocate a new elastic IP address (when needed) and return it"""
    if not domain:
        domain = "standard"

    if reuse_existing_ip_allowed:
        filters = []
        filters.append({"Name": "domain", "Values": [domain]})

        if search_tags is not None:
            filters += ansible_dict_to_boto3_filter_list(search_tags)

        all_addresses = describe_addresses(client, Filters=filters)

        if domain == "vpc":
            unassociated_addresses = [a for a in all_addresses if not a.get("AssociationId", None)]
        else:
            unassociated_addresses = [a for a in all_addresses if not a["InstanceId"]]
        if unassociated_addresses:
            return unassociated_addresses[0], False

    params = {"Domain": domain}
    if public_ipv4_pool:
        params.update({"PublicIpv4Pool": public_ipv4_pool})
    if tags:
        params["TagSpecifications"] = boto3_tag_specifications(tags, types="elastic-ip")
    address = None
    if not check_mode:
        address = allocate_ip_address(client, **params)
    return address, True


def find_device(client, device_id: str, is_instance: bool) -> Optional[Dict[str, Any]]:
    """Attempt to find the EC2 instance and return it"""

    result = None
    if is_instance:
        reservations = describe_instances(client, InstanceIds=[device_id])
        if len(reservations) == 1:
            instances = reservations[0]["Instances"]
            if len(instances) == 1:
                result = instances[0]
    else:
        interfaces = describe_network_interfaces(client, NetworkInterfaceIds=[device_id])
        if len(interfaces) == 1:
            result = interfaces[0]
    return result


def generate_tag_dict(module: AnsibleAWSModule) -> Optional[Dict[str, str]]:
    """Generates a dictionary to be passed as a filter to Amazon"""
    tag_name = module.params.get("tag_name")
    tag_value = module.params.get("tag_value")
    result = None

    if not tag_name:
        return result

    if not tag_value:
        if tag_name.startswith("tag:"):
            tag_name = tag_name.strip("tag:")
        result = {"tag-key": tag_name}
    else:
        if not tag_name.startswith("tag:"):
            tag_name = "tag:" + tag_name
        result = {tag_name: tag_value}

    return result


def check_is_instance(module: AnsibleAWSModule) -> bool:
    device_id = module.params.get("device_id")
    in_vpc = module.params.get("in_vpc")
    if not device_id:
        return False
    if device_id.startswith("i-"):
        return True

    if device_id.startswith("eni-") and not in_vpc:
        raise module.fail_json("If you are specifying an ENI, in_vpc must be true")
    return False


def ensure_absent(
    client: Any, module: AnsibleAWSModule, address: Optional[Dict[str, Any]], is_instance: bool
) -> Dict[str, bool]:
    disassociated = False
    released = False

    device_id = module.params.get("device_id")
    release_on_disassociation = module.params.get("release_on_disassociation")

    if address:
        if device_id:
            # disassociating address from instance
            association_id = address_is_associated_with_device(client, address, device_id, is_instance)
            if association_id:
                disassociated = True
                if not module.check_mode:
                    disassociated = disassociate_address(client, association_id=association_id)

        if not device_id or (disassociated and release_on_disassociation):
            # Release or Release on disassociation
            released = True
            if not module.check_mode:
                released = release_address(client, allocation_id=address["AllocationId"])
    return {"changed": disassociated or released, "disassociated": disassociated, "released": released}


def ensure_present(
    client, module: AnsibleAWSModule, address: Optional[Dict[str, Any]], is_instance: bool
) -> Dict[str, Any]:
    device_id = module.params.get("device_id")
    private_ip_address = module.params.get("private_ip_address")
    in_vpc = module.params.get("in_vpc")
    domain = "vpc" if in_vpc else None
    reuse_existing_ip_allowed = module.params.get("reuse_existing_ip_allowed")
    allow_reassociation = module.params.get("allow_reassociation")
    public_ipv4_pool = module.params.get("public_ipv4_pool")
    tags = module.params.get("tags")
    purge_tags = module.params.get("purge_tags")

    # Tags for *searching* for an EIP.
    search_tags = generate_tag_dict(module)
    result = {}
    changed = False

    # Allocate address
    if not address:
        address, changed = allocate_address(
            client, module.check_mode, search_tags, domain, reuse_existing_ip_allowed, tags, public_ipv4_pool
        )

    # Associate address to instance
    if device_id:
        # Find instance
        instance = find_device(client, device_id, is_instance)
        # Allocate an IP for instance since no public_ip was provided
        if is_instance and reuse_existing_ip_allowed:
            if instance["VpcId"] and len(instance["VpcId"]) > 0 and domain is None:
                raise AnsibleEC2Error(
                    "You must set 'in_vpc' to true to associate an instance with an existing ip in a vpc"
                )

        # check if the address is already associated to the device
        association_id = address_is_associated_with_device(client, address, device_id, is_instance)
        if not association_id:
            changed = True
            if not module.check_mode:
                # Associate address object (provided or allocated) with instance
                if is_instance:
                    params = {"InstanceId": device_id, "AllowReassociation": allow_reassociation}
                    if address.get("Domain") == "vpc":
                        params["AllocationId"] = address.get("AllocationId")
                    else:
                        params["PublicIp"] = address.get("PublicIp")
                else:
                    params = {
                        "NetworkInterfaceId": device_id,
                        "AllocationId": address.get("AllocationId"),
                        "AllowReassociation": allow_reassociation,
                    }

                if private_ip_address:
                    params["PrivateIpAddress"] = private_ip_address
                associate_address(client, **params)

    # Ensure tags
    if address:
        changed |= ensure_ec2_tags(
            client, module, address["AllocationId"], resource_type="elastic-ip", tags=tags, purge_tags=purge_tags
        )
        result.update({"public_ip": address["PublicIp"], "allocation_id": address["AllocationId"]})
    result["changed"] = changed
    return result


def  update_reverse_dns_record_of_eip(client, module: AnsibleAWSModule):
    changed = False
    allocation_id = module.params.get("allocation_id")
    domain_name = module.params.get("domain_name")
    dry_run = module.params.get("dry_run")

    try:
        update_reverse_dns_record_result = client.modify_address_attribute(AllocationId=allocation_id, DomainName=domain_name, DryRun=dry_run)
        changed = True
    except AnsibleEC2Error as e:
        module.fail_json_aws_error(e)

    if "ResponseMetadata" in update_reverse_dns_record_result:
        del update_reverse_dns_record_result["ResponseMetadata"]

    return {"changed": changed, "update_reverse_dns_record_result": camel_dict_to_snake_dict(update_reverse_dns_record_result)}


def main():
    argument_spec = dict(
        allocation_id=dict(required=False, type="str"),
        device_id=dict(required=False),
        domain_name=dict(required=False, type="str"),
        dry_run=dict(default=False, type="bool"),
        public_ip=dict(required=False, aliases=["ip"]),
        state=dict(required=False, default="present", choices=["present", "absent"]),
        in_vpc=dict(required=False, type="bool", default=False),
        reuse_existing_ip_allowed=dict(required=False, type="bool", default=False),
        release_on_disassociation=dict(required=False, type="bool", default=False),
        allow_reassociation=dict(type="bool", default=False),
        private_ip_address=dict(),
        tags=dict(required=False, type="dict", aliases=["resource_tags"]),
        purge_tags=dict(required=False, type="bool", default=True),
        tag_name=dict(),
        tag_value=dict(),
        update_reverse_dns_record=dict(required=False, type="bool"),
        public_ipv4_pool=dict(),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_by={
            "private_ip_address": ["device_id"],
            "tag_value": ["tag_name"],
        },
        required_if=[
          ('update_reverse_dns_record', True, ('allocation_id', 'domain_name')),
        ],
    )

    ec2 = module.client("ec2")

    device_id = module.params.get("device_id")
    public_ip = module.params.get("public_ip")
    state = module.params.get("state")

    is_instance = check_is_instance(module)

    if module.params.get("update_reverse_dns_record") == True:
        result = update_reverse_dns_record_of_eip(ec2, module)
    else:
      try:
          # Find existing address
          address = find_address(ec2, public_ip, device_id, is_instance)
          if state == "present":
              result = ensure_present(ec2, module, address, is_instance)
          else:
              result = ensure_absent(ec2, module, address, is_instance)

      except AnsibleEC2Error as e:
          module.fail_json_aws_error(e)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
