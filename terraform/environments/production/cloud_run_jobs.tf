# Job 1
resource "google_cloud_run_v2_job" "job1" {
  name     = "workflow1-job"
  location = var.region

  template {
    template {
      service_account = module.service_account.service_account_email
      containers {
        image = "gcr.io/${var.project_id}/workflow1:latest"
        
        env {
          name = "DISCORD_WEBHOOK_URL"
          value_source {
            secret_key_ref {
              secret  = module.secret_manager.secret_ids["discord_webhook_url"]
              version = "latest"
            }
          }
        }
        env {
          name = "NEWS_API_KEY"
          value_source {
            secret_key_ref {
              secret  = module.secret_manager.secret_ids["news_api_key"]
              version = "latest"
            }
          }
        }
        env {
          name = "BASE_URL"
          value_source {
            secret_key_ref {
              secret  = module.secret_manager.secret_ids["base_url"]
              version = "latest"
            }
          }
        }
      }
    }
  }
}

# Job 2
resource "google_cloud_run_v2_job" "job2" {
  name     = "workflow2-job"
  location = var.region

  template {
    template {
      service_account = module.service_account.service_account_email
      containers {
        image = "gcr.io/${var.project_id}/workflow2:latest"
        
        env {
          name = "DISCORD_NEW_RESEARCH_CHANNEL_ID"
          value_source {
            secret_key_ref {
              secret  = module.secret_manager.secret_ids["discord_new_research_channel_id"]
              version = "latest"
            }
          }
        }
        # Add other environment variables as needed for job2
      }
    }
  }
}

# Scheduler for Job 1
resource "google_cloud_scheduler_job" "job1_scheduler" {
  name        = "run-workflow1-job"
  description = "Trigger workflow1 job"
  schedule    = "0 * * * *"  # Run every hour, adjust as needed
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.job1.name}:run"
    
    oauth_token {
      service_account_email = module.service_account.service_account_email
    }
  }
}

# Scheduler for Job 2
resource "google_cloud_scheduler_job" "job2_scheduler" {
  name        = "run-workflow2-job"
  description = "Trigger workflow2 job"
  schedule    = "0 */2 * * *"  # Run every 2 hours, adjust as needed
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.job2.name}:run"
    
    oauth_token {
      service_account_email = module.service_account.service_account_email
    }
  }
}