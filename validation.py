from datetime import datetime

def validate_visitor(data):
    """Return a list of validation errors. An empty list means input is valid."""
    errors = []
    name = data.get("name", "").strip()
    contact = data.get("contact", "").strip()
    visit_date = data.get("date", "").strip()
    purpose = data.get("purpose", "").strip()
    entry_time = data.get("entry_time", "").strip()
    exit_time = data.get("exit_time", "").strip()
    status = data.get("status", "Checked-In").strip()

    if not name:
        errors.append("Visitor name is required.")
    if not contact.isdigit() or len(contact) != 10:
        errors.append("Contact number must contain exactly 10 digits.")
    if not visit_date:
        errors.append("Date is required.")
    else:
        try:
            datetime.strptime(visit_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Date must be in YYYY-MM-DD format (example: 2026-10-14).")
    if not purpose:
        errors.append("Visit purpose is required.")
    if not entry_time:
        errors.append("Entry time is required.")
    else:
        try:
            datetime.strptime(entry_time, "%H:%M")
        except ValueError:
            errors.append("Entry time must be in 24-hour HH:MM format (example: 09:30).")
    if exit_time:
        try:
            datetime.strptime(exit_time, "%H:%M")
            if entry_time:
                entry = datetime.strptime(entry_time, "%H:%M")
                exit_ = datetime.strptime(exit_time, "%H:%M")
                if exit_ < entry:
                    errors.append("Exit time cannot be earlier than entry time.")
        except ValueError:
            errors.append("Exit time must be in 24-hour HH:MM format (example: 10:45).")
    if status not in ("Checked-In", "Checked-Out"):
        errors.append("Status must be Checked-In or Checked-Out.")
    if status == "Checked-Out" and not exit_time:
        errors.append("Exit time is required for a Checked-Out visitor.")
    return errors
