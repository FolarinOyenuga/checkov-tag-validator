"""
Custom Checkov policy to validate required tags on AWS resources in Terraform plan.
This policy works with terraform_plan framework to see tags_all and module-created resources.
"""
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
import json
import os


def load_required_tags():
    """Load required tags from config file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('required_tags', [])
    except Exception:
        # Default MoJ tags
        return [
            'business-unit',
            'application',
            'owner',
            'is-production',
            'service-area',
            'environment'
        ]


REQUIRED_TAGS = load_required_tags()


class RequiredTagsPlanCheck(BaseResourceCheck):
    def __init__(self):
        name = "Ensure resource has all required tags"
        id = "CKV_AWS_TAG_001"
        supported_resources = ['*']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Check if resource has all required tags.
        Works with both static terraform files and terraform plan JSON.

        In plan JSON, the structure is different:
        - conf contains the resource configuration from plan
        - tags_all contains merged default_tags + resource tags
        """
        # Try to get tags from different possible locations
        # Plan JSON format
        tags = None
        tags_all = None

        # Direct tags attribute
        if isinstance(conf, dict):
            tags = conf.get('tags')
            tags_all = conf.get('tags_all')

        # Handle list format from Checkov static scanning
        if isinstance(tags, list) and tags:
            tags = tags[0] if tags[0] else {}
        if isinstance(tags_all, list) and tags_all:
            tags_all = tags_all[0] if tags_all[0] else {}

        # Skip resources without tags support (no tags or tags_all field at all)
        if tags is None and tags_all is None:
            return CheckResult.UNKNOWN

        # Prefer tags_all (includes provider default_tags merged with resource tags)
        effective_tags = tags_all if tags_all else tags

        if not isinstance(effective_tags, dict):
            effective_tags = {}

        # Check for missing or empty tags
        missing = []
        for tag in REQUIRED_TAGS:
            if tag not in effective_tags:
                missing.append(tag)
            elif not effective_tags[tag] or str(effective_tags[tag]).strip() == '':
                missing.append(f"{tag} (empty)")

        if missing:
            self.details = f"Missing tags: {', '.join(missing)}"
            return CheckResult.FAILED

        return CheckResult.PASSED


check = RequiredTagsPlanCheck()
