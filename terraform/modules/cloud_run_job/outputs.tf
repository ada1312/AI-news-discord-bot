output "job_name" {
  value = google_cloud_run_v2_job.job.name
}

output "job_id" {
  value = google_cloud_run_v2_job.job.id
}

output "scheduler_job_name" {
  value = google_cloud_scheduler_job.job_scheduler.name
}

output "scheduler_job_id" {
  value = google_cloud_scheduler_job.job_scheduler.id
}