output "dashboard_url" {
  value = google_cloud_run_v2_service.dashboard.uri
}

output "expense_topic" {
  value = google_pubsub_topic.expenses.id
}

output "push_endpoint" {
  value = local.query_endpoint
}
