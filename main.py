import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import os

from visitor_manager import VisitorManager
from validation import validate_visitor
from analytics import get_summary, generate_visitor_trend, generate_purpose_chart, generate_peak_hour_chart

APP_TITLE = "Visitor Management & Analysis System"

class VisitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1120x720")
        self.root.minsize(950, 620)
        self.manager = VisitorManager()
        self.selected_id = None

        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        title = ttk.Label(self.root, text=APP_TITLE, font=("Arial", 18, "bold"))
        title.pack(pady=(12, 4))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=10)

        self.dashboard_tab = ttk.Frame(self.notebook, padding=12)
        self.form_tab = ttk.Frame(self.notebook, padding=12)
        self.records_tab = ttk.Frame(self.notebook, padding=12)
        self.analytics_tab = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.form_tab, text="Add / Edit Visitor")
        self.notebook.add(self.records_tab, text="Visitor Records")
        self.notebook.add(self.analytics_tab, text="Analytics & Reports")

        self._build_dashboard()
        self._build_form()
        self._build_records()
        self._build_analytics()

    def _build_dashboard(self):
        ttk.Label(self.dashboard_tab, text="System Overview", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 12))
        self.summary_frame = ttk.Frame(self.dashboard_tab)
        self.summary_frame.pack(fill="x")
        self.summary_vars = {}
        for key, label in [
            ("total", "Total Visitors"),
            ("active", "Currently Checked-In"),
            ("average", "Average Visit Duration"),
            ("purpose", "Most Common Purpose"),
        ]:
            card = ttk.LabelFrame(self.summary_frame, text=label, padding=18)
            card.pack(side="left", fill="both", expand=True, padx=5)
            var = tk.StringVar(value="—")
            ttk.Label(card, textvariable=var, font=("Arial", 16, "bold")).pack()
            self.summary_vars[key] = var

        ttk.Label(
            self.dashboard_tab,
            text=("Use the tabs to add visitor records, search or filter existing records, "
                  "and create analytical charts. Visitor records are stored in data/visitors.csv."),
            wraplength=950,
            justify="left"
        ).pack(anchor="w", pady=24)

        ttk.Button(self.dashboard_tab, text="Refresh Dashboard", command=self.refresh_all).pack(anchor="w")

    def _build_form(self):
        ttk.Label(self.form_tab, text="Visitor Details", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 12)
        )
        self.form_vars = {}
        fields = [
            ("Date (YYYY-MM-DD)", "date", date.today().isoformat()),
            ("Visitor Name", "name", ""),
            ("Contact Number (10 digits)", "contact", ""),
            ("Purpose", "purpose", "Guest"),
            ("Entry Time (HH:MM)", "entry_time", ""),
            ("Exit Time (HH:MM, optional)", "exit_time", ""),
            ("Host / Notes (optional)", "notes", ""),
        ]
        for i, (label, key, default) in enumerate(fields, start=1):
            row = (i - 1) // 2
            col = ((i - 1) % 2) * 2
            ttk.Label(self.form_tab, text=label).grid(row=row + 1, column=col, sticky="w", padx=6, pady=8)
            var = tk.StringVar(value=default)
            self.form_vars[key] = var
            if key == "purpose":
                widget = ttk.Combobox(
                    self.form_tab, textvariable=var, state="readonly",
                    values=["Business", "Delivery", "Guest", "Interview", "Maintenance", "Other"], width=28
                )
            else:
                widget = ttk.Entry(self.form_tab, textvariable=var, width=32)
            widget.grid(row=row + 1, column=col + 1, sticky="ew", padx=6, pady=8)

        self.form_vars["status"] = tk.StringVar(value="Checked-In")
        ttk.Label(self.form_tab, text="Status").grid(row=5, column=0, sticky="w", padx=6, pady=8)
        ttk.Combobox(
            self.form_tab, textvariable=self.form_vars["status"], state="readonly",
            values=["Checked-In", "Checked-Out"], width=28
        ).grid(row=5, column=1, sticky="ew", padx=6, pady=8)

        button_frame = ttk.Frame(self.form_tab)
        button_frame.grid(row=6, column=0, columnspan=4, sticky="w", pady=16)
        ttk.Button(button_frame, text="Save Visitor", command=self.save_visitor).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel Edit", command=self.cancel_edit).pack(side="left", padx=5)

        for c in range(4):
            self.form_tab.columnconfigure(c, weight=1)

    def _build_records(self):
        filter_frame = ttk.LabelFrame(self.records_tab, text="Search and Filter", padding=8)
        filter_frame.pack(fill="x", pady=(0, 10))

        self.search_var = tk.StringVar()
        self.purpose_filter = tk.StringVar(value="All")
        self.status_filter = tk.StringVar(value="All")
        self.from_date_var = tk.StringVar()
        self.to_date_var = tk.StringVar()

        ttk.Label(filter_frame, text="Search name/contact/notes").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=24)
        search_entry.grid(row=0, column=1, padx=4, pady=4)
        search_entry.bind("<KeyRelease>", lambda _e: self.refresh_records())

        ttk.Label(filter_frame, text="Purpose").grid(row=0, column=2, padx=4, pady=4)
        purpose_box = ttk.Combobox(filter_frame, textvariable=self.purpose_filter, state="readonly",
                                   values=["All", "Business", "Delivery", "Guest", "Interview", "Maintenance", "Other"], width=15)
        purpose_box.grid(row=0, column=3, padx=4, pady=4)
        purpose_box.bind("<<ComboboxSelected>>", lambda _e: self.refresh_records())

        ttk.Label(filter_frame, text="Status").grid(row=0, column=4, padx=4, pady=4)
        status_box = ttk.Combobox(filter_frame, textvariable=self.status_filter, state="readonly",
                                  values=["All", "Checked-In", "Checked-Out"], width=14)
        status_box.grid(row=0, column=5, padx=4, pady=4)
        status_box.bind("<<ComboboxSelected>>", lambda _e: self.refresh_records())

        ttk.Label(filter_frame, text="From date").grid(row=1, column=0, padx=4, pady=4, sticky="w")
        ttk.Entry(filter_frame, textvariable=self.from_date_var, width=14).grid(row=1, column=1, padx=4, pady=4)
        ttk.Label(filter_frame, text="To date").grid(row=1, column=2, padx=4, pady=4)
        ttk.Entry(filter_frame, textvariable=self.to_date_var, width=14).grid(row=1, column=3, padx=4, pady=4)
        ttk.Button(filter_frame, text="Apply Dates", command=self.refresh_records).grid(row=1, column=4, padx=4, pady=4)
        ttk.Button(filter_frame, text="Reset Filters", command=self.reset_filters).grid(row=1, column=5, padx=4, pady=4)

        columns = ("id", "date", "name", "contact", "purpose", "entry", "exit", "status", "notes")
        self.tree = ttk.Treeview(self.records_tab, columns=columns, show="headings", height=16)
        headings = {
            "id": "ID", "date": "Date", "name": "Name", "contact": "Contact",
            "purpose": "Purpose", "entry": "Entry", "exit": "Exit", "status": "Status", "notes": "Notes"
        }
        widths = {"id": 45, "date": 95, "name": 135, "contact": 105, "purpose": 105,
                  "entry": 65, "exit": 65, "status": 105, "notes": 170}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_record_select)

        actions = ttk.Frame(self.records_tab)
        actions.pack(fill="x", pady=8)
        ttk.Button(actions, text="Load Selected to Edit", command=self.load_selected).pack(side="left", padx=4)
        ttk.Button(actions, text="Mark Checked-Out", command=self.checkout_selected).pack(side="left", padx=4)
        ttk.Button(actions, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(actions, text="Refresh", command=self.refresh_records).pack(side="left", padx=4)

    def _build_analytics(self):
        ttk.Label(self.analytics_tab, text="Analytics & Reports", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 12))
        ttk.Label(
            self.analytics_tab,
            text="Create charts from the visitor records. Images are saved in the reports folder.",
            wraplength=900
        ).pack(anchor="w", pady=(0, 16))
        ttk.Button(self.analytics_tab, text="Daily Visitor Volume Trend", command=self.make_trend).pack(anchor="w", pady=6)
        ttk.Button(self.analytics_tab, text="Visitor Distribution by Purpose", command=self.make_purpose).pack(anchor="w", pady=6)
        ttk.Button(self.analytics_tab, text="Peak Visiting Hours", command=self.make_peak).pack(anchor="w", pady=6)
        self.analytics_status = tk.StringVar(value="No chart generated yet.")
        ttk.Label(self.analytics_tab, textvariable=self.analytics_status).pack(anchor="w", pady=18)

    def _form_data(self):
        return {key: var.get().strip() for key, var in self.form_vars.items()}

    def save_visitor(self):
        data = self._form_data()
        errors = validate_visitor(data)
        if errors:
            messagebox.showerror("Input Validation", "\n".join(errors))
            return
        try:
            if self.selected_id is None:
                self.manager.add_visitor(data)
                messagebox.showinfo("Success", "Visitor record added successfully.")
            else:
                self.manager.update_visitor(self.selected_id, data)
                messagebox.showinfo("Success", "Visitor record updated successfully.")
            self.clear_form()
            self.refresh_all()
            self.notebook.select(self.records_tab)
        except Exception as exc:
            messagebox.showerror("Save Error", f"Could not save visitor record.\n{exc}")

    def clear_form(self):
        for key, var in self.form_vars.items():
            var.set(date.today().isoformat() if key == "date" else ("Guest" if key == "purpose" else ("Checked-In" if key == "status" else "")))
        self.selected_id = None

    def cancel_edit(self):
        self.clear_form()
        messagebox.showinfo("Form", "Edit mode cancelled.")

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_records()

    def refresh_dashboard(self):
        try:
            summary = get_summary(self.manager.get_all())
            self.summary_vars["total"].set(str(summary["total"]))
            self.summary_vars["active"].set(str(summary["active"]))
            self.summary_vars["average"].set(f'{summary["average_duration"]} min')
            self.summary_vars["purpose"].set(summary["top_purpose"])
        except Exception as exc:
            messagebox.showerror("Dashboard Error", str(exc))

    def refresh_records(self):
        try:
            records = self.manager.filter_records(
                query=self.search_var.get() if hasattr(self, "search_var") else "",
                purpose=self.purpose_filter.get() if hasattr(self, "purpose_filter") else "All",
                status=self.status_filter.get() if hasattr(self, "status_filter") else "All",
                from_date=self.from_date_var.get() if hasattr(self, "from_date_var") else "",
                to_date=self.to_date_var.get() if hasattr(self, "to_date_var") else "",
            )
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in records:
                self.tree.insert("", "end", values=(
                    row["VisitorID"], row["Date"], row["Name"], row["Contact"], row["Purpose"],
                    row["EntryTime"], row["ExitTime"], row["Status"], row["Notes"]
                ))
        except Exception as exc:
            messagebox.showerror("Filter Error", str(exc))

    def reset_filters(self):
        self.search_var.set("")
        self.purpose_filter.set("All")
        self.status_filter.set("All")
        self.from_date_var.set("")
        self.to_date_var.set("")
        self.refresh_records()

    def on_record_select(self, _event=None):
        selection = self.tree.selection()
        if selection:
            self.selected_id = int(self.tree.item(selection[0], "values")[0])

    def load_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select Record", "Please select a visitor record first.")
            return
        values = self.tree.item(selection[0], "values")
        self.selected_id = int(values[0])
        record = self.manager.get_by_id(self.selected_id)
        if not record:
            messagebox.showerror("Not Found", "Record not found.")
            return
        for key in ["date", "name", "contact", "purpose", "entry_time", "exit_time", "status", "notes"]:
            map_key = {"date": "Date", "name": "Name", "contact": "Contact", "purpose": "Purpose",
                       "entry_time": "EntryTime", "exit_time": "ExitTime", "status": "Status", "notes": "Notes"}[key]
            self.form_vars[key].set(record.get(map_key, ""))
        self.notebook.select(self.form_tab)

    def checkout_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select Record", "Please select a visitor record first.")
            return
        visitor_id = int(self.tree.item(selection[0], "values")[0])
        record = self.manager.get_by_id(visitor_id)
        if not record:
            messagebox.showerror("Not Found", "Record not found.")
            return
        if record["Status"] == "Checked-Out":
            messagebox.showinfo("Already Checked-Out", "This visitor is already checked out.")
            return
        from datetime import datetime
        record["ExitTime"] = datetime.now().strftime("%H:%M")
        record["Status"] = "Checked-Out"
        errors = validate_visitor({
            "date": record["Date"], "name": record["Name"], "contact": record["Contact"],
            "purpose": record["Purpose"], "entry_time": record["EntryTime"],
            "exit_time": record["ExitTime"], "status": record["Status"], "notes": record["Notes"]
        })
        if errors:
            messagebox.showwarning("Checkout Time", "Could not check out automatically because the current time is earlier than the entry time. Load the record and enter a valid exit time manually.")
            return
        self.manager.update_visitor(visitor_id, record, already_normalized=True)
        self.refresh_all()
        messagebox.showinfo("Success", "Visitor marked as Checked-Out.")

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select Record", "Please select a visitor record first.")
            return
        visitor_id = int(self.tree.item(selection[0], "values")[0])
        if messagebox.askyesno("Confirm Delete", f"Delete visitor record ID {visitor_id}?"):
            self.manager.delete_visitor(visitor_id)
            self.refresh_all()
            messagebox.showinfo("Deleted", "Visitor record deleted.")

    def _generate_chart(self, function, label):
        try:
            path = function(self.manager.get_all())
            self.analytics_status.set(f"{label} saved to: {path}")
            messagebox.showinfo("Report Generated", f"{label} created successfully.\n\nSaved at:\n{path}")
        except Exception as exc:
            messagebox.showerror("Analytics Error", str(exc))

    def make_trend(self):
        self._generate_chart(generate_visitor_trend, "Daily visitor volume trend")

    def make_purpose(self):
        self._generate_chart(generate_purpose_chart, "Visitor purpose distribution")

    def make_peak(self):
        self._generate_chart(generate_peak_hour_chart, "Peak visiting hours chart")


def main():
    root = tk.Tk()
    VisitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
