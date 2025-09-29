import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from collections import defaultdict
import datetime
import threading
import os
import platform
import sys
import tempfile

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller bundle"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # We are in development mode
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Platform-specific imports
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    # Fallback for systems without tkinterdnd2
    DND_AVAILABLE = False
    print("Warning: Drag and drop functionality not available")
    # Create dummy classes for build compatibility
    class TkinterDnD:
        class Tk(tk.Tk):
            pass
    DND_FILES = None

class CSVFormatterApp:
    def __init__(self):
        # Initialize root window with or without drag-and-drop support
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
            
        self.root.title("Realisierungsdatenvisualizer")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # Platform-specific window setup
        self._setup_platform_specific()
        
        # Center the window
        self._center_window()
        
        self.input_file = None
        self.output_dir = None
        self.weekly_team_leaders = {}  # Store TL selections per week: {week: {fundraiser: working_days}}
        self.fundraiser_working_days = {}  # Store working days for all fundraisers per week
        self.setup_ui()
    
    def _setup_platform_specific(self):
        """Setup platform-specific configurations."""
        system = platform.system()
        
        if system == "Windows":
            # Windows-specific settings
            try:
                # Set Windows taskbar icon
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('changing_waves.csv_formatter.1.0')
            except:
                pass
            # Set Windows-specific font scaling
            self.root.tk.call('tk', 'scaling', 1.2)
        elif system == "Darwin":
            # macOS-specific settings
            try:
                # Try to center window on macOS
                self.root.eval('tk::PlaceWindow . center')
            except:
                pass
    
    def _center_window(self):
        """Center the window on screen."""
        try:
            # Try macOS method first
            self.root.eval('tk::PlaceWindow . center')
        except:
            # Fallback for Windows/Linux
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
            y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
            self.root.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        # Main title
        title = tk.Label(self.root, text="Realisierungsdatenvisualizer", 
                        font=("Helvetica", 20, "bold"), 
                        bg="#f0f0f0", fg="#2c3e50")
        title.pack(pady=20)
        
        subtitle = tk.Label(self.root, text="Changing Waves Fundraiser Data Processor", 
                           font=("Helvetica", 12), 
                           bg="#f0f0f0", fg="#7f8c8d")
        subtitle.pack(pady=(0, 30))
        
        # Drag and drop area
        self.drop_frame = tk.Frame(self.root, bg="#ecf0f1", relief="solid", bd=2)
        self.drop_frame.pack(pady=20, padx=40, fill="both", expand=True)
        
        # Adjust text based on drag and drop availability
        if DND_AVAILABLE:
            drop_text = "Drag & Drop CSV File Here\n\nor\n\nClick to Browse Files"
        else:
            drop_text = "Click to Browse CSV Files\n\n(Drag & Drop not available)"
            
        self.drop_label = tk.Label(self.drop_frame, 
                                  text=drop_text, 
                                  font=("Helvetica", 16), 
                                  bg="#ecf0f1", fg="#34495e",
                                  cursor="hand2")
        self.drop_label.pack(expand=True)
        
        # Configure drag and drop if available
        if DND_AVAILABLE:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_label.bind("<Button-1>", self.browse_file)
        
        # File info label
        self.file_info_label = tk.Label(self.root, text="No file selected",
                                       font=("Helvetica", 10),
                                       bg="#f0f0f0", fg="#7f8c8d")
        self.file_info_label.pack(pady=(10, 10))

        # Output directory selection
        output_frame = tk.Frame(self.root, bg="#f0f0f0")
        output_frame.pack(pady=(0, 20), padx=40, fill="x")

        output_label = tk.Label(output_frame, text="Output Directory:",
                               font=("Helvetica", 11, "bold"),
                               bg="#f0f0f0", fg="#2c3e50")
        output_label.pack(anchor="w")

        output_dir_frame = tk.Frame(output_frame, bg="#f0f0f0")
        output_dir_frame.pack(fill="x", pady=(5, 0))

        self.output_dir_var = tk.StringVar()
        self.output_dir_var.set("pdf_output (default)")

        self.output_entry = tk.Entry(output_dir_frame, textvariable=self.output_dir_var,
                                    font=("Helvetica", 10), width=40,
                                    bg="white", fg="#2c3e50")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_output_btn = tk.Button(output_dir_frame, text="Browse",
                                          font=("Helvetica", 10),
                                          bg="#95a5a6", fg="white",
                                          padx=15, pady=5,
                                          command=self.browse_output_dir,
                                          cursor="hand2")
        self.browse_output_btn.pack(side="right")

        # Clear button for output directory
        self.clear_output_btn = tk.Button(output_dir_frame, text="Default",
                                         font=("Helvetica", 10),
                                         bg="#e67e22", fg="white",
                                         padx=15, pady=5,
                                         command=self.reset_output_dir,
                                         cursor="hand2")
        self.clear_output_btn.pack(side="right", padx=(0, 5))
        
        # Progress bar (initially hidden)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, mode='indeterminate', 
                                           length=400)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Ready to process files", 
                                    font=("Helvetica", 10), 
                                    bg="#f0f0f0", fg="#27ae60")
        self.status_label.pack(pady=(0, 10))
        
        # Process button
        self.process_btn = tk.Button(self.root, text="Process CSV", 
                                    font=("Helvetica", 14, "bold"),
                                    bg="#3498db", fg="white", 
                                    padx=30, pady=10,
                                    command=self.process_file,
                                    cursor="hand2",
                                    state="disabled")
        self.process_btn.pack(pady=20)
        
        # Footer
        footer = tk.Label(self.root, text="© 2025 Changing Waves", 
                         font=("Helvetica", 9), 
                         bg="#f0f0f0", fg="#95a5a6")
        footer.pack(side="bottom", pady=10)
    
    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.csv'):
                self.set_input_file(file_path)
            else:
                messagebox.showerror("Invalid File", "Please select a CSV file.")
    
    def browse_file(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.set_input_file(file_path)
    
    def set_input_file(self, file_path):
        self.input_file = file_path
        filename = os.path.basename(file_path)
        self.file_info_label.config(text=f"Selected: {filename}", fg="#27ae60")
        self.drop_label.config(text=f"✓ {filename}\n\nClick to select a different file",
                              fg="#27ae60")
        self.process_btn.config(state="normal", bg="#27ae60")
        self.status_label.config(text="File ready for processing", fg="#27ae60")

    def browse_output_dir(self):
        directory = filedialog.askdirectory(
            title="Select Output Directory for PDF Files"
        )
        if directory:
            self.output_dir = directory
            self.output_dir_var.set(directory)

    def reset_output_dir(self):
        self.output_dir = None
        self.output_dir_var.set("pdf_output (default)")
    
    def show_processing(self):
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.start(10)
        self.process_btn.config(state="disabled", bg="#95a5a6", text="Processing...")
        self.status_label.config(text="Processing CSV file...", fg="#f39c12")
        self.root.update()
    
    def hide_processing(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.process_btn.config(state="normal", bg="#27ae60", text="Process CSV")
        self.root.update()
    
    def process_file(self):
        if not self.input_file:
            messagebox.showerror("No File", "Please select a CSV file first.")
            return
        
        # Run processing in separate thread
        thread = threading.Thread(target=self.run_processing)
        thread.daemon = True
        thread.start()
    
    def run_processing(self):
        try:
            self.root.after(0, self.show_processing)

            # Get output filename (Windows-safe path handling)
            input_dir = os.path.dirname(self.input_file)
            input_name = os.path.splitext(os.path.basename(self.input_file))[0]
            output_file = os.path.normpath(os.path.join(input_dir, f"{input_name}_formatted.csv"))

            # Determine PDF output directory
            pdf_output_dir = None
            if self.output_dir:
                pdf_output_dir = self.output_dir
            else:
                # Use directory name from entry field if it's not the default
                dir_name = self.output_dir_var.get().strip()
                if dir_name and dir_name != "pdf_output (default)":
                    pdf_output_dir = os.path.join(input_dir, dir_name)

            # Process the file
            result = self.format_csv(self.input_file, output_file, pdf_output_dir)

            self.root.after(0, lambda: self.processing_complete(result, output_file))

        except Exception as e:
            error_message = str(e)
            self.root.after(0, lambda: self.processing_error(error_message))
    
    def processing_complete(self, result, output_file):
        self.hide_processing()
        self.status_label.config(text=f"✓ Processing complete! {result['rows']} rows processed", 
                                fg="#27ae60")
        
        # Generate success message
        success_msg = f"CSV processed successfully!\n\nRows processed: {result['rows']}\nOutput saved to: {os.path.basename(output_file)}"

        # Add PDF generation info if applicable
        if 'pdf_files' in result and result['pdf_files']:
            success_msg += f"\n\nPDF files generated: {len(result['pdf_files'])}"
            # Show the actual PDF output directory path
            if result['pdf_files']:
                pdf_dir = os.path.dirname(result['pdf_files'][0])
                success_msg += f"\nLocation: {pdf_dir}"

        messagebox.showinfo("Success", success_msg)
    
    def processing_error(self, error_msg):
        self.hide_processing()
        self.status_label.config(text="❌ Processing failed", fg="#e74c3c")
        messagebox.showerror("Error", f"An error occurred while processing:\n\n{error_msg}")

    def show_weekly_tl_selection_dialog(self, fundraisers_by_week):
        """
        Show dialog to select team leaders per calendar week and input working days.

        Args:
            fundraisers_by_week: Dict of {week: [fundraiser_names]}

        Returns:
            True if user confirmed selections, False if cancelled
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Weekly Team Leader Selection & Working Days")
        dialog.geometry("800x600")
        dialog.configure(bg="#f0f0f0")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        # Title
        title = tk.Label(dialog, text="Weekly Team Leader Selection & Working Days",
                        font=("Helvetica", 16, "bold"),
                        bg="#f0f0f0", fg="#2c3e50")
        title.pack(pady=20)

        instructions = tk.Label(dialog,
                               text="For each calendar week:\n1. Check TL boxes for Team Leaders\n2. Enter working days for each fundraiser",
                               font=("Helvetica", 11),
                               bg="#f0f0f0", fg="#7f8c8d",
                               justify="center")
        instructions.pack(pady=(0, 20))

        # Create notebook for weeks
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Store all variables
        weekly_checkboxes = {}
        weekly_working_days = {}

        # Create tab for each week
        for week in sorted(fundraisers_by_week.keys()):
            # Create frame for this week
            week_frame = ttk.Frame(notebook)
            notebook.add(week_frame, text=f"{week}")

            # Scrollable frame for this week's fundraisers
            canvas = tk.Canvas(week_frame, bg="#f9f9f9")
            scrollbar = ttk.Scrollbar(week_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Week header
            week_title = tk.Label(scrollable_frame, text=f"Calendar Week: {week}",
                                font=("Helvetica", 14, "bold"),
                                bg="#f9f9f9", fg="#2c3e50")
            week_title.pack(pady=10)

            # Headers
            header_frame = tk.Frame(scrollable_frame, bg="#f9f9f9")
            header_frame.pack(fill="x", padx=20, pady=5)

            tk.Label(header_frame, text="TL", font=("Helvetica", 10, "bold"),
                    bg="#f9f9f9", width=5).pack(side="left", padx=(0, 10))
            tk.Label(header_frame, text="Fundraiser Name", font=("Helvetica", 10, "bold"),
                    bg="#f9f9f9", width=30, anchor="w").pack(side="left", padx=(0, 10))
            tk.Label(header_frame, text="Working Days", font=("Helvetica", 10, "bold"),
                    bg="#f9f9f9").pack(side="left")

            # Initialize week data
            weekly_checkboxes[week] = {}
            weekly_working_days[week] = {}

            # Create rows for each fundraiser in this week
            for fundraiser in sorted(fundraisers_by_week[week]):
                row_frame = tk.Frame(scrollable_frame, bg="white", relief="solid", bd=1)
                row_frame.pack(fill="x", padx=20, pady=2)

                # Team Leader checkbox
                weekly_checkboxes[week][fundraiser] = tk.BooleanVar()
                checkbox = ttk.Checkbutton(row_frame,
                                         variable=weekly_checkboxes[week][fundraiser])
                checkbox.pack(side="left", padx=(5, 15))

                # Fundraiser name
                name_label = tk.Label(row_frame, text=fundraiser,
                                     font=("Helvetica", 10),
                                     bg="white", width=30, anchor="w")
                name_label.pack(side="left", padx=(0, 10))

                # Working days entry
                weekly_working_days[week][fundraiser] = tk.StringVar()
                weekly_working_days[week][fundraiser].set("5")  # Default to 5 days
                days_entry = tk.Entry(row_frame,
                                    textvariable=weekly_working_days[week][fundraiser],
                                    font=("Helvetica", 10), width=10)
                days_entry.pack(side="left", padx=5)

        # Result storage
        result = {"confirmed": False}

        def on_confirm():
            # Validate all inputs
            for week, fundraisers_vars in weekly_working_days.items():
                for fundraiser, days_var in fundraisers_vars.items():
                    try:
                        days = float(days_var.get())
                        if days <= 0:
                            messagebox.showerror("Invalid Input",
                                               f"Working days for {fundraiser} in {week} must be greater than 0")
                            return
                    except ValueError:
                        messagebox.showerror("Invalid Input",
                                           f"Please enter a valid number for working days for {fundraiser} in {week}")
                        return

            # Store all selections
            self.weekly_team_leaders = {}
            self.fundraiser_working_days = {}

            for week in fundraisers_by_week.keys():
                self.weekly_team_leaders[week] = {}
                self.fundraiser_working_days[week] = {}

                for fundraiser in fundraisers_by_week[week]:
                    is_tl = weekly_checkboxes[week][fundraiser].get()
                    working_days = float(weekly_working_days[week][fundraiser].get())

                    if is_tl:
                        self.weekly_team_leaders[week][fundraiser] = working_days

                    self.fundraiser_working_days[week][fundraiser] = working_days

            result["confirmed"] = True
            dialog.destroy()

        def on_cancel():
            result["confirmed"] = False
            dialog.destroy()

        # Buttons
        button_frame = tk.Frame(dialog, bg="#f0f0f0")
        button_frame.pack(side="bottom", pady=20)

        cancel_btn = tk.Button(button_frame, text="Cancel",
                              font=("Helvetica", 12),
                              bg="#95a5a6", fg="white",
                              padx=20, pady=8,
                              command=on_cancel)
        cancel_btn.pack(side="left", padx=(0, 10))

        confirm_btn = tk.Button(button_frame, text="Confirm",
                               font=("Helvetica", 12, "bold"),
                               bg="#27ae60", fg="white",
                               padx=20, pady=8,
                               command=on_confirm)
        confirm_btn.pack(side="right")

        # Wait for dialog to close
        dialog.wait_window()

        return result["confirmed"]

    def calculate_regular_fundraiser_payout(self, points, working_days):
        """
        Calculate payout for regular fundraiser based on points and working days.

        Args:
            points: Total points earned
            working_days: Number of days worked

        Returns:
            Dictionary with payout details
        """
        if working_days <= 0:
            return {"daily_average": 0, "payout": 0, "rate": "N/A"}

        daily_average = points / working_days

        # Payment rates based on daily average
        if daily_average < 2:
            rate = 3.95
            bracket = "under 2er"
        elif daily_average < 3:
            rate = 10
            bracket = "2er"
        elif daily_average < 5:
            rate = 15
            bracket = "3er"
        elif daily_average < 7:
            rate = 20
            bracket = "5er"
        else:
            rate = 30
            bracket = "7er+"

        payout = points * rate

        return {
            "daily_average": daily_average,
            "payout": payout,
            "rate": rate,
            "bracket": bracket
        }

    def calculate_team_leader_bonus(self, team_data, tl_working_days):
        """
        Calculate team leader bonus based on team performance.

        Args:
            team_data: Dictionary with fundraiser data for the team
            tl_working_days: Team leader's working days

        Returns:
            Dictionary with bonus details
        """
        if not team_data or len(team_data) < 3:  # Minimum 3 team members required
            return {"bonus": 0, "team_average": 0, "rate": "N/A", "team_size": len(team_data)}

        # Calculate team total points (including TL)
        team_points = 0
        team_working_days = 0

        for fundraiser, data in team_data.items():
            team_points += data["points"]
            team_working_days += data["working_days"]

        if team_working_days <= 0:
            return {"bonus": 0, "team_average": 0, "rate": "N/A", "team_size": len(team_data)}

        team_average = team_points / team_working_days

        # Bonus rates based on team average
        if team_average < 2:
            rate = 0.50
            bracket = "under 2er"
        elif team_average < 3:
            rate = 1.00
            bracket = "2er"
        elif team_average < 5:
            rate = 2.50
            bracket = "3er"
        else:
            rate = 4.50
            bracket = "5er+"

        bonus = team_points * rate

        return {
            "bonus": bonus,
            "team_average": team_average,
            "rate": rate,
            "bracket": bracket,
            "team_size": len(team_data),
            "team_points": team_points
        }

    def calculate_team_leader_milestones(self, team_size):
        """
        Calculate milestone bonuses for team leaders based on team size.

        Args:
            team_size: Number of people in the team

        Returns:
            Dictionary with milestone bonus amounts
        """
        if team_size < 4:
            communication_coach = 5
            communication_office = 5
            external_presence = 5
            material_responsibility = 5
        elif team_size < 6:
            communication_coach = 20
            communication_office = 20
            external_presence = 20
            material_responsibility = 20
        else:
            communication_coach = 30
            communication_office = 30
            external_presence = 30
            material_responsibility = 30

        return {
            "communication_coach": communication_coach,
            "communication_office": communication_office,
            "external_presence": external_presence,
            "material_responsibility": material_responsibility,
            "total_possible": communication_coach + communication_office + external_presence + material_responsibility,
            "team_size_bracket": f"{team_size} persons"
        }

    # CSV Processing Logic (from original script)
    def calculate_points(self, age, interval, amount_yearly):
        age = int(age)
        amount = float(amount_yearly)
        
        if age < 25:
            return 0.5
        
        if age < 30:
            return 0.5 if interval.lower() == 'monthly' else 1.0
        
        base_points = 0
        if amount >= 360:
            if interval.lower() == 'yearly':
                base_points = 5
            elif 'half' in interval.lower():
                base_points = 4
            else:
                base_points = 3
        elif amount >= 240:
            if interval.lower() == 'yearly':
                base_points = 4
            elif 'half' in interval.lower():
                base_points = 3
            else:
                base_points = 2
        elif amount >= 180:
            if interval.lower() == 'yearly':
                base_points = 3
            elif 'half' in interval.lower():
                base_points = 2.5
            else:
                base_points = 1.5
        elif amount >= 120:
            if interval.lower() == 'yearly':
                base_points = 2
            elif 'half' in interval.lower():
                base_points = 1.5
            else:
                base_points = 1
        else:
            base_points = 1
        
        if age >= 40:
            base_points += 1
        
        return base_points
    
    def calculate_bonus_eligibility(self, fundraiser_data):
        # Filter for cancellation and active/billable status only
        relevant_donors = fundraiser_data[
            fundraiser_data['status_agency'].isin(['cancellation', 'active', 'billable', 'approved', 'conditionally approved'])
        ]
        
        total_donors = len(relevant_donors)
        # Count both 'approved' and 'conditionally approved' as approved
        approved_donors = len(relevant_donors[
            relevant_donors['status_agency'].isin(['approved', 'conditionally approved'])
        ])
        
        if total_donors == 0:
            return 'not-eligible'
        
        approval_rate = approved_donors / total_donors
        return 'eligible' if approval_rate >= 0.7 else 'not-eligible'
    
    def format_csv(self, input_file, output_file, pdf_output_dir=None):
        # Handle file path encoding issues on Windows and other platforms
        encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'iso-8859-1', 'latin1']
        df = None

        for encoding in encodings:
            try:
                # Read CSV, skipping the first 2 header rows
                df = pd.read_csv(input_file, sep=';', encoding=encoding, skiprows=2)
                print(f"Successfully read file with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if encoding == encodings[-1]:  # Last encoding attempt
                    raise Exception(f"Could not read file with any supported encoding. Error: {e}")
                continue

        if df is None:
            raise Exception("Could not read the CSV file with any supported encoding")

        # Extract fundraisers by calendar week for TL selection
        df_temp = df.copy()
        df_temp.columns = df_temp.columns.str.strip()
        df_temp = df_temp[~df_temp['Fundraiser Name'].str.contains('Subtotal|Total', case=False, na=False)]
        df_temp['Fundraiser Name'] = df_temp['Fundraiser Name'].ffill()
        df_temp['Calendar week'] = df_temp['Calendar week'].ffill()

        # Group fundraisers by calendar week
        fundraisers_by_week = {}
        for _, row in df_temp.iterrows():
            if pd.notna(row['Fundraiser Name']) and pd.notna(row['Calendar week']):
                week = row['Calendar week']
                fundraiser = row['Fundraiser Name']

                if week not in fundraisers_by_week:
                    fundraisers_by_week[week] = set()
                fundraisers_by_week[week].add(fundraiser)

        # Convert sets to lists for dialog
        for week in fundraisers_by_week:
            fundraisers_by_week[week] = list(fundraisers_by_week[week])

        # Show weekly TL selection dialog synchronously
        result = []
        def show_dialog():
            result.append(self.show_weekly_tl_selection_dialog(fundraisers_by_week))

        self.root.after_idle(show_dialog)

        # Wait for dialog to complete
        while not result:
            self.root.update()

        if not result[0]:
            raise Exception("Team Leader selection was cancelled")

        print(f"Weekly Team Leaders: {self.weekly_team_leaders}")
        print(f"Weekly working days: {self.fundraiser_working_days}")

        # Debug: print unique calendar weeks in the data
        print(f"Calendar weeks in data: {sorted(df['Calendar week'].dropna().unique())}")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Filter out subtotal and total rows
        df = df[~df['Fundraiser Name'].str.contains('Subtotal|Total', case=False, na=False)]
        
        # Filter out rows where Public RefID is NaN or empty
        df = df[df['Public RefID'].notna()]
        df = df[df['Public RefID'] != '']
        
        # Forward fill fundraiser information
        df['Fundraiser ID'] = df['Fundraiser ID'].ffill()
        df['Fundraiser Name'] = df['Fundraiser Name'].ffill()
        df['Calendar week'] = df['Calendar week'].ffill()
        df['Billing group'] = df['Billing group'].ffill()
        
        # Preserve original formatting for Fundraiser ID
        df['Fundraiser ID'] = df['Fundraiser ID'].astype(str).str.replace('.0', '').str.zfill(5)
        
        # Extract calendar week number for sorting
        df['KW_num'] = df['Calendar week'].str.extract(r'(\d+)').fillna(0).astype(int)
        
        # Calculate points for each donor
        df['points'] = df.apply(lambda row: self.calculate_points(
            row['Age'], row['Interval'], row['Amount Yearly']
        ), axis=1)
        
        # Group by fundraiser to calculate bonus eligibility
        fundraiser_bonus = {}
        for fundraiser_id in df['Fundraiser ID'].unique():
            if pd.notna(fundraiser_id):
                fundraiser_data = df[df['Fundraiser ID'] == fundraiser_id]
                fundraiser_bonus[fundraiser_id] = self.calculate_bonus_eligibility(fundraiser_data)
        
        # Add bonus status to dataframe
        df['bonus_status'] = df['Fundraiser ID'].map(fundraiser_bonus)
        
        # Sort data
        df_sorted = df.sort_values(['KW_num', 'Fundraiser Name', 'Billing group'])
        
        # Select only required columns
        required_columns = [
            'Fundraiser ID', 'Fundraiser Name', 'Calendar week',
            'Public RefID', 'Age', 'Interval', 'Amount Yearly', 'status_agency',
            'points', 'bonus_status'
        ]
        
        # Calculate payment data for all fundraisers per week
        weekly_fundraiser_payments = {}
        weekly_team_leader_bonuses = {}

        # Process each week separately
        for week in sorted(df_sorted['Calendar week'].dropna().unique()):
            if pd.isna(week) or week == '':
                continue

            week_data = df_sorted[df_sorted['Calendar week'] == week]

            # Skip if no working days data for this week
            if week not in self.fundraiser_working_days:
                print(f"Warning: No working days data for week {week}")
                continue

            weekly_fundraiser_payments[week] = {}
            team_data_for_week = {}

            # Calculate individual fundraiser payouts for this week
            for fundraiser_name in week_data['Fundraiser Name'].dropna().unique():
                if pd.notna(fundraiser_name) and fundraiser_name in self.fundraiser_working_days[week]:
                    fundraiser_week_data = week_data[week_data['Fundraiser Name'] == fundraiser_name]
                    non_cancelled_data = fundraiser_week_data[fundraiser_week_data['status_agency'] != 'cancellation']
                    week_points = non_cancelled_data['points'].sum()
                    working_days = self.fundraiser_working_days[week][fundraiser_name]

                    # Calculate regular payout
                    payout_info = self.calculate_regular_fundraiser_payout(week_points, working_days)

                    # Debug: check payout_info structure
                    if not payout_info or 'bracket' not in payout_info:
                        print(f"Warning: Invalid payout_info for {fundraiser_name} in {week}: {payout_info}")

                    weekly_fundraiser_payments[week][fundraiser_name] = {
                        "points": week_points,
                        "working_days": working_days,
                        "payout": payout_info
                    }

                    team_data_for_week[fundraiser_name] = {
                        "points": week_points,
                        "working_days": working_days
                    }

            # Calculate team leader bonuses for this week
            if week in self.weekly_team_leaders and self.weekly_team_leaders[week]:
                weekly_team_leader_bonuses[week] = {}

                for tl_name, tl_working_days in self.weekly_team_leaders[week].items():
                    if tl_name in team_data_for_week:
                        # Calculate team bonus (all fundraisers in this week are considered team members)
                        team_bonus_info = self.calculate_team_leader_bonus(team_data_for_week, tl_working_days)
                        milestone_info = self.calculate_team_leader_milestones(len(team_data_for_week))

                        # Debug: check team bonus structure
                        if not team_bonus_info or 'bracket' not in team_bonus_info:
                            print(f"Warning: Invalid team_bonus_info for {tl_name} in {week}: {team_bonus_info}")

                        weekly_team_leader_bonuses[week][tl_name] = {
                            "team_bonus": team_bonus_info,
                            "milestones": milestone_info
                        }

        # Create output dataframe with subtotals and payment info
        final_rows = []

        # Process data grouped by KW and Fundraiser
        for kw_num in sorted(df_sorted['KW_num'].dropna().unique()):
            if kw_num == 0:
                continue

            # Fix calendar week formatting for weeks 1-12
            if kw_num <= 12:
                kw_str = f"KW{int(kw_num)}"
                # Match calendar week data properly for weeks 1-12
                kw_data = df_sorted[
                    (df_sorted['Calendar week'].str.contains(f'KW{int(kw_num)}', na=False)) |
                    (df_sorted['Calendar week'].str.contains(f'{int(kw_num)}/2025', na=False))
                ]
            else:
                kw_str = f"{int(kw_num)}/2025"
                kw_data = df_sorted[df_sorted['Calendar week'] == kw_str]

            for fundraiser_name in sorted(kw_data['Fundraiser Name'].dropna().unique()):
                fundraiser_data = kw_data[kw_data['Fundraiser Name'] == fundraiser_name]

                # Add all individual entries
                for i, (_, row) in enumerate(fundraiser_data.iterrows()):
                    row_dict = row[required_columns].to_dict()
                    row_dict['bonus_status'] = ''
                    final_rows.append(row_dict)

                # Add subtotal row
                # Exclude cancelled donors from total points calculation
                non_cancelled_data = fundraiser_data[fundraiser_data['status_agency'] != 'cancellation']
                total_points = non_cancelled_data['points'].sum()
                bonus_status = fundraiser_data['bonus_status'].iloc[0]

                subtotal_row = {
                    'Fundraiser ID': '',
                    'Fundraiser Name': '',
                    'Calendar week': '',
                    'Public RefID': '',
                    'Age': '',
                    'Interval': '',
                    'Amount Yearly': '',
                    'status_agency': '',
                    'points': f"Total: {total_points}",
                    'bonus_status': bonus_status
                }
                final_rows.append(subtotal_row)

                # Add payment info for this fundraiser if we have weekly data
                # Use the original calendar week from the data, not kw_str
                original_week = fundraiser_data['Calendar week'].iloc[0]
                if original_week in weekly_fundraiser_payments and fundraiser_name in weekly_fundraiser_payments[original_week]:
                    payment_info = weekly_fundraiser_payments[original_week][fundraiser_name]

                    # Debug: check if payment_info has the expected structure
                    if 'payout' in payment_info and payment_info['payout']:
                        payout_data = payment_info['payout']
                        payout_row = {
                            'Fundraiser ID': '',
                            'Fundraiser Name': '',
                            'Calendar week': '',
                            'Public RefID': f"Payout ({payout_data.get('bracket', 'unknown')} avg)",
                            'Age': '',
                            'Interval': f"{payment_info.get('working_days', 0)} days",
                            'Amount Yearly': f"€{payout_data.get('payout', 0):.2f}",
                            'status_agency': f"Rate: €{payout_data.get('rate', 0)}",
                            'points': f"Avg: {payout_data.get('daily_average', 0):.2f}",
                            'bonus_status': ''
                        }
                        final_rows.append(payout_row)
                    else:
                        print(f"Warning: Invalid payment_info structure for {fundraiser_name} in {original_week}: {payment_info}")

        # Add weekly team leader bonus summary at the end
        if weekly_team_leader_bonuses:
            final_rows.append({col: '' for col in required_columns})  # Empty separator row

            final_rows.append({
                'Fundraiser ID': '',
                'Fundraiser Name': 'TEAM LEADER BONUSES (BY WEEK)',
                'Calendar week': '',
                'Public RefID': '',
                'Age': '',
                'Interval': '',
                'Amount Yearly': '',
                'status_agency': '',
                'points': '',
                'bonus_status': ''
            })

            for week in sorted(weekly_team_leader_bonuses.keys()):
                # Week header
                final_rows.append({
                    'Fundraiser ID': '',
                    'Fundraiser Name': f"--- {week} ---",
                    'Calendar week': '',
                    'Public RefID': '',
                    'Age': '',
                    'Interval': '',
                    'Amount Yearly': '',
                    'status_agency': '',
                    'points': '',
                    'bonus_status': ''
                })

                for tl_name, bonus_info in weekly_team_leader_bonuses[week].items():
                    team_bonus = bonus_info['team_bonus']
                    milestones = bonus_info['milestones']

                    # Team performance bonus
                    final_rows.append({
                        'Fundraiser ID': '',
                        'Fundraiser Name': tl_name,
                        'Calendar week': 'Team Bonus',
                        'Public RefID': f"Team avg: {team_bonus.get('team_average', 0):.2f}",
                        'Age': f"{team_bonus.get('team_size', 0)} persons",
                        'Interval': f"€{team_bonus.get('rate', 0)}/point",
                        'Amount Yearly': f"€{team_bonus.get('bonus', 0):.2f}",
                        'status_agency': team_bonus.get('bracket', 'unknown'),
                        'points': f"{team_bonus.get('team_points', 0):.1f} pts",
                        'bonus_status': ''
                    })

                    # Milestone bonuses (potential)
                    final_rows.append({
                        'Fundraiser ID': '',
                        'Fundraiser Name': '',
                        'Calendar week': 'Milestones',
                        'Public RefID': f"Max potential: €{milestones.get('total_possible', 0)}",
                        'Age': milestones.get('team_size_bracket', 'unknown'),
                        'Interval': f"Coach: €{milestones.get('communication_coach', 0)}",
                        'Amount Yearly': f"Office: €{milestones.get('communication_office', 0)}",
                        'status_agency': f"External: €{milestones.get('external_presence', 0)}",
                        'points': f"Material: €{milestones.get('material_responsibility', 0)}",
                        'bonus_status': ''
                    })
        
        # Create final dataframe
        final_df = pd.DataFrame(final_rows)
        
        # Save with custom headers
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        header_lines = [
            f"WoVi_CW_Formatted_{current_date};" + ";" * (len(required_columns) - 1),
            ";" * len(required_columns)
        ]
        
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            # Write headers
            for line in header_lines:
                f.write(line + '\n')
            
            # Write column headers
            f.write(';'.join(required_columns) + '\n')
            
            # Write data
            for _, row in final_df.iterrows():
                row_values = []
                for col in required_columns:
                    value = row[col]
                    if pd.isna(value) or value == '':
                        row_values.append('')
                    else:
                        # Format numeric values
                        if col == 'points' and isinstance(value, (int, float)) and not str(value).startswith('Total:'):
                            row_values.append(str(value).replace('.', ','))
                        else:
                            row_values.append(str(value))
                f.write(';'.join(row_values) + '\n')
        
        # Generate PDF files
        pdf_files = []
        try:
            from pdf_generator import generate_all_pdf_files
            pdf_files = generate_all_pdf_files(output_file, pdf_output_dir)
            print(f"Generated {len(pdf_files)} PDF files")
        except Exception as e:
            print(f"Error generating PDF files: {e}")

        return {"rows": len(final_df), "pdf_files": pdf_files}
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CSVFormatterApp()
    app.run()