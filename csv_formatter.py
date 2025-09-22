import pandas as pd
import numpy as np
from collections import defaultdict
import os
from html_generator import generate_all_html_files

def calculate_points(age, interval, amount_yearly):
    """
    Calculate points based on age, donation interval, and yearly amount.
    Rules:
    - Spenderin unter 25 Jahren pauschal 0,5 Punkte
    - Spenderin unter 30 Jahren: monatlich 0,5 Punkte, sonst pauschal 1 Punkt
    - Spenderin ab 30 reguläre Punktevergabe nach Tabelle
    - Spenderin über 40 Jahre: +1 extra Punkt

    Point table:
    Jahresbeitrag | Jährlich | Halbjährlich | Monatlich
    Ab 120 €     |    2     |     1,5      |     1
    Ab 180 €     |    3     |     2,5      |    1,5
    Ab 240 €     |    4     |      3       |     2
    Ab 360 €     |    5     |      4       |     3
    """
    age = int(age)
    amount = float(amount_yearly)

    # Under 25: always 0.5 points
    if age < 25:
        return 0.5

    # Under 30 but 25+: monthly = 0.5, others = 1
    if age < 30:
        return 0.5 if interval.lower() == 'monthly' else 1.0

    # 30+ follow the point table
    base_points = 0
    interval_lower = interval.lower()

    if amount >= 360:
        if 'yearly' in interval_lower or 'jährlich' in interval_lower:
            base_points = 5
        elif 'half' in interval_lower or 'halbjährlich' in interval_lower:
            base_points = 4
        else:  # monthly/monatlich
            base_points = 3
    elif amount >= 240:
        if 'yearly' in interval_lower or 'jährlich' in interval_lower:
            base_points = 4
        elif 'half' in interval_lower or 'halbjährlich' in interval_lower:
            base_points = 3
        else:  # monthly/monatlich
            base_points = 2
    elif amount >= 180:
        if 'yearly' in interval_lower or 'jährlich' in interval_lower:
            base_points = 3
        elif 'half' in interval_lower or 'halbjährlich' in interval_lower:
            base_points = 2.5
        else:  # monthly/monatlich
            base_points = 1.5
    elif amount >= 120:
        if 'yearly' in interval_lower or 'jährlich' in interval_lower:
            base_points = 2
        elif 'half' in interval_lower or 'halbjährlich' in interval_lower:
            base_points = 1.5
        else:  # monthly/monatlich
            base_points = 1
    else:
        # Less than 120€ - minimum points based on interval
        if 'yearly' in interval_lower or 'jährlich' in interval_lower:
            base_points = 1
        elif 'half' in interval_lower or 'halbjährlich' in interval_lower:
            base_points = 0.5
        else:  # monthly/monatlich
            base_points = 0.5

    # Over 40 (not 40+): +1 extra point
    if age > 40:
        base_points += 1

    return base_points

def calculate_bonus_eligibility(fundraiser_data):
    """
    Calculate if fundraiser is eligible for bonus based on 70% approved rule.
    Only count cancellation and active/billable donors for that person.
    """
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

def format_csv(input_file, output_file, generate_html=True, html_template_path="realisierungsdaten.html"):
    """
    Main function to reformat the CSV according to specifications and optionally generate HTML files.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        generate_html: Whether to generate HTML files for each fundraiser
        html_template_path: Path to HTML template file

    Returns:
        dict: Summary of processing results
    """
    # Read CSV, skipping the first 2 header rows
    df = pd.read_csv(input_file, sep=';', encoding='utf-8-sig', skiprows=2)
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Filter out subtotal and total rows
    df = df[~df['Fundraiser Name'].str.contains('Subtotal|Total', case=False, na=False)]
    
    # Filter out rows where Public RefID is NaN or empty
    df = df[df['Public RefID'].notna()]
    df = df[df['Public RefID'] != '']
    
    # Forward fill fundraiser information for rows that belong to the same fundraiser
    df['Fundraiser ID'] = df['Fundraiser ID'].ffill()
    df['Fundraiser Name'] = df['Fundraiser Name'].ffill()
    df['Calendar week'] = df['Calendar week'].ffill()
    df['Billing group'] = df['Billing group'].ffill()
    
    # Preserve original formatting for Fundraiser ID (keep leading zeros)
    df['Fundraiser ID'] = df['Fundraiser ID'].astype(str).str.replace('.0', '').str.zfill(5)
    
    # Extract calendar week number for sorting
    df['KW_num'] = df['Calendar week'].str.extract(r'(\d+)').fillna(0).astype(int)
    
    # Calculate points for each donor
    df['points'] = df.apply(lambda row: calculate_points(
        row['Age'], row['Interval'], row['Amount Yearly']
    ), axis=1)
    
    # Group by fundraiser to calculate bonus eligibility
    fundraiser_bonus = {}
    for fundraiser_id in df['Fundraiser ID'].unique():
        if pd.notna(fundraiser_id):
            fundraiser_data = df[df['Fundraiser ID'] == fundraiser_id]
            fundraiser_bonus[fundraiser_id] = calculate_bonus_eligibility(fundraiser_data)
    
    # Add bonus status to dataframe
    df['bonus_status'] = df['Fundraiser ID'].map(fundraiser_bonus)
    
    # Sort by KW number, then by Fundraiser Name alphabetically
    df_sorted = df.sort_values(['KW_num', 'Fundraiser Name', 'Billing group'])
    
    # Select only required columns (removed billing group)
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
            
            # Add all individual entries for this fundraiser
            for i, (_, row) in enumerate(fundraiser_data.iterrows()):
                row_dict = row[required_columns].to_dict()
                
                # Don't show bonus_status on individual rows anymore
                row_dict['bonus_status'] = ''
                    
                final_rows.append(row_dict)
            
            # Add subtotal row for this fundraiser
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
    
    # Save to CSV with original styling
    import datetime
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Create header rows like the original
    header_lines = [
        f"WoVi_CW_Formatted_{current_date};" + ";" * (len(required_columns) - 1),
        ";" * len(required_columns)
    ]
    
    # Write the file with custom headers
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        # Write header lines
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
                    # Format numeric values properly
                    if col == 'points' and isinstance(value, (int, float)) and not str(value).startswith('Total:'):
                        row_values.append(str(value).replace('.', ','))  # Use comma as decimal separator
                    else:
                        row_values.append(str(value))
            f.write(';'.join(row_values) + '\n')
    
    print(f"CSV formatted successfully! Output saved to: {output_file}")
    print(f"Total rows processed: {len(final_df)}")
    print(f"Added subtotal rows for each fundraiser per calendar week")

    # Generate HTML files if requested
    html_files = []
    if generate_html and os.path.exists(html_template_path):
        try:
            print("\nGenerating HTML files for each fundraiser...")
            html_files = generate_all_html_files(output_file, html_template_path)
            if html_files:
                html_dir = os.path.dirname(html_files[0])
                print(f"Generated {len(html_files)} HTML files in '{html_dir}' directory")
            else:
                print("No HTML files were generated")
        except Exception as e:
            print(f"Error generating HTML files: {e}")
    elif generate_html:
        print(f"Warning: HTML template not found at {html_template_path}. Skipping HTML generation.")

    return {
        "csv_rows": len(final_df),
        "html_files": html_files,
        "csv_path": output_file
    }

if __name__ == "__main__":
    # Usage
    input_file = "KW18_Bis_KW22_WoVi_CW_Final_2025-0_1753881139314(1).csv"
    output_file = "formatted_output.csv"
    
    format_csv(input_file, output_file)