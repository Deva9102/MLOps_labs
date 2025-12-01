"""
Command-line timezone converter.

This is the CLI version of the timezone app. It runs locally (or on the VM)
and asks the user for a datetime and two timezones, then prints the converted
time in the target timezone.
"""

from datetime import datetime
import pytz


def list_examples():
    """Print a few example timezone names for the user."""
    print("\nSome common timezones you can use:")
    print("  UTC")
    print("  US/Eastern")
    print("  US/Pacific")
    print("  Europe/London")
    print("  Asia/Kolkata")
    print("  Asia/Singapore")
    print("  Australia/Sydney")
    print()


def convert_time():
    """Main loop: prompt user for inputs and perform conversions."""
    print("Timezone Converter :")
    list_examples()

    while True:
        # Get the datetime string or quit
        time_str = input("\nEnter time (YYYY-MM-DD HH:MM) or 'q' to quit: ").strip()
        if time_str.lower() == "q":
            print("Goodbye!")
            break

        # Get source and target timezones
        from_tz_name = input("From timezone (e.g. UTC): ").strip()
        to_tz_name   = input("To timezone   (e.g. Asia/Kolkata): ").strip()

        try:
            # Parse naive datetime
            naive_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")

            # Look up timezone objects
            from_tz = pytz.timezone(from_tz_name)
            to_tz   = pytz.timezone(to_tz_name)

            # Attach source timezone and convert to target
            localized = from_tz.localize(naive_dt)
            converted = localized.astimezone(to_tz)

            # Print nicely formatted result with TZ name + offset
            print(f"\nResult: {converted.strftime('%Y-%m-%d %H:%M (%Z%z)')}")
        except Exception as e:
            # Any parsing or timezone error ends up here
            print(f"\nError: {e}")
            print("Check your format and timezone names and try again.")


if __name__ == "__main__":
    convert_time()
