"""
Custom Checkov policy to validate required tags on AWS resources.
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
            'environment-name'
        ]


REQUIRED_TAGS = load_required_tags()


class RequiredTagsCheck(BaseResourceCheck):
    def __init__(self):
        name = "Ensure resource has all required tags"
        id = "CKV_AWS_TAG_001"
        supported_resources = ['*']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
        Check if resource has all required tags.
        """
        # Get tags from resource (check both tags and tags_all)
        tags = conf.get('tags', [{}])
        tags_all = conf.get('tags_all', [{}])
        
        # Handle list format from Checkov
        if isinstance(tags, list) and tags:
            tags = tags[0] if tags[0] else {}
        if isinstance(tags_all, list) and tags_all:
            tags_all = tags_all[0] if tags_all[0] else {}
        
        # Skip resources without tags support
        if not tags and not tags_all:
            return CheckResult.UNKNOWN
        
        # Prefer tags_all (includes provider default_tags)
        effective_tags = tags_all if tags_all else tags
        
        if not isinstance(effective_tags, dict):
            return CheckResult.FAILED
        
        # Check for missing tags
        missing = [tag for tag in REQUIRED_TAGS if tag not in effective_tags]
        
        if missing:
            self.details = f"Missing tags: {', '.join(missing)}"
            return CheckResult.FAILED
        
        return CheckResult.PASSED


check = RequiredTagsCheck()
