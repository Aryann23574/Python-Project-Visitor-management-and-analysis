import os
from collections import Counter
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def _dataframe(records):
    df = pd.DataFrame(records)
    if df.empty:
        return df
    for column in ["VisitorID", "Date", "Name", "Contact", "Purpose", "EntryTime", "ExitTime", "Status", "Notes"]:
        if column not in df.columns:
            df[column] = ""
    df["DateParsed"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
    df["EntryHour"] = pd.to_datetime(df["EntryTime"], format="%H:%M", errors="coerce").dt.hour
    entry = pd.to_datetime(df["EntryTime"], format="%H:%M", errors="coerce")
    exit_time = pd.to_datetime(df["ExitTime"], format="%H:%M", errors="coerce")
    df["Duration"] = (exit_time - entry).dt.total_seconds() / 60
    df.loc[df["Duration"] < 0, "Duration"] = np.nan
    return df

def get_summary(records):
    df = _dataframe(records)
    if df.empty:
        return {"total": 0, "active": 0, "average_duration": 0, "top_purpose": "N/A"}
    total = int(len(df))
    active = int((df["Status"] == "Checked-In").sum())
    durations = df["Duration"].dropna()
    average = int(round(float(durations.mean()))) if not durations.empty else 0
    purpose_counts = df["Purpose"].value_counts()
    top_purpose = str(purpose_counts.index[0]) if not purpose_counts.empty else "N/A"
    return {"total": total, "active": active, "average_duration": average, "top_purpose": top_purpose}

def generate_visitor_trend(records):
    df = _dataframe(records)
    path = os.path.join(REPORTS_DIR, "visitor_trend.png")
    plt.figure(figsize=(9, 5))
    if df.empty or df["DateParsed"].dropna().empty:
        plt.text(0.5, 0.5, "No visitor data available", ha="center", va="center")
        plt.axis("off")
    else:
        counts = df.groupby(df["DateParsed"].dt.date).size().sort_index()
        plt.plot([str(x) for x in counts.index], counts.values, marker="o")
        plt.title("Daily Visitor Volume Trend")
        plt.xlabel("Date")
        plt.ylabel("Number of Visitors")
        plt.xticks(rotation=35, ha="right")
        plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path

def generate_purpose_chart(records):
    df = _dataframe(records)
    path = os.path.join(REPORTS_DIR, "purpose_distribution.png")
    plt.figure(figsize=(8, 5))
    if df.empty:
        plt.text(0.5, 0.5, "No visitor data available", ha="center", va="center")
        plt.axis("off")
    else:
        counts = df["Purpose"].value_counts()
        plt.bar(counts.index.astype(str), counts.values)
        plt.title("Visitor Distribution by Purpose")
        plt.xlabel("Purpose")
        plt.ylabel("Visitor Count")
        plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path

def generate_peak_hour_chart(records):
    df = _dataframe(records)
    path = os.path.join(REPORTS_DIR, "peak_visiting_hours.png")
    plt.figure(figsize=(8, 5))
    if df.empty or df["EntryHour"].dropna().empty:
        plt.text(0.5, 0.5, "No visitor data available", ha="center", va="center")
        plt.axis("off")
    else:
        counts = df["EntryHour"].dropna().astype(int).value_counts().sort_index()
        plt.bar([f"{h:02d}:00" for h in counts.index], counts.values)
        plt.title("Peak Visiting Hours")
        plt.xlabel("Entry Hour")
        plt.ylabel("Visitor Count")
        plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path
