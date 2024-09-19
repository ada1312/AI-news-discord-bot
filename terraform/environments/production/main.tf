provider "google" {
  project = var.project_id
  region  = var.region
}

module "service_account" {
  source             = "../../modules/service_account"
  account_id         = "discord-bot-ai-agent"
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
    "iam.serviceAccounts.actAs", 
    "secretmanager.versions.access",
    "secretmanager.versions.get",
    "secretmanager.secrets.get",
    "secretmanager.secrets.list",
    "secretmanager.secrets.create",
    "secretmanager.secrets.update"
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

module "cloud_run_job_1" {
  source = "../../modules/cloud_run_job"

  project_id            = var.project_id
  job_name_job1         = "discord-ai-news-bot"
  job_name_job2         = "discord-ai-news-bot-placeholder"  # This is required but not used for this job
  location              = var.region
  container_image       = "gcr.io/${var.project_id}/discord-ai-news-bot:latest"
  service_account_email = module.service_account.service_account_email
  job_timeout           = "3540s"
  scheduler_job_name    = "run-discord-ai-news-bot-job"
  scheduler_schedule    = "0 14 * * *"
  time_zone             = "UTC"
  discord_webhook_url   = module.secret_manager.secret_ids["discord_webhook_url"]
  news_api_key          = module.secret_manager.secret_ids["news_api_key"]
  base_url              = module.secret_manager.secret_ids["base_url"]
  discord_new_research_channel_id = module.secret_manager.secret_ids["discord_new_research_channel_id"]
}

module "cloud_run_job_2" {
  source = "../../modules/cloud_run_job"

  project_id            = var.project_id
  job_name_job1         = "discord-daily-arxiv-bot-placeholder"  # This is required but not used for this job
  job_name_job2         = "discord-daily-arxiv-bot"
  location              = var.region
  container_image       = "gcr.io/${var.project_id}/discord-daily-arxiv-bot:latest"
  service_account_email = module.service_account.service_account_email
  job_timeout           = "3540s"
  scheduler_job_name    = "run-discord-daily-arxiv-bot-job"
  scheduler_schedule    = "0 11 * * *"
  time_zone             = "UTC"
  discord_webhook_url   = module.secret_manager.secret_ids["discord_webhook_url"]
  news_api_key          = module.secret_manager.secret_ids["news_api_key"]
  base_url              = module.secret_manager.secret_ids["base_url"]
  discord_new_research_channel_id = module.secret_manager.secret_ids["discord_new_research_channel_id"]
}

resource "google_service_account" "compute_service_account" {
  account_id   = "compute-${substr(lower(replace(var.project_id, "-", "")), 0, 20)}"
  display_name = "Compute Engine default service account"
}

resource "google_project_iam_member" "compute_service_account_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.compute_service_account.email}"
}

data "google_project" "project" {}

resource "google_secret_manager_secret_iam_member" "secret_access" {
  for_each  = module.secret_manager.secret_ids
  project   = var.project_id
  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:service-${data.google_project.project.number}@serverless-robot-prod.iam.gserviceaccount.com"
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