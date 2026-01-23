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
                    # Get file location details
                    file_path = check_type.get('file_path', 'Unknown')
                    file_line_range = check_type.get('file_line_range', [0, 0])
                    start_line = file_line_range[0] if file_line_range else 0
                    end_line = file_line_range[1] if len(file_line_range) > 1 else start_line
                    
                    violations.append({
                        'resource': check_type.get('resource', 'Unknown'),
                        'file': file_path,
                        'start_line': start_line,
                        'end_line': end_line,
                        'check': check_type.get('check_id', 'Unknown'),
                        'message': check_type.get('check_name', 'Missing required tags'),
                        'details': check_type.get('check_result', {}).get('evaluated_keys', [])
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
            # Format: resource (file:line-line)
            location = f"{v['file']}:{v['start_line']}"
            if v['end_line'] != v['start_line']:
                location = f"{v['file']}:{v['start_line']}-{v['end_line']}"
            summary_lines.append(f"- **{v['resource']}**")
            summary_lines.append(f"  - 📁 `{location}`")
            summary_lines.append(f"  - ❌ {v['message']}")
    
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
