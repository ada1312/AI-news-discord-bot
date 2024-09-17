output "secret_ids" {
  value = {
    discord_webhook_url = google_secret_manager_secret.discord_webhook_url.id
    news_api_key        = google_secret_manager_secret.news_api_key.id
    base_url            = google_secret_manager_secret.base_url.id
    discord_new_research_channel_id = google_secret_manager_secret.discord_new_research_channel_id.id
  }
}