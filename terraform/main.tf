terraform {
  required_providers {
    minio = {
      source  = "aminueza/minio"
      version = "1.13.0"
    }
  }
}

provider "minio" {
  minio_server   = "minio:9000"
  minio_user     = "admin"
  minio_password = "password123"
  minio_ssl      = false
}

resource "minio_s3_bucket" "creditstar_features" {
  bucket = "creditstar-features"
  acl    = "public"
}
