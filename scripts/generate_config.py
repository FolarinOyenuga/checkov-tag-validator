#!/usr/bin/env python3
"""
Generates Checkov custom policy configuration based on required tags input.
"""
import os
import json


def parse_required_tags(tags_input: str) -> list:
    """Parse required tags from input (comma-separated or newline-separated)."""
    if ',' in tags_input:
        return [t.strip() for t in tags_input.split(',') if t.strip()]
    return [t.strip() for t in tags_input.split('\n') if t.strip()]


def main():
    required_tags = os.environ.get('REQUIRED_TAGS', '')
    tags = parse_required_tags(required_tags)
    
    if not tags:
        print("⚠️  No required tags specified")
        return
    
    print(f"📋 Required tags: {', '.join(tags)}")
    
    # Write tags to file for custom policy to read
    config = {
        'required_tags': tags
    }
    
    config_path = os.path.join(os.environ.get('GITHUB_ACTION_PATH', '.'), 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    print(f"✅ Generated config at {config_path}")


if __name__ == '__main__':
    main()
