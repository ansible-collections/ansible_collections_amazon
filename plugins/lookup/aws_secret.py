# Copyright: (c) 2018, Aaron Smith <ajsmith10381@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
lookup: aws_secret
author:
  - Aaron Smith <ajsmith10381@gmail.com>
requirements:
  - boto3
  - botocore>=1.10.0
extends_documentation_fragment:
- amazon.aws.aws_credentials
- amazon.aws.aws_region

short_description: Look up secrets stored in AWS Secrets Manager.
description:
  - Look up secrets stored in AWS Secrets Manager provided the caller
    has the appropriate permissions to read the secret.
  - Lookup is based on the secret's `Name` value.
  - Optional parameters can be passed into this lookup; `version_id` and `version_stage`
options:
  _terms:
    description: Name of the secret to look up in AWS Secrets Manager.
    required: True
  bypath:
    description: A boolean to indicate whether the parameter is provided as a hierarchy.
    default: false
    type: boolean
  version_id:
    description: Version of the secret(s).
    required: False
  version_stage:
    description: Stage of the secret version.
    required: False
  join:
    description:
        - Join two or more entries to form an extended secret.
        - This is useful for overcoming the 4096 character limit imposed by AWS.
        - No effect when used with `bypath`
    type: boolean
    default: false
  on_missing:
    description:
        - Action to take if the secret is missing.
        - C(error) will raise a fatal error when the secret is missing.
        - C(skip) will silently ignore the missing secret.
        - C(warn) will skip over the missing secret but issue a warning.
    default: error
    type: string
    choices: ['error', 'skip', 'warn']
  on_denied:
    description:
        - Action to take if access to the secret is denied.
        - C(error) will raise a fatal error when access to the secret is denied.
        - C(skip) will silently ignore the denied secret.
        - C(warn) will skip over the denied secret but issue a warning.
    default: error
    type: string
    choices: ['error', 'skip', 'warn']
