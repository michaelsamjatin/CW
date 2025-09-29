import pandas as pd
import os
from datetime import datetime
import re

def generate_html_for_fundraiser(fundraiser_data, template_path, output_dir):
    """
    Generate HTML file for a specific fundraiser using the template.

    Args:
        fundraiser_data: DataFrame containing data for one fundraiser
        template_path: Path to the HTML template file
        output_dir: Directory to save the generated HTML files
    """
    # Read the template
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # Extract fundraiser info - preserve original ID formatting
    fundraiser_id = str(fundraiser_data['Fundraiser ID'].iloc[0])
    # Ensure fundraiser ID has leading zeros (5 digits)
    if fundraiser_id.replace('.', '').replace('0', '').isdigit():
        fundraiser_id = fundraiser_id.replace('.0', '').zfill(5)
    fundraiser_name = fundraiser_data['Fundraiser Name'].iloc[0]

    # Determine month and year from calendar weeks
    calendar_weeks = fundraiser_data['Calendar week'].dropna().unique()
    year = "2025"  # Default year based on data

    # Extract month from calendar weeks (approximation)
    month_mapping = {
        range(1, 5): "Januar",
        range(5, 9): "Februar",
        range(9, 14): "März",
        range(14, 18): "April",
        range(18, 23): "Mai",
        range(23, 27): "Juni",
        range(27, 31): "Juli",
        range(31, 35): "August",
        range(35, 40): "September",
        range(40, 44): "Oktober",
        range(44, 48): "November",
        range(48, 53): "Dezember"
    }

    # Get first week number to determine month
    first_week = None
    for week in calendar_weeks:
        if '/' in str(week):
            week_num = int(str(week).split('/')[0])
        else:
            week_num = int(re.findall(r'\d+', str(week))[0])
        if first_week is None or week_num < first_week:
            first_week = week_num

    month = "Mai"  # Default
    if first_week:
        for week_range, month_name in month_mapping.items():
            if first_week in week_range:
                month = month_name
                break

    # Fill in the basic info fields
    template_content = template_content.replace('placeholder="Charlotte Lui"', f'value="{fundraiser_name}"')
    template_content = template_content.replace('placeholder="00004"', f'value="{fundraiser_id}"')
    template_content = template_content.replace('placeholder="November"', f'value="{month}"')
    template_content = template_content.replace('placeholder="2025"', f'value="{year}"')

    # Group data by calendar week, separating regular data from payment info
    weeks_data = {}
    payment_info = []
    tl_bonus_info = []

    for _, row in fundraiser_data.iterrows():
        if pd.notna(row['Calendar week']) and pd.notna(row['Public RefID']):
            week = row['Calendar week']
            if week not in weeks_data:
                weeks_data[week] = []
            weeks_data[week].append(row)
        elif pd.notna(row['Public RefID']) and str(row['Public RefID']).startswith('Payout'):
            # This is payment information
            payment_info.append(row)
        elif pd.notna(row['Calendar week']) and str(row['Calendar week']) in ['Team Bonus', 'Milestones']:
            # This is TL bonus information
            tl_bonus_info.append(row)
        elif pd.notna(row['Fundraiser Name']) and str(row['Fundraiser Name']).startswith('---') and str(row['Fundraiser Name']).endswith('---'):
            # This is a week header for TL bonuses
            tl_bonus_info.append(row)

    # Generate weeks HTML
    weeks_html = ""
    week_index = 0

    for week, week_rows in weeks_data.items():
        # Calculate total points for this week (excluding cancelled)
        total_points = 0
        for row in week_rows:
            if row['status_agency'] != 'cancelled':
                try:
                    points_val = float(str(row['points']).replace(',', '.'))
                    total_points += points_val
                except (ValueError, TypeError):
                    continue

        # Determine bonus status
        approved_count = sum(1 for row in week_rows if row['status_agency'] in ['approved', 'conditionally-approved'])
        total_count = len([row for row in week_rows if row['status_agency'] in ['approved', 'conditionally-approved', 'cancelled']])
        bonus_eligible = "ja" if total_count > 0 and (approved_count / total_count) >= 0.7 else "nein"

        # Generate rows HTML for this week
        rows_html = ""
        for row in week_rows:
            # Convert points to German decimal format - ensure always visible
            try:
                points_val = float(str(row['points']).replace(',', '.'))
                points_str = str(points_val).replace('.', ',')
                # Ensure points are never empty
                if not points_str or points_str == '':
                    points_str = "0,0"
            except (ValueError, TypeError):
                points_str = "0,0"

            # Format values properly without unnecessary conversions
            ref_id = str(row['Public RefID']).replace('.0', '') if pd.notna(row['Public RefID']) else ""
            age = str(int(float(row['Age']))) if pd.notna(row['Age']) else ""
            interval = str(row['Interval']) if pd.notna(row['Interval']) else ""
            amount = str(int(float(row['Amount Yearly']))) if pd.notna(row['Amount Yearly']) else ""
            status = str(row['status_agency']) if pd.notna(row['status_agency']) else ""

            rows_html += f'''
                        <tr>
                            <td><input type="text" value="{ref_id}" readonly></td>
                            <td><input type="text" value="{age}" readonly></td>
                            <td><input type="text" value="{interval}" readonly></td>
                            <td><input type="text" value="{amount}" readonly></td>
                            <td><input type="text" value="{status}" readonly></td>
                            <td><input type="text" value="{points_str}" readonly></td>
                        </tr>'''

        # Generate week section HTML - ensure total points are visible
        total_points_str = str(total_points).replace('.', ',')
        if not total_points_str or total_points_str == '':
            total_points_str = "0,0"

        week_html = f'''
            <div class="week-section">
                <div class="week-title">
                    <span>Kalenderwoche:</span>
                    <input type="text" value="{week}" readonly>
                </div>

                <table class="week-table">
                    <thead>
                        <tr>
                            <th style="width: 20%;">Public Ref ID</th>
                            <th style="width: 10%;">Alter</th>
                            <th style="width: 15%;">Intervall</th>
                            <th style="width: 12%;">Jahresbeitrag</th>
                            <th style="width: 13%;">Status</th>
                            <th style="width: 10%;">Punkte</th>
                        </tr>
                    </thead>
                    <tbody class="week-tbody">{rows_html}
                    </tbody>
                </table>

                <div class="week-footer">
                    <div>
                        <span class="points-total">Punkte gesamt: <span class="total-display">{total_points_str}</span></span>
                    </div>
                    <div>
                        <label>Bonus gewährt:</label>
                        <input type="text" value="{"Ja" if bonus_eligible == "ja" else "Nein"}" readonly>
                    </div>
                </div>
            </div>'''

        weeks_html += week_html
        week_index += 1

    # Add payment information section if available
    if payment_info:
        payment_html = '''
            <div class="payment-section" style="margin-top: 30px; padding: 20px; border: 2px solid #3498db; border-radius: 8px; background-color: #f8f9fa;">
                <h3 style="color: #2c3e50; margin-bottom: 15px;">💰 Payment Information</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">'''

        for payment in payment_info:
            payout_type = str(payment['Public RefID']).replace('Payout (', '').replace(' avg)', '')
            working_days = str(payment['Interval']).replace(' days', '')
            payout_amount = str(payment['Amount Yearly'])
            rate = str(payment['status_agency'])
            daily_avg = str(payment['points']).replace('Avg: ', '')

            payment_html += f'''
                    <div style="background-color: white; padding: 15px; border-radius: 5px; border-left: 4px solid #27ae60;">
                        <div style="font-weight: bold; color: #2c3e50; margin-bottom: 10px;">Regular Fundraiser Payout</div>
                        <div style="font-size: 14px;">
                            <div><strong>Performance Level:</strong> {payout_type}</div>
                            <div><strong>Working Days:</strong> {working_days}</div>
                            <div><strong>Daily Average:</strong> {daily_avg} points/day</div>
                            <div><strong>{rate}</strong></div>
                            <div style="font-size: 16px; font-weight: bold; color: #27ae60; margin-top: 8px;">
                                <strong>Total Payout: {payout_amount}</strong>
                            </div>
                        </div>
                    </div>'''

        payment_html += '''
                </div>
            </div>'''

        weeks_html += payment_html

    # Add team leader bonus section if available
    if tl_bonus_info:
        tl_html = '''
            <div class="tl-bonus-section" style="margin-top: 30px; padding: 20px; border: 2px solid #e74c3c; border-radius: 8px; background-color: #fdf2f2;">
                <h3 style="color: #c0392b; margin-bottom: 15px;">👑 Team Leader Bonuses by Week</h3>'''

        current_week = None
        for bonus in tl_bonus_info:
            # Check if this is a week header
            if pd.notna(bonus['Fundraiser Name']) and str(bonus['Fundraiser Name']).startswith('---'):
                week_name = str(bonus['Fundraiser Name']).replace('---', '').strip()
                current_week = week_name
                tl_html += f'''
                    <div style="background-color: #34495e; color: white; padding: 10px; border-radius: 5px; margin: 20px 0 10px 0; text-align: center;">
                        <strong>Calendar Week: {week_name}</strong>
                    </div>'''
                continue

            # Team bonus
            if str(bonus['Calendar week']) == 'Team Bonus':
                tl_name = str(bonus['Fundraiser Name'])
                team_avg = str(bonus['Public RefID']).replace('Team avg: ', '')
                team_size = str(bonus['Age'])
                rate = str(bonus['Interval'])
                bonus_amount = str(bonus['Amount Yearly'])
                bracket = str(bonus['status_agency'])
                team_points = str(bonus['points']).replace(' pts', '')

                tl_html += f'''
                    <div style="background-color: white; padding: 15px; border-radius: 5px; border-left: 4px solid #e74c3c; margin-bottom: 15px;">
                        <div style="font-weight: bold; color: #c0392b; margin-bottom: 10px;">Team Leader: {tl_name} - Performance Bonus</div>
                        <div style="font-size: 14px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div><strong>Team Average:</strong> {team_avg} points/day</div>
                            <div><strong>Team Size:</strong> {team_size}</div>
                            <div><strong>Performance Level:</strong> {bracket}</div>
                            <div><strong>Rate:</strong> {rate}</div>
                            <div><strong>Team Points:</strong> {team_points} points</div>
                            <div style="grid-column: 1/-1; font-size: 16px; font-weight: bold; color: #e74c3c; margin-top: 8px;">
                                <strong>Weekly Team Bonus: {bonus_amount}</strong>
                            </div>
                        </div>
                    </div>'''

            elif str(bonus['Calendar week']) == 'Milestones':
                max_potential = str(bonus['Public RefID']).replace('Max potential: ', '')
                team_size_bracket = str(bonus['Age'])
                coach_bonus = str(bonus['Interval']).replace('Coach: ', '')
                office_bonus = str(bonus['Amount Yearly']).replace('Office: ', '')
                external_bonus = str(bonus['status_agency']).replace('External: ', '')
                material_bonus = str(bonus['points']).replace('Material: ', '')

                tl_html += f'''
                    <div style="background-color: white; padding: 15px; border-radius: 5px; border-left: 4px solid #f39c12; margin-bottom: 15px;">
                        <div style="font-weight: bold; color: #e67e22; margin-bottom: 10px;">Milestone Bonuses ({team_size_bracket})</div>
                        <div style="font-size: 14px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div><strong>Communication (Coach):</strong> {coach_bonus}</div>
                            <div><strong>Communication (Office):</strong> {office_bonus}</div>
                            <div><strong>External Presence:</strong> {external_bonus}</div>
                            <div><strong>Material Responsibility:</strong> {material_bonus}</div>
                            <div style="grid-column: 1/-1; font-size: 16px; font-weight: bold; color: #f39c12; margin-top: 8px;">
                                <strong>{max_potential}</strong>
                            </div>
                        </div>
                    </div>'''

        tl_html += '''
            </div>'''

        weeks_html += tl_html

    # Replace the weeks container in template
    # Find the weeks container and replace it
    weeks_container_start = template_content.find('<div id="weeks-container">')
    weeks_container_end = template_content.find('</div>', template_content.find('<!-- Add Week Button -->'))

    if weeks_container_start != -1 and weeks_container_end != -1:
        before_container = template_content[:weeks_container_start]
        after_container = template_content[weeks_container_end:]

        new_content = before_container + f'<div id="weeks-container">{weeks_html}</div>' + after_container
    else:
        new_content = template_content

    # Remove the add week button and JavaScript functionality for readonly version
    new_content = re.sub(r'<!-- Add Week Button -->.*?</div>', '', new_content, flags=re.DOTALL)
    new_content = re.sub(r'<script>.*?</script>', '', new_content, flags=re.DOTALL)

    # Add some CSS to hide interactive elements and make it read-only
    readonly_css = '''
        <style>
            .add-row-btn, .add-week-btn, .add-week-container { display: none !important; }
            input[readonly], select[disabled] {
                background-color: #f9f9f9 !important;
                border-color: #ddd !important;
                cursor: not-allowed !important;
            }
        </style>
    '''
    new_content = new_content.replace('</head>', readonly_css + '</head>')

    # Create output filename (Windows-safe)
    safe_name = re.sub(r'[^\w\s-]', '', fundraiser_name).strip()
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    # Remove Windows invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '', safe_name)
    output_filename = f"{fundraiser_id}_{safe_name}_Realisierungsdaten.html"
    output_path = os.path.normpath(os.path.join(output_dir, output_filename))

    # Write the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return output_path

