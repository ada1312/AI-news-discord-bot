resource "google_cloud_run_v2_job" "job" {
  name     = var.job_name_job1  # or just var.job_name if you simplify this
  location = var.location

  template {
    template {
      service_account = var.service_account_email
      containers {
        image = var.container_image
        
        dynamic "env" {
          for_each = {
            DISCORD_WEBHOOK_URL = var.discord_webhook_url
            NEWS_API_KEY = var.news_api_key
            BASE_URL = var.base_url
            DISCORD_NEW_RESEARCH_CHANNEL_ID = var.discord_new_research_channel_id
          }
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = env.value
                version = "latest"
              }
            }
          }
        }
      }
    }
  }
}

resource "google_cloud_scheduler_job" "job_scheduler" {
  name        = var.scheduler_job_name
  description = "Trigger ${var.job_name_job1} job"
  schedule    = var.scheduler_schedule
  time_zone   = var.time_zone

  http_target {
    http_method = "POST"
    uri         = "https://${var.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.job.name}:run"
    
    oauth_token {
      service_account_email = var.service_account_email
    }
  }
}