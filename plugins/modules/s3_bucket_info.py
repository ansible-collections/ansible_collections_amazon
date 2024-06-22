#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket_info
version_added: 1.0.0
version_added_collection: community.aws
author:
  - "Gerben Geijteman (@hyperized)"
short_description: Lists S3 buckets in AWS
description:
  - Lists S3 buckets and details about those buckets.
  - Prior to release 5.0.0 this module was called C(community.aws.aws_s3_bucket_info).
    The usage did not change.
options:
  name:
    description:
      - Name of bucket to query.
    type: str
    default: ""
    version_added: 1.4.0
  name_filter:
    description:
      - Limits buckets to only buckets who's name contain the string in I(name_filter).
    type: str
    default: ""
    version_added: 1.4.0
  bucket_facts:
    description:
      - Retrieve requested S3 bucket detailed information.
      - Each bucket_X option executes one API call, hence many options being set to C(true) will cause slower module execution.
      - You can limit buckets by using the I(name) or I(name_filter) option.
    suboptions:
      bucket_accelerate_configuration:
        description: Retrieve S3 accelerate configuration.
        type: bool
        default: False
      bucket_location:
        description: Retrieve S3 bucket location.
        type: bool
        default: False
      bucket_replication:
        description: Retrieve S3 bucket replication.
        type: bool
        default: False
      bucket_acl:
        description: Retrieve S3 bucket ACLs.
        type: bool
        default: False
      bucket_logging:
        description: Retrieve S3 bucket logging.
        type: bool
        default: False
      bucket_request_payment:
        description: Retrieve S3 bucket request payment.
        type: bool
        default: False
      bucket_tagging:
        description: Retrieve S3 bucket tagging.
        type: bool
        default: False
      bucket_cors:
        description: Retrieve S3 bucket CORS configuration.
        type: bool
        default: False
      bucket_notification_configuration:
        description: Retrieve S3 bucket notification configuration.
        type: bool
        default: False
      bucket_encryption:
        description: Retrieve S3 bucket encryption.
        type: bool
        default: False
      bucket_ownership_controls:
        description:
        - Retrieve S3 ownership controls.
        type: bool
        default: False
      bucket_website:
        description: Retrieve S3 bucket website.
        type: bool
        default: False
      bucket_policy:
        description: Retrieve S3 bucket policy.
        type: bool
        default: False
      bucket_policy_status:
        description: Retrieve S3 bucket policy status.
        type: bool
        default: False
      bucket_lifecycle_configuration:
        description: Retrieve S3 bucket lifecycle configuration.
        type: bool
        default: False
      public_access_block:
        description: Retrieve S3 bucket public access block.
        type: bool
        default: False
      bucket_versioning:
        description:
          - Retrieve the versioning state of a bucket.
          - To retrieve the versioning state of a bucket, you must be the bucket owner.
        type: bool
        default: False
        version_added: 7.3.0
    type: dict
    version_added: 1.4.0
  transform_location:
    description:
      - S3 bucket location for default us-east-1 is normally reported as C(null).
      - Setting this option to C(true) will return C(us-east-1) instead.
      - Affects only queries with I(bucket_facts=true) and I(bucket_location=true).
    type: bool
    default: False
    version_added: 1.4.0
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Note: Only AWS S3 is currently supported

# Lists all S3 buckets
- amazon.aws.s3_bucket_info:
  register: result

# Retrieve detailed bucket information
- amazon.aws.s3_bucket_info:
    # Show only buckets with name matching
    name_filter: your.testing
    # Choose facts to retrieve
    bucket_facts:
      # bucket_accelerate_configuration: true
      bucket_acl: true
      bucket_cors: true
      bucket_encryption: true
      # bucket_lifecycle_configuration: true
      bucket_location: true
      # bucket_logging: true
      # bucket_notification_configuration: true
      # bucket_ownership_controls: true
      # bucket_policy: true
      # bucket_policy_status: true
      # bucket_replication: true
      # bucket_request_payment: true
      # bucket_tagging: true
      # bucket_website: true
      # public_access_block: true
    transform_location: true
    register: result

