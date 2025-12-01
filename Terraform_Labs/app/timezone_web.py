"""
Simple Flask timezone converter web app.

This runs on the VM created by Terraform.
It listens on 0.0.0.0:8080 so it can be reached via the VM's external IP.
"""

from datetime import datetime
import pytz
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Basic HTML template
PAGE = """
<!doctype html>
<title>Timezone Converter</title>
<h1>Timezone Converter</h1>
<p>Format: <code>YYYY-MM-DD HH:MM</code> (24-hour time)</p>
<p>Examples of timezones: UTC, US/Eastern, US/Pacific, Europe/London,
Asia/Kolkata, Asia/Singapore, Australia/Sydney</p>
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
    """Handle form display + timezone conversion."""
    result = ""
    time_str = ""
    from_tz = "UTC"
    to_tz = "Asia/Kolkata"

    if request.method == "POST":
        # Read form fields
        time_str = request.form.get("time", "").strip()
        from_tz = request.form.get("from_tz", "UTC").strip()
        to_tz = request.form.get("to_tz", "Asia/Kolkata").strip()

        try:
            # Parse the input time
            naive_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")

            # Build timezone objects
            from_zone = pytz.timezone(from_tz)
            to_zone = pytz.timezone(to_tz)

            # Attach the "from" timezone, then convert to the "to" timezone
            localized = from_zone.localize(naive_dt)
            converted = localized.astimezone(to_zone)

            # Format the output with timezone name and offset
            result = converted.strftime("%Y-%m-%d %H:%M (%Z%z)")
        except Exception as e:
            # Any parsing/lookup error gets shown as a friendly message
            result = f"Error: {e}. Check your format and timezone names."

    # Render the page with the latest values + result
    return render_template_string(
        PAGE,
        result=result,
        time=time_str,
        from_tz=from_tz,
        to_tz=to_tz,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)