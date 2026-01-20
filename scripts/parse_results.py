#!/usr/bin/env python3
"""
Parses Checkov JSON output and generates GitHub Action outputs.
"""
import os
import json
import glob


def main():
    terraform_dir = os.environ.get('TERRAFORM_DIR', '.')
    soft_fail = os.environ.get('SOFT_FAIL', 'false').lower() == 'true'
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    
    # Find Checkov JSON output
    json_files = glob.glob(os.path.join(terraform_dir, 'results_*.json'))
    
    violations = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                results = json.load(f)
            
            # Parse failed checks
            for check_type in results.get('results', {}).get('failed_checks', []):
                if 'CKV_AWS_TAG' in check_type.get('check_id', ''):
                    violations.append({
                        'resource': check_type.get('resource', 'Unknown'),
                        'file': check_type.get('file_path', 'Unknown'),
                        'check': check_type.get('check_id', 'Unknown'),
                        'message': check_type.get('check_name', 'Missing required tags')
                    })
        except Exception as e:
            print(f"Warning: Could not parse {json_file}: {e}")
    
    # Build summary
    violations_count = len(violations)
    passed = violations_count == 0
    
    summary_lines = []
    if passed:
        summary_lines.append("✅ **All resources have required tags**")
    else:
        summary_lines.append(f"❌ **Found {violations_count} tag violation(s)**\n")
        for v in violations:
            summary_lines.append(f"- **{v['resource']}** ({v['file']})")
            summary_lines.append(f"  - {v['message']}")
    
    summary = '\n'.join(summary_lines)
    
    # Print results
    print(f"\n📊 Violations: {violations_count}")
    print(summary)
    
    # Write outputs
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"violations_count={violations_count}\n")
            f.write(f"passed={str(passed).lower()}\n")
            f.write(f"violations_summary<<EOF\n{summary}\nEOF\n")
    
    # Exit code
    if not passed and not soft_fail:
        exit(1)


if __name__ == '__main__':
    main()
