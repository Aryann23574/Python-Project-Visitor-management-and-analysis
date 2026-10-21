# Visitor Management & Analysis System

A Python desktop project based on the supplied project report. It uses Tkinter for the GUI, CSV for persistent storage, Pandas and NumPy for analysis, and Matplotlib for charts.

## Requirements
- Python 3.10 or newer recommended
- Tkinter (included with most standard Python installations)
- pandas, numpy, matplotlib

## Run on Windows
1. Extract the ZIP file.
2. Open the extracted `VisitorManagementSystem` folder.
3. Click the address bar in File Explorer, type `cmd`, and press Enter.
4. Install libraries:
   ```
   python -m pip install -r requirements.txt
   ```
5. Start the app:
   ```
   python main.py
   ```

## Demo steps for your teacher
1. Open Dashboard and explain total visitors, active check-ins, average duration, and common purpose.
2. Open Add / Edit Visitor. Add a visitor with date `2026-10-16`, a name, a 10-digit contact number, purpose, and entry time such as `09:30`. Keep status as Checked-In and leave exit time blank.
3. Open Visitor Records and show the saved row.
4. Select the row and click `Mark Checked-Out` (if current time is earlier than entry time, use Load Selected to Edit and enter a valid exit time manually).
5. Search for the visitor by name or contact, and try filtering by purpose/status.
6. Generate the Daily Visitor Volume Trend and Visitor Distribution by Purpose charts.
7. To demonstrate validation, try saving a record with a blank name or a contact number with fewer/more than 10 digits.

## Files
- `main.py`: Tkinter interface and event handlers
- `visitor_manager.py`: CSV storage and add/update/delete/search/filter
- `validation.py`: input validation
- `analytics.py`: Pandas/NumPy summaries and Matplotlib charts
- `data/visitors.csv`: created automatically when the app first runs
- `reports/`: generated chart images

## Notes
- The app creates `data/visitors.csv` automatically.
- Records remain saved after closing and reopening the application.
- Use valid `YYYY-MM-DD` dates and 24-hour `HH:MM` times.
- If you delete the sample CSV or want to reset the project, close the app and remove `data/visitors.csv`; it will be recreated on next launch.