# Print out result
- name: List buckets
  ansible.builtin.debug:
    msg: "{{ result['buckets'] }}"
"""

RETURN = r"""
buckets:
  description: A list of S3 buckets.
  returned: always
  type: complex
  contains:
    bucket_accelerate_configuration:
      description: The accelerate configuration of the bucket.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_accelerate_configuration=true).
      type: dict
      sample: {
                'Status': 'Enabled',
                'RequestCharged': 'requester'
              }
    name:
      description: Bucket name.
      returned: always
      type: str
      sample: "a-testing-bucket-name"
    creation_date:
      description: Bucket creation date timestamp.
      returned: always
      type: str
      sample: "2021-01-21T12:44:10+00:00"
    public_access_block:
      description: Bucket public access block configuration.
      returned: when O(bucket_facts=true) and  RV(buckets.public_access_block=true)
      type: dict
      sample: {
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": true,
                    "BlockPublicPolicy": true,
                    "IgnorePublicAcls": true,
                    "RestrictPublicBuckets": true
                }
              }
      contains:
        PublicAccessBlockConfiguration:
          description: PublicAccessBlockConfiguration data.
          returned: when PublicAccessBlockConfiguration is defined for the bucket
          type: complex
          contains:
            BlockPublicAcls:
              description: BlockPublicAcls setting value.
              type: bool
            BlockPublicPolicy:
              description: BlockPublicPolicy setting value.
              type: bool
            IgnorePublicAcls:
              description: IgnorePublicAcls setting value.
              type: bool
            RestrictPublicBuckets:
              description: RestrictPublicBuckets setting value.
              type: bool
    bucket_name_filter:
      description: String used to limit buckets. See I(name_filter).
      returned: when O(name_filter) is defined
      type: str
      sample: "filter-by-this-string"
    bucket_acl:
      description: Bucket ACL configuration.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_acl=true).
      type: complex
      contains:
        Grants:
          description: List of ACL grants.
          type: list
          elements: dict
          sample: [
                    {
                        "Grantee": {
                            "DisplayName": "abc-aws-root+721234567890",
                            "ID": "1234567890cbc0f1234567890f1234567890c123456789012123456789091234",
                            "Type": "CanonicalUser"
                        },
                        "Permission": "FULL_CONTROL"
                    }
                  ]
          contains:
            Grantee:
              description: The person being granted permissions.
              type: dict
              contains:
                DisplayName:
                  description: Screen name of the grantee.
                  type: str
                ID:
                  description: The canonical user ID of the grantee.
                  type: str
                Type:
                  description: Type of grantee.
                  type: str
            Permission:
              description: Specifies the permission given to the grantee.
              type: str
        Owner:
          description: Bucket owner information.
          type: dict
          sample: {
                    "DisplayName": "abc-aws-root+721234567890",
                    "ID": "1234567890cbc0f1234567890f1234567890c123456789012123456789091234"
                  }
          contains:
            DisplayName:
              description: Bucket owner user display name.
              type: str
            ID:
              description: Bucket owner user ID.
              type: str
    bucket_cors:
      description: Bucket CORS configuration.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_cors=true)
      type: complex
      contains:
        CORSRules:
          description: Bucket CORS configuration.
          returned: When CORS rules are defined for the bucket
          type: list
          sample: []
    bucket_encryption:
      description: Bucket encryption configuration.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_encryption=true).
      type: complex
      sample: {
                "ServerSideEncryptionConfiguration": {
                    "Rules": [
                        {
                          "ApplyServerSideEncryptionByDefault": {
                              "SSEAlgorithm": "AES256"
                          },
                          "BucketKeyEnabled": true
                        }
                    ]
                  }
                }
      contains:
        ServerSideEncryptionConfiguration:
          description: ServerSideEncryptionConfiguration configuration.
          returned: when encryption is enabled on the bucket.
          type: complex
          contains:
            Rules:
              description: List of applied encryptio rules.
              returned: when encryption is enabled on the bucket.
              type: list
              elements: dict
              contains:
                ApplyServerSideEncryptionByDefault:
                  description: Specifies the default server-side encryption to apply to new objects in the bucket.
                  type: dict
                  contains:
                    SSEAlgorithm:
                      description: Server-side encryption algorithm to use for the default encryption.
                      type: str
                    KMSMasterKeyID:
                      description: Amazon Web Services Key Management Service (KMS) customer Amazon Web Services KMS key ID to use for the default encryption.
                      type: str
                BucketKeyEnabled:
                  description:
                    - Specifies whether Amazon S3 should use an S3 Bucket Key with server-side encryption using KMS (SSE-KMS) for new objects in the bucket.
                  type: bool
    bucket_lifecycle_configuration:
      description: Bucket lifecycle configuration settings.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_lifecycle_configuration=true).
      type: list
      elements: dict
      contains:
        Rules:
          description: List of lifecycle management rules.
          returned: when lifecycle configuration is present.
          type: list
          sample: [
                    {
                      "Status": "Enabled",
                      "ID": "example-rule"
                    }
                  ]
    bucket_location:
      description: Bucket location.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_location=true).
      type: dict
      sample: {
                "LocationConstraint": "us-east-1"
              }
      contains:
        LocationConstraint:
          description: AWS region.
          returned: always
          type: str
    bucket_logging:
      description: Server access logging configuration.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_logging=true).
      type: complex
      contains:
        LoggingEnabled:
          description: Server access logging configuration.
          returned: when server access logging is defined for the bucket.
          type: complex
          contains:
            TargetBucket:
              description: Target bucket name.
              returned: always
              type: str
              sample: "logging-bucket-name"
            TargetPrefix:
              description: Prefix in target bucket.
              returned: always
              type: str
              sample: ""
    bucket_notification_configuration:
      description: Bucket notification settings.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_notification_configuration=true).
      type: complex
      contains:
        TopicConfigurations:
          description: List of notification events configurations.
          returned: when at least one notification is configured.
          type: list
          sample: [
                      {
                          'Id': 'topic-config-dev001',
                          'TopicArn': 'arn:aws:sns:us-west-1:721234567890:sns-dev001-topic',
                          'Events': [
                              "s3:ObjectCreated:Copy"
                          ],
                          'Filter': {
                              'Key': {
                                  'FilterRules': [
                                      {
                                            "Name": "Prefix",
                                            "Value": "test/"
                                      },
                                  ]
                              }
                          }
                      },
                    ]
    bucket_ownership_controls:
      description: Preffered object ownership settings.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_ownership_controls=true)
      type: complex
      sample: {
                "OwnershipControls": {
                  "Rules": [
                      {
                        "ObjectOwnership": "BucketOwnerEnforced"
                      }
                  ]
                }
              }
      contains:
        OwnershipControls:
          description: Object ownership settings.
          returned: when ownership controls are defined for the bucket.
          type: complex
          contains:
            Rules:
              description: List of ownership rules.
              returned: when ownership rule is defined.
              type: list
    bucket_policy:
      description: Bucket policy contents.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_policy=true).
      type: str
      sample: '{"Version":"2012-10-17","Statement":[{"Sid":"AddCannedAcl","Effect":"Allow",..}}]}'
    bucket_policy_status:
      description: Status of bucket policy.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_policy_status=true).
      type: dict
      contains:
        PolicyStatus:
          description: Status of bucket policy.
          returned: when bucket policy is present.
          type: dict
          contains:
            IsPublic:
              description: Report bucket policy public status.
              returned: when bucket policy is present.
              type: bool
              sample: True
    bucket_replication:
      description: Replication configuration settings.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_replication=true).
      type: complex
      contains:
        Role:
          description: IAM role used for replication.
          returned: when replication rule is defined.
          type: str
          sample: "arn:aws:iam::123:role/example-role"
        Rules:
          description: List of replication rules.
          returned: when replication rule is defined/
          type: list
          sample: [{ "ID": "rule-1", "Filter": "{}" }]
    bucket_request_payment:
      description: Requester pays setting.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_request_payment=true)
      type: complex
      sample: {
                "Payer": "BucketOwner"
              }
      contains:
        Payer:
          description: Current payer.
          returned: always
          type: str
    bucket_tagging:
      description: Bucket tags.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_tagging=true).
      type: dict
      sample: { "Tag1": "Value1", "Tag2": "Value2" }
    bucket_website:
      description: Static website hosting.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_website=true).
      type: complex
      contains:
        ErrorDocument:
          description: Object serving as HTTP error page.
          returned: when static website hosting is enabled.
          type: dict
          sample: { "Key": "error.html" }
        IndexDocument:
          description: Object serving as HTTP index page.
          returned: when static website hosting is enabled.
          type: dict
          sample: { "Suffix": "error.html" }
        RedirectAllRequestsTo:
          description: Website redict settings.
          returned: when redirect requests is configured.
          type: complex
          contains:
            HostName:
              description: Hostname to redirect.
              returned: always
              type: str
              sample: "www.example.com"
            Protocol:
              description: Protocol used for redirect.
              returned: always
              type: str
              sample: "https"
    bucket_versioning:
      description:
        - The versioning state of the bucket.
        - This will also specify whether MFA delete is enabled in the bucket versioning configuration.
          if only the bucket has been configured with MFA delete.
      returned: when O(bucket_facts=true) and RV(buckets.bucket_versioning=true).
      type: dict
      sample: { "Status": "Enabled" }
      version_added: 7.2.0
