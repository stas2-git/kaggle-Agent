locals {
  runtime_resource = "projects/${var.project_id}/locations/${var.region}/reasoningEngines/${var.agent_runtime_id}"
  query_endpoint   = "https://${var.region}-aiplatform.googleapis.com/v1/${local.runtime_resource}:query"
}

resource "google_project_service" "apis" {
  for_each = toset(["aiplatform.googleapis.com", "cloudbuild.googleapis.com", "pubsub.googleapis.com", "run.googleapis.com"])
  project = var.project_id
  service = each.value
  disable_on_destroy = false
}

resource "google_project_service_identity" "pubsub" {
  provider = google-beta
  project  = var.project_id
  service  = "pubsub.googleapis.com"
}

resource "google_service_account" "dashboard" {
  project = var.project_id
  account_id = "expense-dashboard"
  display_name = "Expense manager dashboard"
}

resource "google_service_account" "pubsub_invoker" {
  project = var.project_id
  account_id = "pubsub-invoker"
  display_name = "Pub/Sub Agent Runtime invoker"
}

resource "google_project_iam_member" "dashboard_agent_user" {
  project = var.project_id
  role = "roles/aiplatform.user"
  member = "serviceAccount:${google_service_account.dashboard.email}"
}

resource "google_project_iam_member" "pubsub_agent_user" {
  project = var.project_id
  role = "roles/aiplatform.user"
  member = "serviceAccount:${google_service_account.pubsub_invoker.email}"
}

resource "google_service_account_iam_member" "pubsub_token_creator" {
  service_account_id = google_service_account.pubsub_invoker.name
  role = "roles/iam.serviceAccountTokenCreator"
  member = google_project_service_identity.pubsub.member
}

resource "google_cloud_run_v2_service" "dashboard" {
  project = var.project_id
  name = "expense-manager-dashboard"
  location = var.region
  template {
    service_account = google_service_account.dashboard.email
    containers {
      image = var.dashboard_image
      ports {
        container_port = 8080
      }
      env {
        name  = "DASHBOARD_MODE"
        value = "vertex"
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }
      env {
        name  = "AGENT_RUNTIME_ID"
        value = var.agent_runtime_id
      }
      resources {
        limits = { cpu = "1", memory = "512Mi" }
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }
  depends_on = [google_project_service.apis]
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  count = var.allow_unauthenticated ? 1 : 0
  project = var.project_id
  location = var.region
  name = google_cloud_run_v2_service.dashboard.name
  role = "roles/run.invoker"
  member = "allUsers"
}

resource "google_pubsub_topic" "expenses" {
  project = var.project_id
  name    = "expense-reports"
}

resource "google_pubsub_topic" "dead_letter" {
  project = var.project_id
  name    = "expense-reports-dead-letter"
}

resource "google_pubsub_subscription" "expense_push" {
  project = var.project_id
  name = "expense-reports-push"
  topic = google_pubsub_topic.expenses.id
  ack_deadline_seconds = 600
  push_config {
    push_endpoint = local.query_endpoint
    oidc_token {
      service_account_email = google_service_account.pubsub_invoker.email
      audience              = local.query_endpoint
    }
    no_wrapper {
      write_metadata = false
    }
  }
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  depends_on = [google_service_account_iam_member.pubsub_token_creator]
}

resource "google_pubsub_topic_iam_member" "dead_letter_publisher" {
  project = var.project_id
  topic = google_pubsub_topic.dead_letter.name
  role = "roles/pubsub.publisher"
  member = google_project_service_identity.pubsub.member
}

resource "google_pubsub_subscription_iam_member" "forwarding_subscriber" {
  project = var.project_id
  subscription = google_pubsub_subscription.expense_push.name
  role = "roles/pubsub.subscriber"
  member = google_project_service_identity.pubsub.member
}
