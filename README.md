# Checkov Tag Validator

A GitHub Action that validates Terraform resources have required tags using [Checkov](https://www.checkov.io/).

## Usage

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
            environment-name

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
- `environment-name`

## Features

- **Dynamic resource detection** - Checks all taggable AWS resources
- **tags_all support** - Works with AWS provider v3.38.0+ default_tags
- **Configurable** - Specify your own required tags
- **PR comments** - Easy integration with GitHub PR workflows

## License

MIT