'''

EXAMPLES = r"""
 - name: lookup secretsmanager secret in the current region
   debug: msg="{{ lookup('aws_secret', '/path/to/secrets', bypath=true) }}"

 - name: Create RDS instance with aws_secret lookup for password param
   rds:
     command: create
     instance_name: app-db
     db_engine: MySQL
     size: 10
     instance_type: db.m1.small
     username: dbadmin
     password: "{{ lookup('aws_secret', 'DbSecret') }}"
     tags:
       Environment: staging

 - name: skip if secret does not exist
   debug: msg="{{ lookup('aws_secret', 'secret-not-exist', on_missing='skip')}}"

 - name: warn if access to the secret is denied
   debug: msg="{{ lookup('aws_secret', 'secret-denied', on_denied='warn')}}"
"""

RETURN = r"""
_raw:
  description:
    Returns the value of the secret stored in AWS Secrets Manager.
"""

from ansible.errors import AnsibleError
from ansible.module_utils.six import string_types

try:
    import boto3
    import botocore
except ImportError:
    raise AnsibleError("The lookup aws_secret requires boto3 and botocore.")

from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_native
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code

from ..module_utils.ec2 import HAS_BOTO3


def _boto3_conn(region, credentials):
    boto_profile = credentials.pop('aws_profile', None)

    try:
        connection = boto3.session.Session(profile_name=boto_profile).client('secretsmanager', region, **credentials)
    except (botocore.exceptions.ProfileNotFound, botocore.exceptions.PartialCredentialsError) as e:
        if boto_profile:
            try:
                connection = boto3.session.Session(profile_name=boto_profile).client('secretsmanager', region)
            except (botocore.exceptions.ProfileNotFound, botocore.exceptions.PartialCredentialsError) as e:
                raise AnsibleError("Insufficient credentials found.")
        else:
            raise AnsibleError("Insufficient credentials found.")
    return connection


class LookupModule(LookupBase):
    def run(self, terms, variables=None, boto_profile=None, aws_profile=None,
            aws_secret_key=None, aws_access_key=None, aws_security_token=None, region=None,
            bypath=False, join=False, version_stage=None, version_id=None, on_missing=None,
            on_denied=None):
        '''
                   :arg terms: a list of lookups to run.
                       e.g. ['parameter_name', 'parameter_name_too' ]
                   :kwarg variables: ansible variables active at the time of the lookup
                   :kwarg aws_secret_key: identity of the AWS key to use
                   :kwarg aws_access_key: AWS secret key (matching identity)
                   :kwarg aws_security_token: AWS session key if using STS
                   :kwarg decrypt: Set to True to get decrypted parameters
                   :kwarg region: AWS region in which to do the lookup
                   :kwarg bypath: Set to True to do a lookup of variables under a path
                   :kwarg join: Join two or more entries to form an extended secret
                   :kwarg version_stage: Stage of the secret version
                   :kwarg version_id: Version of the secret(s)
                   :kwarg on_missing: Action to take if the secret is missing
                   :kwarg on_denied: Action to take if access to the secret is denied
                   :returns: A list of parameter values or a list of dictionaries if bypath=True.
               '''
        if not HAS_BOTO3:
            raise AnsibleError('botocore and boto3 are required for aws_ssm lookup.')

        missing = kwargs.get('on_missing', 'error').lower()
        if not isinstance(missing, string_types) or missing not in ['error', 'warn', 'skip']:
            raise AnsibleError('"on_missing" must be a string and one of "error", "warn" or "skip", not %s' % missing)

        denied = kwargs.get('on_denied', 'error').lower()
        if not isinstance(denied, string_types) or denied not in ['error', 'warn', 'skip']:
            raise AnsibleError('"on_denied" must be a string and one of "error", "warn" or "skip", not %s' % denied)

        credentials = {}
        if aws_profile:
            credentials['aws_profile'] = aws_profile
        else:
            credentials['aws_profile'] = boto_profile
        credentials['aws_secret_access_key'] = aws_secret_key
        credentials['aws_access_key_id'] = aws_access_key
        credentials['aws_session_token'] = aws_security_token

        # fallback to IAM role credentials
        if not credentials['aws_profile'] and not (
                credentials['aws_access_key_id'] and credentials['aws_secret_access_key']):
            session = botocore.session.get_session()
            if session.get_credentials() is not None:
                credentials['aws_access_key_id'] = session.get_credentials().access_key
                credentials['aws_secret_access_key'] = session.get_credentials().secret_key
                credentials['aws_session_token'] = session.get_credentials().token

        client = _boto3_conn(region, credentials)

        if bypath:
            secrets = {}
            for term in terms:
                try:
                    response = client.list_secrets(Filters=[{'Key': 'name', 'Values': [term]}])

                    if 'SecretList' in response:
                        for secret in response['SecretList']:
                            secrets.update({secret['Name']: self.get_secret_value(secret['Name'], client,
                                                                                  on_missing=on_missing,
                                                                                  on_denied=on_denied)})
                except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                    raise AnsibleError("Failed to retrieve secret: %s" % to_native(e))
            secrets = [secrets]
        else:
            secrets = []
            for term in terms:
                value = self.get_secret_value(term, client,
                                              version_stage=version_stage, version_id=version_id,
                                              on_missing=on_missing, on_denied=on_denied)
                if value:
                    secrets.append(value)
            if join:
                joined_secret = []
                joined_secret.append(''.join(secrets))
                return joined_secret

        return secrets

    def get_secret_value(self, term, client, version_stage=None, version_id=None, on_missing=None, on_denied=None):
        params = {}
        params['SecretId'] = term
        if version_id:
            params['VersionId'] = version_id
        if version_stage:
            params['VersionStage'] = version_stage

        try:
            response = client.get_secret_value(**params)
            if 'SecretBinary' in response:
                return response['SecretBinary']
            if 'SecretString' in response:
                return response['SecretString']
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            raise AnsibleError("Failed to retrieve secret: %s" % to_native(e))
            try:
                response = client.get_secret_value(**params)
                if 'SecretBinary' in response:
                    secrets.append(response['SecretBinary'])
                if 'SecretString' in response:
                    secrets.append(response['SecretString'])
            except is_boto3_error_code('ResourceNotFoundException'):
                if missing == 'error':
                    raise AnsibleError("Failed to find secret %s (ResourceNotFound)" % term)
                elif missing == 'warn':
                    self._display.warning('Skipping, did not find secret %s' % term)
            except is_boto3_error_code('AccessDeniedException'):  # pylint: disable=duplicate-except
                if denied == 'error':
                    raise AnsibleError("Failed to access secret %s (AccessDenied)" % term)
                elif denied == 'warn':
                    self._display.warning('Skipping, access denied for secret %s' % term)
            except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:  # pylint: disable=duplicate-except
                raise AnsibleError("Failed to retrieve secret: %s" % to_native(e))

        return None
