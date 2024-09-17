resource "google_secret_manager_secret" "api_id" {
  project     = var.project_id
  secret_id   = "api_id"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "discord_webhook_url" {
  project     = var.project_id
    secret_id   = "discord_webhook_url"
    replication {
      auto {}
    }
}

resource "google_secret_manager_secret" "news_api_key" {
    project     = var.project_id
        secret_id   = "news_api_key"
        replication {
          auto {}
        }
}

resource "google_secret_manager_secret" "base_url" {
    project     = var.project_id
        secret_id  = "base_url"
        replication {
          auto {}
        }
}

resource "google_secret_manager_secret" "discord_new_research_channel_id" {
    project     = var.project_id
        secret_id  = "discord_new_research_channel_id"
        replication {
          auto {}
        }
}
