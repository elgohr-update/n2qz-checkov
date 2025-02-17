import json
import re

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

ACCOUNT_ACCESS = re.compile(r'\d{12}|arn:aws:iam::\d{12}:root')

class IAMRoleAllowAssumeFromAccount(BaseResourceCheck):
    def __init__(self):
        name = "Ensure IAM role allows only specific principals in account to assume it"
        id = "CKV_AWS_61"
        supported_resources = ['AWS::IAM::Role']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'AssumeRolePolicyDocument' in conf['Properties']:
            assume_role_policy_doc = conf['Properties']['AssumeRolePolicyDocument']
            if isinstance(assume_role_policy_doc, dict) and 'Fn::Sub' in assume_role_policy_doc.keys():
                assume_role_block = json.loads(assume_role_policy_doc['Fn::Sub'])
            elif isinstance(assume_role_policy_doc, str):
                assume_role_block = json.loads(assume_role_policy_doc)
            else:
                assume_role_block = assume_role_policy_doc

        if 'Statement' in assume_role_block.keys():
            if isinstance(assume_role_block['Statement'], list) and 'Principal' in \
                    assume_role_block['Statement'][0]:
                if 'AWS' in assume_role_block['Statement'][0]['Principal']:
                    if isinstance(assume_role_block['Statement'][0]['Principal']['AWS'],list) \
                            and isinstance(assume_role_block['Statement'][0]['Principal']['AWS'][0], str):
                        if re.match(ACCOUNT_ACCESS, assume_role_block['Statement'][0]['Principal']['AWS'][0]):
                            return CheckResult.FAILED

            return CheckResult.PASSED


check = IAMRoleAllowAssumeFromAccount()
