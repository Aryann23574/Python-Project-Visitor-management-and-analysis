import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "visitors.csv")

FIELDS = ["VisitorID", "Date", "Name", "Contact", "Purpose", "EntryTime", "ExitTime", "Status", "Notes"]

class VisitorManager:
    """Handles CSV persistence and visitor CRUD/search operations."""

    def __init__(self, csv_path=CSV_PATH):
        self.csv_path = csv_path
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.csv_path) or os.path.getsize(self.csv_path) == 0:
            with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                writer.writeheader()

    def get_all(self):
        self._ensure_file()
        with open(self.csv_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return [self._normalize_row(row) for row in reader]

    @staticmethod
    def _normalize_row(row):
        return {field: str(row.get(field, "") or "") for field in FIELDS}

    def _write_all(self, records):
        with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            for record in records:
                writer.writerow({field: str(record.get(field, "") or "") for field in FIELDS})

    def add_visitor(self, data):
        records = self.get_all()
        next_id = max([int(r["VisitorID"]) for r in records if r["VisitorID"].isdigit()] or [0]) + 1
        record = {
            "VisitorID": str(next_id),
            "Date": data["date"],
            "Name": data["name"],
            "Contact": data["contact"],
            "Purpose": data["purpose"],
            "EntryTime": data["entry_time"],
            "ExitTime": data.get("exit_time", ""),
            "Status": data.get("status", "Checked-In"),
            "Notes": data.get("notes", ""),
        }
        if record["Status"] == "Checked-Out" and not record["ExitTime"]:
            raise ValueError("Exit time is required when status is Checked-Out.")
        records.append(record)
        self._write_all(records)
        return record

    def update_visitor(self, visitor_id, data, already_normalized=False):
        records = self.get_all()
        updated = False
        for index, record in enumerate(records):
            if record["VisitorID"] == str(visitor_id):
                if already_normalized:
                    new_record = self._normalize_row(data)
                    new_record["VisitorID"] = str(visitor_id)
                else:
                    new_record = {
                        "VisitorID": str(visitor_id),
                        "Date": data["date"],
                        "Name": data["name"],
                        "Contact": data["contact"],
                        "Purpose": data["purpose"],
                        "EntryTime": data["entry_time"],
                        "ExitTime": data.get("exit_time", ""),
                        "Status": data.get("status", "Checked-In"),
                        "Notes": data.get("notes", ""),
                    }
                records[index] = new_record
                updated = True
                break
        if not updated:
            raise ValueError(f"Visitor ID {visitor_id} was not found.")
        self._write_all(records)

    def delete_visitor(self, visitor_id):
        records = self.get_all()
        remaining = [r for r in records if r["VisitorID"] != str(visitor_id)]
        if len(remaining) == len(records):
            raise ValueError(f"Visitor ID {visitor_id} was not found.")
        self._write_all(remaining)

    def get_by_id(self, visitor_id):
        for record in self.get_all():
            if record["VisitorID"] == str(visitor_id):
                return record
        return None

    def filter_records(self, query="", purpose="All", status="All", from_date="", to_date=""):
        records = self.get_all()
        query = (query or "").strip().lower()
        filtered = []
        for row in records:
            searchable = " ".join([row["Name"], row["Contact"], row["Notes"], row["Purpose"]]).lower()
            if query and query not in searchable:
                continue
            if purpose and purpose != "All" and row["Purpose"] != purpose:
                continue
            if status and status != "All" and row["Status"] != status:
                continue
            try:
                row_date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
                if from_date.strip():
                    start = datetime.strptime(from_date.strip(), "%Y-%m-%d").date()
                    if row_date < start:
                        continue
                if to_date.strip():
                    end = datetime.strptime(to_date.strip(), "%Y-%m-%d").date()
                    if row_date > end:
                        continue
            except ValueError as exc:
                raise ValueError("Dates must use YYYY-MM-DD format.") from exc
            filtered.append(row)
        return filtered
