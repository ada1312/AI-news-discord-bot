provider "google" {
  project = var.project_id
  region  = "us-central1"
}

module "service_account" {
  source             = "../../modules/service_account"
  account_id         = "discord-bot-ai-agent"  # Make sure this matches exactly
  display_name       = "Discord Bot Agent"
  description        = "Service account with cloud run permissions and run codes for discord bots"
  project_id         = var.project_id

  role_id            = "telegram_chat_etl_agent"
  role_title         = "Telegram Chat ETL Agent"
  role_description   = "Custom role for telegram etl agent permissions"
  role_permissions   = [
    "run.jobs.run",
    "run.executions.cancel",
    "run.routes.invoke",
    "iam.serviceAccounts.actAs",  # Add this permission
  ]
}

module "secret_manager" {
  source     = "../../modules/secret_manager"
  project_id = var.project_id
}

resource "google_secret_manager_secret_version" "discord_webhook_url" {
  secret      = module.secret_manager.secret_ids["discord_webhook_url"]
  secret_data = var.discord_webhook_url
}

resource "google_secret_manager_secret_version" "news_api_key" {
  secret      = module.secret_manager.secret_ids["news_api_key"]
  secret_data = var.news_api_key
}

resource "google_secret_manager_secret_version" "base_url" {
  secret      = module.secret_manager.secret_ids["base_url"]
  secret_data = var.base_url
}

resource "google_secret_manager_secret_version" "discord_new_research_channel_id" {
  secret      = module.secret_manager.secret_ids["discord_new_research_channel_id"]
  secret_data = var.discord_new_research_channel_id
}


module "cloud_run" {
  source                        = "../../modules/cloud_run_job"
  location                      = "us-central1"
  project_id                    = var.project_id
  service_account_email         = module.service_account.service_account_email
  container_image               = "gcr.io/container-testing-381309/discord-bot:latest"
  job_name                      = "discord-bot-update"
  scheduler_job_name            = "discord-bot-update-scheduler"
  scheduler_schedule            = "0 * * * *"
  job_timeout                   = "3540s"
  DISCORD_WEBHOOK_URL          = module.secret_manager.secret_ids["discord_webhook_url"]
  NEWS_API_KEY                 = module.secret_manager.secret_ids["news_api_key"]
  BASE_URL                     = module.secret_manager.secret_ids["base_url"]
  DISCORD_NEW_RESEARCH_CHANNEL_ID = module.secret_manager.secret_ids["discord_new_research_channel_id"]
}

data "google_project" "project" {}

resource "google_secret_manager_secret_iam_member" "secret_access" {
  for_each  = module.secret_manager.secret_ids
  project   = var.project_id
  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:service-${data.google_project.project.number}@serverless-robot-prod.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "compute_service_account_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${var.project_id}-compute@developer.gserviceaccount.com"
}

output "service_account_email" {
  value = module.service_account.service_account_email
}

output "service_account_unique_id" {
  value = module.service_account.service_account_unique_id
}

output "custom_role_id" {
  value = module.service_account.custom_role_id
}