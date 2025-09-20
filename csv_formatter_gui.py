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

# Platform-specific imports
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    # Fallback for systems without tkinterdnd2
    DND_AVAILABLE = False
    print("Warning: Drag and drop functionality not available")

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
        self.file_info_label.pack(pady=(10, 20))
        
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
            
            # Process the file
            result = self.format_csv(self.input_file, output_file)
            
            self.root.after(0, lambda: self.processing_complete(result, output_file))
            
        except Exception as e:
            self.root.after(0, lambda: self.processing_error(str(e)))
    
    def processing_complete(self, result, output_file):
        self.hide_processing()
        self.status_label.config(text=f"✓ Processing complete! {result['rows']} rows processed", 
                                fg="#27ae60")
        
        # Generate success message
        success_msg = f"CSV processed successfully!\n\nRows processed: {result['rows']}\nOutput saved to: {os.path.basename(output_file)}"

        # Add HTML generation info if applicable
        if 'html_files' in result and result['html_files']:
            success_msg += f"\n\nHTML files generated: {len(result['html_files'])}"
            success_msg += f"\nLocation: html_output/"

        messagebox.showinfo("Success", success_msg)
    
    def processing_error(self, error_msg):
        self.hide_processing()
        self.status_label.config(text="❌ Processing failed", fg="#e74c3c")
        messagebox.showerror("Error", f"An error occurred while processing:\n\n{error_msg}")
    
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
    
    def format_csv(self, input_file, output_file):
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
        
        # Create output dataframe with subtotals
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
        
        # Generate HTML files if template exists
        html_files = []
        template_path = "realisierungsdaten.html"
        if os.path.exists(template_path):
            try:
                from html_generator import generate_all_html_files
                html_files = generate_all_html_files(output_file, template_path)
            except Exception as e:
                print(f"Error generating HTML files: {e}")

        return {"rows": len(final_df), "html_files": html_files}
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CSVFormatterApp()
    app.run()