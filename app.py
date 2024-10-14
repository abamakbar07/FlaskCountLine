import os
from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from pyxlsb import open_workbook
import time
from flask import jsonify

app = Flask(__name__)

# Global log and progress variables
logs = []
progress = 0

# Your existing functions
def count_pending_in_status_column(file_name, sheet_name):
    with open_workbook(file_name) as wb:
        with wb.get_sheet(sheet_name) as sheet:
            data = []
            for row in sheet.rows():
                data.append([item.v for item in row])

            df = pd.DataFrame(data[1:], columns=data[0])

            if 'Status' in df.columns:
                pending_count = df['Status'].str.contains('Pending', case=False).sum()
            else:
                pending_count = 0

            total_rows = len(df)
    
    return pending_count, total_rows

def get_pending_count_and_rows(file_name):
    with open_workbook(file_name) as wb:
        sheet_names = wb.sheets
        total_pending = 0
        total_rows = 0
        
        for sheet_name in sheet_names:
            try:
                pending_count, rows = count_pending_in_status_column(file_name, sheet_name)
                total_pending += pending_count
                total_rows += rows
            except Exception as e:
                print(f"Error processing sheet '{sheet_name}': {e}")
        
        return total_pending, total_rows


@app.route("/", methods=["GET", "POST"])
def choose_files():
    upload_folder = os.path.join(os.getcwd(), "uploads")
    xlsb_files = [file for file in os.listdir(upload_folder) if file.endswith('.xlsb')]

    if request.method == "POST":
        first_file = request.form.get("first_file")
        second_file = request.form.get("second_file")

        if not (first_file and second_file):
            return jsonify({"error": "Please select both files before submitting."})

        # Process the files and return the result
        first_file_path = os.path.join(upload_folder, first_file)
        second_file_path = os.path.join(upload_folder, second_file)

        result = process_files(first_file_path, second_file_path)
        return jsonify({"success": True, "result": result})

    return render_template("choose_files.html", xlsb_files=xlsb_files)


def process_files(first_file, second_file):
    upload_folder = os.path.join(os.getcwd(), "uploads")
    xlsb_files = [file for file in os.listdir(upload_folder) if file.endswith('.xlsb')]
    
    if request.method == "POST":
        # Capture the selected files from the form
        first_file = request.form.get("first_file")
        second_file = request.form.get("second_file")

        if not (first_file and second_file):
            return "Please select both files before submitting."

        # Process the files
        first_file_path = os.path.join(upload_folder, first_file)
        second_file_path = os.path.join(upload_folder, second_file)

        first_file_pending_count, first_file_rows = get_pending_count_and_rows(first_file_path)
        second_file_pending_count, second_file_rows = get_pending_count_and_rows(second_file_path)

        row_difference = abs(second_file_rows - first_file_rows)
        final_result = first_file_pending_count + second_file_pending_count + row_difference

    return f"Processed {first_file} and {second_file} result is {final_result}"

@app.route("/logs")
def get_logs():
    """Return the current logs and progress."""
    return jsonify({
        "logs": logs,
        "progress": progress
    })

# Run the app
if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)