"""

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict


def get_bucket_list(module, connection, name="", name_filter=""):
    """
    Return result of list_buckets json encoded
    Filter only buckets matching 'name' or name_filter if defined
    :param module:
    :param connection:
    :return:
    """
    buckets = []
    filtered_buckets = []
    final_buckets = []

    # Get all buckets
    try:
        buckets = camel_dict_to_snake_dict(connection.list_buckets())["buckets"]
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as err_code:
        module.fail_json_aws(err_code, msg="Failed to list buckets")

    # Filter buckets if requested
    if name_filter:
        for bucket in buckets:
            if name_filter in bucket["name"]:
                filtered_buckets.append(bucket)
    elif name:
        for bucket in buckets:
            if name == bucket["name"]:
                filtered_buckets.append(bucket)

    # Return proper list (filtered or all)
    if name or name_filter:
        final_buckets = filtered_buckets
    else:
        final_buckets = buckets
    return final_buckets


def get_buckets_facts(connection, buckets, requested_facts, transform_location):
    """
    Retrieve additional information about S3 buckets
    """
    full_bucket_list = []
    # Iterate over all buckets and append Retrieved facts to bucket
    for bucket in buckets:
        bucket.update(get_bucket_details(connection, bucket["name"], requested_facts, transform_location))
        full_bucket_list.append(bucket)

    return full_bucket_list


def get_bucket_details(connection, name, requested_facts, transform_location):
    """
    Execute all enabled S3API get calls for selected bucket
    """
    all_facts = {}

    for key in requested_facts:
        if requested_facts[key]:
            if key == "bucket_location":
                all_facts[key] = {}
                try:
                    all_facts[key] = get_bucket_location(name, connection, transform_location)
                # we just pass on error - error means that resources is undefined
                except botocore.exceptions.ClientError:
                    pass
            elif key == "bucket_tagging":
                all_facts[key] = {}
                try:
                    all_facts[key] = get_bucket_tagging(name, connection)
                # we just pass on error - error means that resources is undefined
                except botocore.exceptions.ClientError:
                    pass
            else:
                all_facts[key] = {}
                try:
                    all_facts[key] = get_bucket_property(name, connection, key)
                # we just pass on error - error means that resources is undefined
                except botocore.exceptions.ClientError:
                    pass

    return all_facts


@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["NoSuchBucket", "OperationAborted"])
def get_bucket_location(name, connection, transform_location=False):
    """
    Get bucket location and optionally transform 'null' to 'us-east-1'
    """
    data = connection.get_bucket_location(Bucket=name)

    # Replace 'null' with 'us-east-1'?
    if transform_location:
        try:
            if not data["LocationConstraint"]:
                data["LocationConstraint"] = "us-east-1"
        except KeyError:
            pass
    # Strip response metadata (not needed)
    data.pop("ResponseMetadata", None)
    return data


@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["NoSuchBucket", "OperationAborted"])
def get_bucket_tagging(name, connection):
    """
    Get bucket tags and transform them using `boto3_tag_list_to_ansible_dict` function
    """
    data = connection.get_bucket_tagging(Bucket=name)

    try:
        bucket_tags = boto3_tag_list_to_ansible_dict(data["TagSet"])
        return bucket_tags
    except KeyError:
        # Strip response metadata (not needed)
        data.pop("ResponseMetadata", None)
        return data


@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["NoSuchBucket", "OperationAborted"])
def get_bucket_property(name, connection, get_api_name):
    """
    Get bucket property
    """
    api_call = "get_" + get_api_name
    api_function = getattr(connection, api_call)
    data = api_function(Bucket=name)

    # Strip response metadata (not needed)
    data.pop("ResponseMetadata", None)
    return data


def main():
    """
    Get list of S3 buckets
    :return:
    """
    argument_spec = dict(
        name=dict(type="str", default=""),
        name_filter=dict(type="str", default=""),
        bucket_facts=dict(
            type="dict",
            options=dict(
                bucket_accelerate_configuration=dict(type="bool", default=False),
                bucket_acl=dict(type="bool", default=False),
                bucket_cors=dict(type="bool", default=False),
                bucket_encryption=dict(type="bool", default=False),
                bucket_lifecycle_configuration=dict(type="bool", default=False),
                bucket_location=dict(type="bool", default=False),
                bucket_logging=dict(type="bool", default=False),
                bucket_notification_configuration=dict(type="bool", default=False),
                bucket_ownership_controls=dict(type="bool", default=False),
                bucket_policy=dict(type="bool", default=False),
                bucket_policy_status=dict(type="bool", default=False),
                bucket_replication=dict(type="bool", default=False),
                bucket_request_payment=dict(type="bool", default=False),
                bucket_tagging=dict(type="bool", default=False),
                bucket_website=dict(type="bool", default=False),
                public_access_block=dict(type="bool", default=False),
                bucket_versioning=dict(type="bool", default=False),
            ),
        ),
        transform_location=dict(type="bool", default=False),
    )

    # Ensure we have an empty dict
    result = {}

    # Define mutually exclusive options
    mutually_exclusive = [
        ["name", "name_filter"],
    ]

    # Including ec2 argument spec
    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=mutually_exclusive,
    )

    # Get parameters
    name = module.params.get("name")
    name_filter = module.params.get("name_filter")
    requested_facts = module.params.get("bucket_facts")
    transform_location = module.params.get("bucket_facts")

    # Set up connection
    connection = {}
    try:
        connection = module.client("s3")
    except (connection.exceptions.ClientError, botocore.exceptions.BotoCoreError) as err_code:
        module.fail_json_aws(err_code, msg="Failed to connect to AWS")

    # Get basic bucket list (name + creation date)
    bucket_list = get_bucket_list(module, connection, name, name_filter)

    # Add information about name/name_filter to result
    if name:
        result["bucket_name"] = name
    elif name_filter:
        result["bucket_name_filter"] = name_filter

    # Gather detailed information about buckets if requested
    bucket_facts = module.params.get("bucket_facts")
    if bucket_facts:
        result["buckets"] = get_buckets_facts(connection, bucket_list, requested_facts, transform_location)
    else:
        result["buckets"] = bucket_list

    module.exit_json(msg="Retrieved s3 info.", **result)


# MAIN
if __name__ == "__main__":
    main()
