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

        # Initialize dark mode
        self.dark_mode = tk.BooleanVar()
        self.dark_mode.set(False)
        self.dark_mode.trace('w', self.toggle_theme)

        # Apply initial theme
        self.apply_theme()

        # Platform-specific window setup
        self._setup_platform_specific()

        # Center the window
        self._center_window()

        self.input_file = None
        self.output_dir = None
        self.weekly_team_leaders = {}  # Store TL selections per week: {week: {tl_name: working_days}}
        self.weekly_team_assignments = {}  # Store team assignments per week: {week: {tl_name: [team_member_names]}}
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

    def apply_theme(self):
        """Apply current theme colors to the app."""
        if self.dark_mode.get():
            # Dark mode colors
            self.colors = {
                'bg': '#2b2b2b',
                'fg': '#ffffff',
                'bg_secondary': '#3c3c3c',
                'fg_secondary': '#cccccc',
                'accent': '#4a9eff',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336',
                'button': '#404040',
                'button_hover': '#505050',
                'entry': '#404040',
                'drop_zone': '#353535'
            }
        else:
            # Light mode colors (original)
            self.colors = {
                'bg': '#f0f0f0',
                'fg': '#2c3e50',
                'bg_secondary': '#ecf0f1',
                'fg_secondary': '#7f8c8d',
                'accent': '#3498db',
                'success': '#27ae60',
                'warning': '#f39c12',
                'error': '#e74c3c',
                'button': '#95a5a6',
                'button_hover': '#34495e',
                'entry': 'white',
                'drop_zone': '#ecf0f1'
            }

        self.root.configure(bg=self.colors['bg'])

    def toggle_theme(self, *args):
        """Toggle between light and dark mode."""
        self.apply_theme()
        # Refresh UI with new colors
        if hasattr(self, 'title_label'):
            self.refresh_ui_colors()

    def refresh_ui_colors(self):
        """Refresh all UI elements with current theme colors."""
        # Update all widgets with new colors
        widgets_to_update = [
            (self.title_label, {'bg': self.colors['bg'], 'fg': self.colors['fg']}),
            (self.subtitle_label, {'bg': self.colors['bg'], 'fg': self.colors['fg_secondary']}),
            (self.drop_frame, {'bg': self.colors['drop_zone']}),
            (self.drop_label, {'bg': self.colors['drop_zone'], 'fg': self.colors['fg']}),
            (self.file_info_label, {'bg': self.colors['bg'], 'fg': self.colors['fg_secondary']}),
            (self.status_label, {'bg': self.colors['bg'], 'fg': self.colors['success']}),
            (self.footer_label, {'bg': self.colors['bg'], 'fg': self.colors['fg_secondary']})
        ]

        for widget, config in widgets_to_update:
            if widget and widget.winfo_exists():
                try:
                    widget.configure(**config)
                except:
                    pass

        # Update frames
        if hasattr(self, 'output_frame'):
            self.output_frame.configure(bg=self.colors['bg'])
            self.output_dir_frame.configure(bg=self.colors['bg'])

        # Update buttons
        if hasattr(self, 'process_btn'):
            if self.process_btn['state'] == 'normal':
                self.process_btn.configure(bg=self.colors['success'])
            else:
                self.process_btn.configure(bg=self.colors['button'])

    def setup_ui(self):
        # Dark mode toggle
        toggle_frame = tk.Frame(self.root, bg=self.colors['bg'])
        toggle_frame.pack(anchor="ne", padx=20, pady=10)

        dark_mode_checkbox = ttk.Checkbutton(toggle_frame, text="Dark Mode",
                                           variable=self.dark_mode)
        dark_mode_checkbox.pack()

        # Main title
        self.title_label = tk.Label(self.root, text="Realisierungsdatenvisualizer",
                        font=("Helvetica", 20, "bold"),
                        bg=self.colors['bg'], fg=self.colors['fg'])
        self.title_label.pack(pady=20)

        self.subtitle_label = tk.Label(self.root, text="Changing Waves Fundraiser Data Processor",
                           font=("Helvetica", 12),
                           bg=self.colors['bg'], fg=self.colors['fg_secondary'])
        self.subtitle_label.pack(pady=(0, 30))
        
        # Drag and drop area
        self.drop_frame = tk.Frame(self.root, bg=self.colors['drop_zone'], relief="solid", bd=2)
        self.drop_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # Adjust text based on drag and drop availability
        if DND_AVAILABLE:
            drop_text = "Drag & Drop CSV File Here\n\nor\n\nClick to Browse Files"
        else:
            drop_text = "Click to Browse CSV Files\n\n(Drag & Drop not available)"

        self.drop_label = tk.Label(self.drop_frame,
                                  text=drop_text,
                                  font=("Helvetica", 16),
                                  bg=self.colors['drop_zone'], fg=self.colors['fg'],
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
                                       bg=self.colors['bg'], fg=self.colors['fg_secondary'])
        self.file_info_label.pack(pady=(10, 10))

        # Output directory selection
        self.output_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.output_frame.pack(pady=(0, 20), padx=40, fill="x")

        output_label = tk.Label(self.output_frame, text="Output Directory:",
                               font=("Helvetica", 11, "bold"),
                               bg=self.colors['bg'], fg=self.colors['fg'])
        output_label.pack(anchor="w")

        self.output_dir_frame = tk.Frame(self.output_frame, bg=self.colors['bg'])
        self.output_dir_frame.pack(fill="x", pady=(5, 0))

        self.output_dir_var = tk.StringVar()
        self.output_dir_var.set("pdf_output (default)")

        self.output_entry = tk.Entry(self.output_dir_frame, textvariable=self.output_dir_var,
                                    font=("Helvetica", 10), width=40,
                                    bg=self.colors['entry'], fg=self.colors['fg'])
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_output_btn = tk.Button(self.output_dir_frame, text="Browse",
                                          font=("Helvetica", 10),
                                          bg=self.colors['button'], fg="white",
                                          padx=15, pady=5,
                                          command=self.browse_output_dir,
                                          cursor="hand2")
        self.browse_output_btn.pack(side="right")

        # Clear button for output directory
        self.clear_output_btn = tk.Button(self.output_dir_frame, text="Default",
                                         font=("Helvetica", 10),
                                         bg=self.colors['warning'], fg="white",
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
                                    bg=self.colors['bg'], fg=self.colors['success'])
        self.status_label.pack(pady=(0, 10))

        # Process button
        self.process_btn = tk.Button(self.root, text="Process CSV",
                                    font=("Helvetica", 14, "bold"),
                                    bg=self.colors['button'], fg="white",
                                    padx=30, pady=10,
                                    command=self.process_file,
                                    cursor="hand2",
                                    state="disabled")
        self.process_btn.pack(pady=20)

        # Footer
        self.footer_label = tk.Label(self.root, text="© 2025 Changing Waves",
                         font=("Helvetica", 9),
                         bg=self.colors['bg'], fg=self.colors['fg_secondary'])
        self.footer_label.pack(side="bottom", pady=10)
    
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
        self.file_info_label.config(text=f"Selected: {filename}", fg=self.colors['success'])
        self.drop_label.config(text=f"✓ {filename}\n\nClick to select a different file",
                              fg=self.colors['success'])
        self.process_btn.config(state="normal", bg=self.colors['success'])
        self.status_label.config(text="File ready for processing", fg=self.colors['success'])

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
        self.status_label.config(text="❌ Processing failed", fg=self.colors['error'])
        messagebox.showerror("Error", f"An error occurred while processing:\n\n{error_msg}")

    def update_team_assignments_ui(self, week, fundraiser, tl_checkboxes, team_assignments, all_fundraisers, assignment_frame):
        """Update the team assignment UI when TL selection changes."""
        # Clear existing assignment UI
        for widget in team_assignments[week]["frame"].winfo_children():
            widget.destroy()

        # Get current TLs for this week
        current_tls = []
        for person, checkbox_var in tl_checkboxes[week].items():
            if checkbox_var.get():
                current_tls.append(person)

        # Initialize assignments for new TLs
        if "assignments" not in team_assignments[week]:
            team_assignments[week]["assignments"] = {}

        for tl in current_tls:
            if tl not in team_assignments[week]["assignments"]:
                team_assignments[week]["assignments"][tl] = {}

        # Remove assignments for non-TLs
        tls_to_remove = []
        for tl in team_assignments[week]["assignments"].keys():
            if tl not in current_tls:
                tls_to_remove.append(tl)
        for tl in tls_to_remove:
            del team_assignments[week]["assignments"][tl]

        # Create UI for each TL's team selection
        for tl in current_tls:
            # TL section
            tl_frame = tk.LabelFrame(team_assignments[week]["frame"],
                                   text=f"Team for {tl}",
                                   font=("Helvetica", 10, "bold"),
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['fg'])
            tl_frame.pack(fill="x", padx=5, pady=5)

            # Team member checkboxes
            for person in sorted(all_fundraisers[week]):
                if person != tl:  # Don't include TL in their own team selection
                    if person not in team_assignments[week]["assignments"][tl]:
                        team_assignments[week]["assignments"][tl][person] = tk.BooleanVar()

                    member_checkbox = ttk.Checkbutton(tl_frame,
                                                    text=person,
                                                    variable=team_assignments[week]["assignments"][tl][person])
                    member_checkbox.pack(anchor="w", padx=10, pady=2)

    def show_weekly_tl_selection_dialog(self, fundraisers_by_week):
        """
        Show dialog to select team leaders per calendar week and assign team members.

        Args:
            fundraisers_by_week: Dict of {week: [fundraiser_names]}

        Returns:
            True if user confirmed selections, False if cancelled
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Weekly Team Leader Selection & Team Assignment")
        dialog.geometry("1000x700")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        # Title
        title = tk.Label(dialog, text="Weekly Team Leader Selection & Team Assignment",
                        font=("Helvetica", 16, "bold"),
                        bg=self.colors['bg'], fg=self.colors['fg'])
        title.pack(pady=20)

        instructions = tk.Label(dialog,
                               text="For each calendar week:\n1. Check TL boxes for Team Leaders\n2. Select team members for each TL\n3. Enter working days for each person",
                               font=("Helvetica", 11),
                               bg=self.colors['bg'], fg=self.colors['fg_secondary'],
                               justify="center")
        instructions.pack(pady=(0, 20))

        # Create notebook for weeks
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Store all variables
        weekly_tl_checkboxes = {}
        weekly_working_days = {}
        weekly_team_assignments = {}  # {week: {tl_name: [team_member_names]}}

        # Create tab for each week
        for week in sorted(fundraisers_by_week.keys()):
            # Create frame for this week
            week_frame = ttk.Frame(notebook)
            notebook.add(week_frame, text=f"{week}")

            # Main container
            main_container = tk.Frame(week_frame, bg=self.colors['bg_secondary'])
            main_container.pack(fill="both", expand=True, padx=10, pady=10)

            # Left side - Team Leader selection
            left_frame = tk.Frame(main_container, bg=self.colors['bg_secondary'])
            left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

            # TL selection title
            tl_title = tk.Label(left_frame, text=f"Team Leaders for {week}",
                               font=("Helvetica", 12, "bold"),
                               bg=self.colors['bg_secondary'], fg=self.colors['fg'])
            tl_title.pack(pady=(0, 10))

            # Scrollable TL frame
            tl_canvas = tk.Canvas(left_frame, bg=self.colors['bg_secondary'], height=200)
            tl_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=tl_canvas.yview)
            tl_scrollable_frame = tk.Frame(tl_canvas, bg=self.colors['bg_secondary'])

            tl_scrollable_frame.bind(
                "<Configure>",
                lambda e: tl_canvas.configure(scrollregion=tl_canvas.bbox("all"))
            )

            tl_canvas.create_window((0, 0), window=tl_scrollable_frame, anchor="nw")
            tl_canvas.configure(yscrollcommand=tl_scrollbar.set)

            tl_canvas.pack(side="left", fill="both", expand=True)
            tl_scrollbar.pack(side="right", fill="y")

            # Initialize week data
            weekly_tl_checkboxes[week] = {}
            weekly_working_days[week] = {}
            weekly_team_assignments[week] = {}

            # Team leader selection rows
            for fundraiser in sorted(fundraisers_by_week[week]):
                tl_row_frame = tk.Frame(tl_scrollable_frame, bg=self.colors['entry'], relief="solid", bd=1)
                tl_row_frame.pack(fill="x", padx=5, pady=2)

                # TL checkbox
                weekly_tl_checkboxes[week][fundraiser] = tk.BooleanVar()
                tl_checkbox = ttk.Checkbutton(tl_row_frame, text="TL",
                                            variable=weekly_tl_checkboxes[week][fundraiser],
                                            command=lambda f=fundraiser, w=week: dialog.on_tl_selection_changed(w, f, weekly_tl_checkboxes, weekly_team_assignments, fundraisers_by_week, team_assignment_frame))
                tl_checkbox.pack(side="left", padx=5)

                # Fundraiser name
                name_label = tk.Label(tl_row_frame, text=fundraiser,
                                     font=("Helvetica", 10),
                                     bg=self.colors['entry'], fg=self.colors['fg'],
                                     width=25, anchor="w")
                name_label.pack(side="left", padx=(0, 10))

                # Working days entry
                weekly_working_days[week][fundraiser] = tk.StringVar()
                weekly_working_days[week][fundraiser].set("5")  # Default to 5 days
                days_entry = tk.Entry(tl_row_frame,
                                    textvariable=weekly_working_days[week][fundraiser],
                                    font=("Helvetica", 9), width=8,
                                    bg=self.colors['bg'], fg=self.colors['fg'])
                days_entry.pack(side="right", padx=5)

                tk.Label(tl_row_frame, text="Days:", font=("Helvetica", 9),
                        bg=self.colors['entry'], fg=self.colors['fg']).pack(side="right", padx=(0, 5))

            # Right side - Team assignments
            right_frame = tk.Frame(main_container, bg=self.colors['bg_secondary'])
            right_frame.pack(side="right", fill="both", expand=True)

            # Team assignment title
            team_title = tk.Label(right_frame, text="Team Assignments",
                                 font=("Helvetica", 12, "bold"),
                                 bg=self.colors['bg_secondary'], fg=self.colors['fg'])
            team_title.pack(pady=(0, 10))

            # Team assignment frame (will be populated dynamically)
            team_assignment_frame = tk.Frame(right_frame, bg=self.colors['bg_secondary'])
            team_assignment_frame.pack(fill="both", expand=True)

            # Store reference to the team assignment frame for updates
            weekly_team_assignments[week] = {"frame": team_assignment_frame, "assignments": {}}

        # Add helper method for TL selection changes
        def on_tl_selection_changed(week, fundraiser, tl_checkboxes, team_assignments, all_fundraisers, assignment_frame):
            self.update_team_assignments_ui(week, fundraiser, tl_checkboxes, team_assignments, all_fundraisers, assignment_frame)

        # Store the helper function in dialog for access
        dialog.on_tl_selection_changed = on_tl_selection_changed

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
            self.weekly_team_assignments = {}
            self.fundraiser_working_days = {}

            for week in fundraisers_by_week.keys():
                self.weekly_team_leaders[week] = {}
                self.weekly_team_assignments[week] = {}
                self.fundraiser_working_days[week] = {}

                for fundraiser in fundraisers_by_week[week]:
                    is_tl = weekly_tl_checkboxes[week][fundraiser].get()
                    working_days = float(weekly_working_days[week][fundraiser].get())

                    if is_tl:
                        self.weekly_team_leaders[week][fundraiser] = working_days
                        # Get team assignments for this TL
                        if fundraiser in weekly_team_assignments[week]["assignments"]:
                            team_members = []
                            for member, var in weekly_team_assignments[week]["assignments"][fundraiser].items():
                                if var.get():
                                    team_members.append(member)
                            self.weekly_team_assignments[week][fundraiser] = team_members
                            print(f"DEBUG: TL {fundraiser} in {week} assigned team: {team_members}")

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
        # Initialize default return structure
        default_return = {
            "bonus": 0,
            "team_average": 0,
            "rate": 0,
            "bracket": "no bonus",
            "team_size": len(team_data) if team_data else 0,
            "team_points": 0
        }

        if not team_data or len(team_data) < 2:  # Minimum 2 team members required (TL + 1 member)
            default_return["bracket"] = "team too small"
            return default_return

        # Calculate team total points (including TL)
        team_points = 0
        team_working_days = 0

        for fundraiser, data in team_data.items():
            team_points += data["points"]
            team_working_days += data["working_days"]

        if team_working_days <= 0:
            default_return["bracket"] = "no working days"
            return default_return

        team_average = team_points / team_working_days

        # Bonus rates based on team average - adjusted for smaller teams
        if len(team_data) < 3:
            # Reduced rates for small teams (TL + 1 member)
            if team_average < 2:
                rate = 0.25
                bracket = "small team under 2er"
            elif team_average < 3:
                rate = 0.50
                bracket = "small team 2er"
            elif team_average < 5:
                rate = 1.25
                bracket = "small team 3er"
            else:
                rate = 2.25
                bracket = "small team 5er+"
        else:
            # Full rates for larger teams (3+ members)
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
        print(f"Weekly Team Assignments: {self.weekly_team_assignments}")
        print(f"Weekly working days: {self.fundraiser_working_days}")

        # Debug: Check if team leaders appear in multiple weeks
        all_tls = set()
        for week, tls in self.weekly_team_leaders.items():
            all_tls.update(tls.keys())
        print(f"All team leaders across all weeks: {all_tls}")
        for tl in all_tls:
            weeks_for_tl = [week for week, tls in self.weekly_team_leaders.items() if tl in tls]
            print(f"TL {tl} is assigned to weeks: {weeks_for_tl}")

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
                print(f"Processing TL bonuses for {week}: TLs = {list(self.weekly_team_leaders[week].keys())}")
                weekly_team_leader_bonuses[week] = {}

                for tl_name, tl_working_days in self.weekly_team_leaders[week].items():
                    if tl_name in team_data_for_week:
                        # Get specific team members for this TL
                        tl_team_data = {tl_name: team_data_for_week[tl_name]}  # Include TL in their team

                        # Add selected team members for this TL
                        if week in self.weekly_team_assignments and tl_name in self.weekly_team_assignments[week]:
                            for team_member in self.weekly_team_assignments[week][tl_name]:
                                if team_member in team_data_for_week:
                                    tl_team_data[team_member] = team_data_for_week[team_member]
                        else:
                            # If no specific team assignments, include all other fundraisers as team members (backward compatibility)
                            print(f"No specific team assignments for TL {tl_name} in {week}, using all fundraisers")
                            for fundraiser_name, fundraiser_data in team_data_for_week.items():
                                if fundraiser_name != tl_name:  # Don't duplicate the TL
                                    tl_team_data[fundraiser_name] = fundraiser_data

                        # Calculate team bonus only for selected team members
                        team_bonus_info = self.calculate_team_leader_bonus(tl_team_data, tl_working_days)
                        milestone_info = self.calculate_team_leader_milestones(len(tl_team_data))

                        # Debug: check team bonus structure
                        if not team_bonus_info or 'bracket' not in team_bonus_info:
                            print(f"Warning: Invalid team_bonus_info for {tl_name} in {week}: {team_bonus_info}")

                        print(f"TL {tl_name} team in {week}: {list(tl_team_data.keys())} (size: {len(tl_team_data)})")

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
            print(f"Final weekly_team_leader_bonuses keys: {list(weekly_team_leader_bonuses.keys())}")
            for week, bonuses in weekly_team_leader_bonuses.items():
                print(f"Week {week} has TL bonuses for: {list(bonuses.keys())}")
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