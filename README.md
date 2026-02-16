# Checkov Tag Validator

[![CI](https://github.com/FolarinOyenuga/checkov-tag-validator/actions/workflows/ci.yml/badge.svg)](https://github.com/FolarinOyenuga/checkov-tag-validator/actions/workflows/ci.yml)

> **Shift-left tag enforcement for Terraform PRs**. Catch missing or invalid tags before they reach production.

## Impact

Untagged AWS resources cost organisations money and create compliance gaps. This action:

- **Prevents untagged resources** from being deployed by failing PRs with missing tags
- **Enforces consistency** across teams by validating against a defined tag policy
- **Reduces remediation costs** by catching issues at PR time, not after deployment
- **Supports FinOps and compliance** by ensuring resources are properly attributed

## Features

- **Works with modules**: Validates tags on module-created resources via Terraform plan
- **Detects empty values**: Catches null, empty, or whitespace-only tag values
- **Supports default_tags**: Works with AWS provider `default_tags` via `tags_all`
- **Configurable**: Specify your own required tags or use MoJ defaults

## Quick Start

```yaml
name: Validate Tags

on:
  pull_request:
    paths:
      - '**/*.tf'

permissions:
  contents: read
  pull-requests: write

jobs:
  validate-tags:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: FolarinOyenuga/checkov-tag-validator@v1
        id: validate
        with:
          terraform_directory: ./terraform
          required_tags: |
            business-unit
            application
            owner
            is-production
            service-area
            environment

      # Optional: Post results as PR comment
      - name: Post Validation Results
        if: always() && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        env:
          SUMMARY: ${{ steps.validate.outputs.violations_summary }}
        with:
          script: |
            const summary = process.env.SUMMARY || '✅ All resources have required tags';
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🏷️ Checkov Tag Validation\n\n${summary}`
            });
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `terraform_directory` | Path to Terraform files | Yes | `.` |
| `required_tags` | List of required tag keys (newline or comma-separated) | Yes | MoJ defaults |
| `framework` | Checkov framework to use | No | `terraform` |
| `soft_fail` | Return exit code 0 even if violations found | No | `false` |

## Outputs

| Output | Description |
|--------|-------------|
| `violations_count` | Number of tag violations found |
| `violations_summary` | Markdown summary for PR comments |
| `passed` | Whether validation passed (`true`/`false`) |

## Default Required Tags

If not specified, the following MoJ tags are required:
- `business-unit`
- `application`
- `owner`
- `is-production`
- `service-area`
- `environment`

## How It Works

1. **Generates Terraform plan**: Runs `terraform init` and `terraform plan` with dummy credentials
2. **Scans plan with Checkov**: Uses custom policy to check `tags_all` on all resources
3. **Reports violations**: Outputs violation count, pass/fail status, and markdown summary

## Integration Guide

### For Teams Adopting This Action

1. Add the workflow file to `.github/workflows/validate-tags.yml`
2. Ensure your Terraform can `init` without real credentials (use `backend = false`)
3. Configure required tags for your team's needs
4. Optionally add PR comment integration for visibility

### Handling Violations

When violations are detected:
- The action exits with code 1 (fails the check)
- The `violations_summary` output contains markdown-formatted details
- Use `soft_fail: true` to report violations without failing the build

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b my-feature`)
3. Run linting locally: `ruff check . && ruff format --check .`
4. Commit and push your changes
5. Open a pull request

## License

MIT
