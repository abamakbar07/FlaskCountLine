import os
import pandas as pd
from pyxlsb import open_workbook

def count_pending_in_status_column(file_name, sheet_name):
    with open_workbook(file_name) as wb:
        with wb.get_sheet(sheet_name) as sheet:
            # Read the data into a pandas DataFrame
            data = []
            for row in sheet.rows():
                data.append([item.v for item in row])

            # Convert to DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])

            # Check if 'Status' column exists
            if 'Status' in df.columns:
                # Count the occurrences of 'Pending' in the 'Status' column
                pending_count = df['Status'].str.contains('Pending', case=False).sum()
            else:
                # Skip the sheet if 'Status' column doesn't exist
                print(f"Sheet '{sheet_name}' skipped (No 'Status' column).")
                pending_count = 0

            # Count the total number of rows
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
                print(f"Error processing sheet '{sheet_name}' in file '{file_name}': {e}")
        
        return total_pending, total_rows

def process_files():
    # List all files in the current directory
    files = os.listdir()
    
    # Filter out the .xlsb files
    xlsb_files = [file for file in files if file.endswith('.xlsb')]
    
    if len(xlsb_files) < 2:
        print("There should be at least two .xlsb files in the directory.")
        return None
    
    # Display available files to the user
    print("Available .xlsb files:")
    for i, file_name in enumerate(xlsb_files, 1):
        print(f"{i}. {file_name}")
    
    # Prompt user to select the first and second files
    first_file_choice = int(input("Enter the number corresponding to the first file: "))
    second_file_choice = int(input("Enter the number corresponding to the second file: "))
    
    first_file = xlsb_files[first_file_choice - 1]
    second_file = xlsb_files[second_file_choice - 1]
    
    # Get pending counts and row counts for both files
    print(f"\nProcessing file: {first_file}")
    first_file_pending_count, first_file_rows = get_pending_count_and_rows(first_file)
    
    print(f"\nProcessing file: {second_file}")
    second_file_pending_count, second_file_rows = get_pending_count_and_rows(second_file)
    
    # Calculate the difference in row count between the two files
    row_difference = abs(second_file_rows - first_file_rows)
    
    # Calculate the final result
    final_result = first_file_pending_count + second_file_pending_count + row_difference
    
    print(f"\nPending in first file: {first_file_pending_count}")
    print(f"Pending in second file: {second_file_pending_count}")
    print(f"Difference in row count: {row_difference}")
    print(f"Final result (Pending in both files + row difference): {final_result}")
    
    ask_to_restart()

def ask_to_restart():
    # Ask the user if they want to restart the process
    restart_choice = input("\nWould you like to restart the process? (yes/no): ").strip().lower()
    if restart_choice == 'yes':
        print("\nRestarting the process...\n")
        process_files()
    elif restart_choice == 'no':
        print("\nProcess completed. Exiting now...")
    else:
        print("\nInvalid input. Please enter 'yes' or 'no'.")
        ask_to_restart()

# Run the function to perform the task
process_files()