def generate_all_html_files(csv_file_path, template_path, output_dir=None):
    """
    Generate HTML files for all fundraisers from formatted CSV.

    Args:
        csv_file_path: Path to the formatted CSV file
        template_path: Path to the HTML template
        output_dir: Directory to save HTML files (defaults to html_output next to CSV file)

    Returns:
        List of generated HTML file paths
    """
    # If no output directory specified, create one next to the CSV file
    if output_dir is None:
        csv_dir = os.path.dirname(os.path.abspath(csv_file_path))
        output_dir = os.path.join(csv_dir, "html_output")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the formatted CSV
    df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig', skiprows=2)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Filter out subtotal rows and empty rows
    df = df[df['Public RefID'].notna()]
    df = df[df['Public RefID'] != '']
    df = df[~df['Public RefID'].astype(str).str.contains('Total:', na=False)]

    # Get unique fundraisers
    fundraisers = df.groupby(['Fundraiser ID', 'Fundraiser Name'])

    generated_files = []

    for (fundraiser_id, fundraiser_name), fundraiser_data in fundraisers:
        if pd.notna(fundraiser_id) and pd.notna(fundraiser_name):
            try:
                output_path = generate_html_for_fundraiser(
                    fundraiser_data,
                    template_path,
                    output_dir
                )
                generated_files.append(output_path)
                print(f"Generated HTML for {fundraiser_name} ({fundraiser_id}): {output_path}")
            except Exception as e:
                print(f"Error generating HTML for {fundraiser_name}: {e}")

    return generated_files

if __name__ == "__main__":
    # Test the HTML generation
    csv_path = "formatted_output.csv"
    template_path = "realisierungsdaten.html"

    if os.path.exists(csv_path) and os.path.exists(template_path):
        generated_files = generate_all_html_files(csv_path, template_path)
        print(f"\nGenerated {len(generated_files)} HTML files:")
        for file_path in generated_files:
            print(f"  - {file_path}")
    else:
        print("Required files not found. Please ensure formatted_output.csv and realisierungsdaten.html exist.")