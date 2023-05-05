# -*- coding: utf-8 -*-

# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


try:
    import botocore
except ImportError:
    pass  # Handled by HAS_BOTO3

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict


def get_backup_resource_tags(module, backup_client):
    resource = module.params.get("resource")
    try:
        response = backup_client.list_tags(ResourceArn=resource)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to list tags on the resource f{resource}")

    return response["Tags"]


def _list_backup_plans(client, backup_plan_name):
    first_iteration = False
    next_token = None

    # We can not use the paginator at the moment because if was introduced after boto3 version 1.22
    # paginator = client.get_paginator("list_backup_plans")
    # result = paginator.paginate(**params).build_full_result()["BackupPlansList"]

    response = client.list_backup_plans()
    next_token = response.get("NextToken", None)

    if next_token is None:
        entries = response["BackupPlansList"]
        for backup_plan in entries:
            if backup_plan_name == backup_plan["BackupPlanName"]:
                return backup_plan["BackupPlanId"]

    while next_token is not None:
        if first_iteration != False:
            response = client.list_backup_plans(NextToken=next_token)
        first_iteration = True
        entries = response["BackupPlansList"]
        for backup_plan in entries:
            if backup_plan_name == backup_plan["BackupPlanName"]:
                return backup_plan["BackupPlanId"]
        try:
            next_token = response.get('NextToken')
        except:
            next_token = None


def get_plan_details(module, client, backup_plan_name: str):
    backup_plan_id = _list_backup_plans(client, backup_plan_name)

    if not backup_plan_id:
        return []

    try:
        _result = client.get_backup_plan(BackupPlanId=backup_plan_id)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to describe plan {backup_plan_id}")

    try:
       module.params["resource"] = _result.get("BackupPlanArn", None)
       tag_dict = get_backup_resource_tags(module, client)
       _result.update({"tags": tag_dict})
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
     module.fail_json_aws(e, msg=f"Failed to get the backup plan tags")

    # Turn the boto3 result in to ansible friendly tag dictionary
    result = [_result]
    for v in result:
        if "TagsList" in v:
            v["Tags"] = boto3_tag_list_to_ansible_dict(v["TagsList"], "key", "value")
            del v["TagsList"]
        if "ResponseMetadata" in v:
            del v["ResponseMetadata"]
        v["BackupPlanName"] = v["BackupPlan"]["BackupPlanName"]

    return result
