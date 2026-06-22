variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-west1"
}

variable "agent_runtime_id" {
  type = string
}

variable "dashboard_image" {
  type = string
}
variable "allow_unauthenticated" {
  type        = bool
  description = "Codelab-only public access switch. Keep false for production."
  default     = false
}
