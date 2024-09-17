resource "google_cloud_run_v2_job" "job1" {
  name     = var.job_name
  location = var.location

  template {
    template {
      containers {
        image = var.container_image
        # Add secret environment variables
        env {
          name = "DISCORD_WEBHOOK_URL"
          value_source {
            secret_key_ref {
              secret  = var.discord_webhook_url
              version = "latest"
            }
          }
        }
        env {
          name = "NEWS_API_KEY"
          value_source {
            secret_key_ref {
              secret  = var.news_api_key
              version = "latest"
            }
          }
        }
      }
      service_account = var.service_account_email
      timeout         = var.job_timeout
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }
}



resource "google_cloud_run_v2_job" "job2" {
  name     = var.job_name
  location = var.location

  template {
    template {
      containers {
        image = var.container_image
        # Add secret environment variables
        env {
          name = "BASE_URL"
          value_source {
            secret_key_ref {
              secret  = var.base_url
              version = "latest"
            }
          }
        }
        env {
          name = "DICORD_NEW_RESEARCH_CHANNEL_ID"
          value_source {
            secret_key_ref {
              secret  = var.discord_new_research_channel_id
              version = "latest"
            }
          }
        }
      }
      service_account = var.service_account_email
      timeout         = var.job_timeout
    }
  }

  lifecycle {
    ignore_changes = [
      launch_stage,
    ]
  }
}


resource "google_cloud_scheduler_job" "job" {
  name     = var.scheduler_job_name
  schedule = var.scheduler_schedule
  time_zone = var.time_zone
  region = var.location
  http_target {
    uri        = "https://${var.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${var.job_name}:run"
    http_method = "POST"

    oauth_token {
      service_account_email = var.service_account_email
    }    
  }
  depends_on = [google_cloud_run_v2_job.default]
}