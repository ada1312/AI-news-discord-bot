variable "job_name" {
  description = "The name of the Cloud Run job"
  type        = string
}

variable "location" {
  description = "The location where the job and scheduler will be deployed"
  type        = string
}

variable "container_image" {
  description = "The container image for the Cloud Run job"
  type        = string
}

variable "service_account_email" {
  description = "The service account email to use with the Cloud Run job"
  type        = string
}

variable "job_timeout" {
  description = "The maximum duration of the Cloud Run job"
  default     = "3540s"
  type        = string
}

variable "scheduler_job_name" {
  description = "The name of the Cloud Scheduler job"
  type        = string
}

variable "scheduler_schedule" {
  description = "The schedule on which the Cloud Scheduler job should run"
  type        = string
}

variable "time_zone" {
  description = "The time zone for the Cloud Scheduler job schedule"
  type        = string
  default     = "Etc/UTC"
}

variable "discord_webhook_url" {
  description = "The Discord webhook URL"
  type        = string
}

variable "news_api_key" {
  description = "The News API key"
  type        = string
}

variable "base_url" {
  description = "The base URL for the Cloud Run job"
  type        = string
}

variable "discord_new_research_channel_id" {
  description = "The Discord new research channel ID"
  type        = string
}

variable "project_id" {
  description = "The project ID"
  type        = string
  
}