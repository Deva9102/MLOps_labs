# Configure the Google Cloud provider
provider "google" {
  project = "terraform-lab-project-479903"  # GCP project ID
  region  = "us-central1"
  zone    = "us-central1-a"
}

# Compute Engine VM + Flask app 

# Startup script to install Python + Flask and run the timezone web app.
resource "google_compute_instance" "vm_instance" {
  name         = "terraform-vm"
  machine_type = "e2-micro"        # free-tier friendly instance type
  zone         = "us-central1-a"

  labels = {
    environment = "lab"
    owner       = "devadarshini"
    purpose     = "terraform-beginner-lab"
  }

  # Network tag used by the firewall rule below
  tags = ["timezone-app"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"  
      size  = 12                       
    }
  }

  # Attach the VM to the default VPC and give it an external IP so we can access the Flask app from the internet.
  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    # Log everything from this script to /var/log/startup-script.log
    exec > /var/log/startup-script.log 2>&1
    set -eux

    # Install Python and pip
    apt-get update -y
    apt-get install -y python3 python3-pip

    # Create app directory
    mkdir -p /opt/timezone_app

    # Write the Flask app code to /opt/timezone_app/timezone_web.py
    cat << 'PYEOF' >/opt/timezone_app/timezone_web.py
from datetime import datetime
import pytz
from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = """
<!doctype html>
<title>Timezone Converter</title>
<h1>Timezone Converter</h1>
<p>Format: <code>YYYY-MM-DD HH:MM</code> (24-hour time)</p>
<p>Examples of timezones: UTC, US/Eastern, US/Pacific, Europe/London, Asia/Kolkata, Asia/Singapore, Australia/Sydney</p>
<form method="post">
  <p>
    <label>Time:
      <input name="time" value="{{ time }}" placeholder="2025-12-01 13:09">
    </label>
  </p>
  <p>
    <label>From timezone:
      <input name="from_tz" value="{{ from_tz }}" placeholder="UTC">
    </label>
  </p>
  <p>
    <label>To timezone:
      <input name="to_tz" value="{{ to_tz }}" placeholder="Asia/Kolkata">
    </label>
  </p>
  <button type="submit">Convert</button>
</form>

{% if result %}
  <h2>Result</h2>
  <p>{{ result }}</p>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    time_str = ""
    from_tz = "UTC"
    to_tz = "Asia/Kolkata"

    if request.method == "POST":
        time_str = request.form.get("time", "").strip()
        from_tz = request.form.get("from_tz", "UTC").strip()
        to_tz = request.form.get("to_tz", "Asia/Kolkata").strip()

        try:
            naive_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            from_zone = pytz.timezone(from_tz)
            to_zone = pytz.timezone(to_tz)
            localized = from_zone.localize(naive_dt)
            converted = localized.astimezone(to_zone)
            result = converted.strftime("%Y-%m-%d %H:%M (%Z%z)")
        except Exception as e:
            result = f"Error: {e}. Check your format and timezone names."

    return render_template_string(
        PAGE,
        result=result,
        time=time_str,
        from_tz=from_tz,
        to_tz=to_tz,
    )

if __name__ == "__main__":
PYEOF

    # Install Python dependencies for the app
    pip3 install flask pytz

    # Kill any old instance
    pkill -f "python3 /opt/timezone_app/timezone_web.py" || true

    # Start the Flask app in the background and log it.
    nohup python3 /opt/timezone_app/timezone_web.py > /var/log/timezone_web.log 2>&1 &
  EOT
}

# Firewall rule for port 8080 
resource "google_compute_firewall" "allow-http-8080" {
  name    = "allow-http-8080"
  network = "default"

  direction     = "INGRESS"
  source_ranges = ["0.0.0.0/0"]
  target_tags = ["timezone-app"]

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }
}

# Cloud Storage bucket 

resource "google_storage_bucket" "terraform-lab-bucket" {
  name          = "terraform-lab-bucket-devadarshini-12345"
  location      = "us-central1"
  force_destroy = true
}

# Outputs 

# External IP of the VM 
output "vm_external_ip" {
  description = "External IP of the Terraform VM"
  value       = google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip
}

# Full URL of the Flask app
output "app_url" {
  description = "URL of the timezone Flask app"
  value       = "http://${google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip}:8080"
}
