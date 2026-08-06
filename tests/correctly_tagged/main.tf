terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = "eu-west-2"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_requesting_account_id  = true
    access_key                  = "mock"
    secret_key                  = "mock"
}

resource "aws_s3_bucket" "test" {
    bucket = "test-bucket-compliant"

    tags = {
        business-unit = "HMPPS"
        application   = "test-app"
        owner         = "testo@example.com"
        is-production = "false"
        service-area  = "testing"
    }
}