import pandas as pd
import os
from datetime import datetime
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_pdf_for_fundraiser(fundraiser_data, output_dir, payment_info=None, tl_bonus_info=None):
    """
    Generate PDF file for a specific fundraiser with payment information.

    Args:
        fundraiser_data: DataFrame containing regular donor data for one fundraiser
        output_dir: Directory to save the generated PDF files
        payment_info: DataFrame containing payment information for this fundraiser
        tl_bonus_info: DataFrame containing TL bonus information for this fundraiser

    Returns:
        Path to the generated PDF file
    """
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
            first_week = week_num
            break

    month = "Mai"  # Default
    if first_week:
        for week_range, month_name in month_mapping.items():
            if first_week in week_range:
                month = month_name
                break

    # Create filename
    safe_name = re.sub(r'[^\w\s-]', '', fundraiser_name.replace(' ', '_'))
    filename = f"{fundraiser_id}_{safe_name}_Realisierungsdaten.pdf"
    output_path = os.path.join(output_dir, filename)

    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=18,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=5
    )

    address_style = ParagraphStyle(
        'AddressStyle',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        textColor=colors.grey,
        alignment=TA_LEFT,
        spaceAfter=20
    )

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=16,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=20
    )

    # Build PDF content
    content = []

    # Header
    header_text = "CWF Changing Waves Fundraising GmbH"
    address_text = "Moselstraße 26 • 50674 Köln"

    content.append(Paragraph(header_text, header_style))
    content.append(Spacer(1, 10))  # Add spacing between header and address
    content.append(Paragraph(address_text, address_style))
    content.append(HRFlowable(width="100%", thickness=2, color=colors.black))
    content.append(Spacer(1, 20))

    # Title
    content.append(Paragraph("Realisierungsdaten", title_style))

    # Info fields table
    info_data = [
        ['Name:', fundraiser_name, 'Fundraiser-ID:', fundraiser_id],
        ['Monat:', month, 'Jahr:', year]
    ]

    info_table = Table(info_data, colWidths=[2.5*cm, 4.5*cm, 3*cm, 3*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    content.append(info_table)
    content.append(Spacer(1, 30))

    # Group data by calendar weeks
    weeks_data = {}
    for week in sorted(calendar_weeks):
        if pd.notna(week):
            week_data = fundraiser_data[fundraiser_data['Calendar week'] == week]
            if not week_data.empty:
                weeks_data[week] = week_data

    # Generate content for each week
    for week, week_data in weeks_data.items():
        # Week title
        week_title = f"Kalenderwoche: {week}"
        week_style = ParagraphStyle(
            'WeekStyle',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            spaceAfter=10
        )
        content.append(Paragraph(week_title, week_style))

        # Create data table
        table_data = [['Public Ref ID', 'Alter', 'Intervall', 'Jahresbeitrag', 'Status', 'Punkte']]

        total_points = 0
        approved_count = 0
        total_count = 0

        # Filter valid rows once for better performance
        valid_rows = week_data[week_data['Public RefID'].notna()]

        if not valid_rows.empty:
            # Vectorized operations for better performance
            ref_ids = valid_rows['Public RefID'].fillna(0).astype(int).astype(str)
            ages = valid_rows['Age'].fillna(0).astype(int).astype(str)
            intervals = valid_rows['Interval'].fillna('').astype(str)
            amounts = valid_rows['Amount Yearly'].fillna(0).astype(int).astype(str)
            statuses = valid_rows['status_agency'].fillna('').astype(str).str.replace('conditionally-approved', 'conditionally-\napproved')
            points = valid_rows['points'].fillna(0).astype(str).str.replace('.', ',')

            # Build table data efficiently with proper text wrapping for status
            for i in range(len(valid_rows)):
                status_text = statuses.iloc[i]
                if '\n' in status_text:
                    status_cell = Paragraph(status_text.replace('\n', '<br/>'), styles['Normal'])
                else:
                    status_cell = status_text

                table_data.append([ref_ids.iloc[i], ages.iloc[i], intervals.iloc[i],
                                 amounts.iloc[i], status_cell, points.iloc[i]])

            # Calculate totals efficiently
            total_points = valid_rows['points'].fillna(0).sum()
            total_count = len(valid_rows)
            approved_count = (valid_rows['status_agency'].str.lower() == 'approved').sum()

        # Create table with properly balanced column widths (wider Status column)
        data_table = Table(table_data, colWidths=[2.5*cm, 1.4*cm, 2.0*cm, 2.8*cm, 2.3*cm, 1.6*cm])
        data_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))

        content.append(data_table)
        content.append(Spacer(1, 10))

        # Week footer with totals and payout
        points_total_str = str(total_points).replace('.', ',')
        bonus_granted = "Ja" if approved_count / total_count >= 0.7 else "Nein"

        # Calculate payout for this week's points
        # We need to get working days - for now we'll use a default approach
        # In the full implementation, this would come from the payment_info data
        working_days = 5  # Default assumption
        week_payout = 0
        if total_points > 0:
            # Calculate daily average and determine payout
            daily_avg = total_points / working_days
            if daily_avg < 2:
                rate = 3.95
            elif daily_avg < 3:
                rate = 10
            elif daily_avg < 5:
                rate = 15
            elif daily_avg < 7:
                rate = 20
            else:
                rate = 30
            week_payout = total_points * rate

        payout_str = f"€{week_payout:.2f}"

        footer_data = [
            [f'Punkte gesamt: {points_total_str}', f'Bonus gewährt: {bonus_granted}'],
            [f'Wochenauszahlung: {payout_str}', f'Rate: €{rate if total_points > 0 else 0}/Punkt']
        ]

        footer_table = Table(footer_data, colWidths=[7*cm, 6*cm])
        footer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        content.append(footer_table)
        content.append(Spacer(1, 30))


    # Add team leader bonus page if available
    if tl_bonus_info is not None and not tl_bonus_info.empty:
        content.append(PageBreak())

        # Header
        content.append(Paragraph(header_text, header_style))
        content.append(Spacer(1, 10))
        content.append(Paragraph(address_text, address_style))
        content.append(HRFlowable(width="100%", thickness=2, color=colors.black))
        content.append(Spacer(1, 20))

        # Title
        content.append(Paragraph("Team Leader Bonuses", title_style))

        # Info fields table
        tl_info_data = [
            ['Name:', fundraiser_name, 'Fundraiser-ID:', fundraiser_id],
            ['Monat:', month, 'Jahr:', year]
        ]

        tl_info_table = Table(tl_info_data, colWidths=[2.5*cm, 4.5*cm, 3*cm, 3*cm])
        tl_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))

        content.append(tl_info_table)
        content.append(Spacer(1, 30))

        # Process TL bonus data into tabular format
        tl_data_rows = []
        milestone_data_rows = []
        current_week = None

        for _, bonus_row in tl_bonus_info.iterrows():
            # Check if this is a week header
            if pd.notna(bonus_row['Fundraiser Name']) and str(bonus_row['Fundraiser Name']).startswith('---'):
                current_week = str(bonus_row['Fundraiser Name']).replace('---', '').strip()
                continue

            # Team bonus data
            if str(bonus_row['Calendar week']) == 'Team Bonus':
                tl_name = str(bonus_row['Fundraiser Name'])
                team_avg = str(bonus_row['Public RefID']).replace('Team avg: ', '')
                team_size = str(bonus_row['Age'])
                rate = str(bonus_row['Interval'])
                bonus_amount = str(bonus_row['Amount Yearly'])
                bracket = str(bonus_row['status_agency'])
                team_points = str(bonus_row['points']).replace(' pts', '')

                tl_data_rows.append([current_week or 'Unknown', team_avg, team_size,
                                   bracket, rate, bonus_amount])

            elif str(bonus_row['Calendar week']) == 'Milestones':
                max_potential = str(bonus_row['Public RefID']).replace('Max potential: ', '')
                team_size_bracket = str(bonus_row['Age'])
                coach_bonus = str(bonus_row['Interval']).replace('Coach: ', '')
                office_bonus = str(bonus_row['Amount Yearly']).replace('Office: ', '')
                external_bonus = str(bonus_row['status_agency']).replace('External: ', '')
                material_bonus = str(bonus_row['points']).replace('Material: ', '')

                milestone_data_rows.append([current_week or 'Unknown', team_size_bracket,
                                          coach_bonus, office_bonus, external_bonus,
                                          material_bonus, max_potential])

        # Team Performance Bonus Table
        if tl_data_rows:
            tl_table_data = [['Week', 'Team Avg/Day', 'Team Size', 'Level', 'Rate', 'Bonus']] + tl_data_rows

            tl_table = Table(tl_table_data, colWidths=[3.0*cm, 3.0*cm, 3.0*cm, 3.0*cm, 3.0*cm, 3.0*cm])
            tl_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),

                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))

            content.append(tl_table)
            content.append(Spacer(1, 30))

        # Milestone Bonuses Tables (split into two)
        if milestone_data_rows:
            # Add subtitle for milestones
            milestone_subtitle_style = ParagraphStyle(
                'MilestoneSubtitleStyle',
                parent=styles['Normal'],
                fontSize=14,
                fontName='Helvetica-Bold',
                spaceAfter=10
            )
            content.append(Paragraph("Milestone Bonuses (Potential)", milestone_subtitle_style))

            # Debug: Check if we have milestone data
            print(f"Milestone data rows: {len(milestone_data_rows)}")
            if milestone_data_rows:
                print(f"First milestone row: {milestone_data_rows[0]}")

            # First table: Milestone Categories
            milestone_categories_data = [['Week', 'Team Size', 'Coach', 'Office', 'External', 'Material']]
            for row in milestone_data_rows:
                # Ensure we have enough columns
                if len(row) >= 6:
                    milestone_categories_data.append(row[:6])
                else:
                    print(f"Warning: Milestone row has only {len(row)} columns: {row}")

            if len(milestone_categories_data) > 1:  # Only create table if we have data
                milestone_categories_table = Table(milestone_categories_data, colWidths=[3.0*cm, 3.0*cm, 3.0*cm, 3.0*cm, 3.0*cm, 3.0*cm])
                milestone_categories_table.setStyle(TableStyle([
                    # Header row
                    ('BACKGROUND', (0, 0), (-1, 0), colors.white),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

                    # Data rows
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),

                    # Grid
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ]))

                content.append(milestone_categories_table)
                content.append(Spacer(1, 15))

            # Second table: Maximum Totals
            milestone_totals_data = [['Week', 'Max Total']]
            for row in milestone_data_rows:
                # Take first column (Week) and last column (Max Total)
                if len(row) >= 7:
                    milestone_totals_data.append([row[0], row[6]])
                else:
                    print(f"Warning: Cannot access column 6 in milestone row: {row}")

            if len(milestone_totals_data) > 1:  # Only create table if we have data
                milestone_totals_table = Table(milestone_totals_data, colWidths=[9.0*cm, 9.0*cm])
                milestone_totals_table.setStyle(TableStyle([
                    # Header row
                    ('BACKGROUND', (0, 0), (-1, 0), colors.white),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

                    # Data rows
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),

                    # Grid
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ]))

                content.append(milestone_totals_table)
                content.append(Spacer(1, 30))

    # Add total summary page
    content.append(PageBreak())

    # Header
    content.append(Paragraph(header_text, header_style))
    content.append(Spacer(1, 10))
    content.append(Paragraph(address_text, address_style))
    content.append(HRFlowable(width="100%", thickness=2, color=colors.black))
    content.append(Spacer(1, 20))

    # Title
    content.append(Paragraph("Total Payout Summary", title_style))

    # Info fields table
    summary_info_data = [
        ['Name:', fundraiser_name, 'Fundraiser-ID:', fundraiser_id],
        ['Monat:', month, 'Jahr:', year]
    ]

    summary_info_table = Table(summary_info_data, colWidths=[2.5*cm, 4.5*cm, 3*cm, 3*cm])
    summary_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))

    content.append(summary_info_table)
    content.append(Spacer(1, 30))

    # Calculate totals
    total_regular_payout = 0
    total_tl_bonus = 0

    # Sum up regular payouts
    if payment_info is not None and not payment_info.empty:
        for _, payment_row in payment_info.iterrows():
            payout_amount_str = str(payment_row['Amount Yearly']).replace('€', '')
            try:
                total_regular_payout += float(payout_amount_str)
            except:
                pass

    # Sum up TL bonuses
    if tl_bonus_info is not None and not tl_bonus_info.empty:
        for _, bonus_row in tl_bonus_info.iterrows():
            if str(bonus_row['Calendar week']) == 'Team Bonus':
                bonus_amount_str = str(bonus_row['Amount Yearly']).replace('€', '')
                try:
                    total_tl_bonus += float(bonus_amount_str)
                except:
                    pass

    total_payout = total_regular_payout + total_tl_bonus

    # Summary table
    summary_table_data = [
        ['Category', 'Amount'],
        ['Regular Fundraiser Payout', f'€{total_regular_payout:.2f}'],
        ['Team Leader Bonus', f'€{total_tl_bonus:.2f}'],
        ['TOTAL PAYOUT', f'€{total_payout:.2f}']
    ]

    summary_table = Table(summary_table_data, colWidths=[9.0*cm, 9.0*cm])
    summary_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Data rows
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -2), 11),

        # Total row (last row)
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),

        # All rows padding
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),

        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right-align amounts
    ]))

    content.append(summary_table)

    # Build PDF
    doc.build(content)
    return output_path

def generate_all_pdf_files(csv_file_path, output_dir=None):
    """
    Generate PDF files for all fundraisers from formatted CSV.

    Args:
        csv_file_path: Path to the formatted CSV file
        output_dir: Directory to save PDF files (defaults to pdf_output next to CSV file)

    Returns:
        List of generated PDF file paths
    """
    # If no output directory specified, create one next to the CSV file
    if output_dir is None:
        csv_dir = os.path.dirname(os.path.abspath(csv_file_path))
        output_dir = os.path.join(csv_dir, "pdf_output")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Reading and preprocessing CSV data...")
    # Read the formatted CSV
    df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig', skiprows=2)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Separate different types of data
    # Regular donor data
    regular_data = df[
        df['Public RefID'].notna() &
        (df['Public RefID'] != '') &
        (~df['Public RefID'].astype(str).str.contains('Total:', na=False)) &
        (~df['Public RefID'].astype(str).str.contains('Payout', na=False))
    ]

    # Payment information
    payment_data = df[
        df['Public RefID'].notna() &
        df['Public RefID'].astype(str).str.contains('Payout', na=False)
    ]

    # Team leader bonus information
    tl_bonus_data = df[
        (df['Calendar week'].notna() & df['Calendar week'].astype(str).isin(['Team Bonus', 'Milestones'])) |
        (df['Fundraiser Name'].notna() & df['Fundraiser Name'].astype(str).str.contains('---', na=False)) |
        (df['Fundraiser Name'].notna() & df['Fundraiser Name'].astype(str).str.contains('TEAM LEADER BONUSES', na=False))
    ]

    # Pre-process common data types for better performance
    numeric_columns = ['Public RefID', 'Age', 'Amount Yearly']
    for col in numeric_columns:
        if col in regular_data.columns:
            regular_data[col] = pd.to_numeric(regular_data[col], errors='coerce')

    # Handle points column with comma decimal separator
    if 'points' in regular_data.columns:
        regular_data['points'] = regular_data['points'].astype(str).str.replace(',', '.', regex=False)
        regular_data['points'] = pd.to_numeric(regular_data['points'], errors='coerce')

    # Get unique fundraisers from regular data
    fundraisers = regular_data.groupby(['Fundraiser ID', 'Fundraiser Name'])
    total_fundraisers = len(fundraisers)
    print(f"Processing {total_fundraisers} fundraisers...")

    generated_files = []

    for i, ((fundraiser_id, fundraiser_name), fundraiser_data) in enumerate(fundraisers, 1):
        try:
            print(f"[{i}/{total_fundraisers}] Generating PDF for {fundraiser_name} (ID: {fundraiser_id})...")

            # Get payment info for this fundraiser (payment info is stored right after each fundraiser's data)
            # We need to get all CSV data first to find payment info by proximity
            all_csv_data = pd.read_csv(csv_file_path, sep=';', encoding='utf-8-sig', skiprows=2)
            all_csv_data.columns = all_csv_data.columns.str.strip()

            # Find payment rows that appear after this specific fundraiser
            fundraiser_payment_info = pd.DataFrame()
            fundraiser_tl_info = pd.DataFrame()

            # Find rows related to this fundraiser in the complete CSV
            for idx, row in all_csv_data.iterrows():
                # Check if this is payment info following our fundraiser
                if (pd.notna(row['Public RefID']) and
                    str(row['Public RefID']).startswith('Payout') and
                    idx > 0):  # Look at previous rows to find the fundraiser this belongs to

                    # Look backwards to find the fundraiser this payment belongs to
                    for prev_idx in range(idx - 1, max(0, idx - 20), -1):  # Look back up to 20 rows
                        prev_row = all_csv_data.iloc[prev_idx]
                        if (pd.notna(prev_row['Fundraiser Name']) and
                            prev_row['Fundraiser Name'] == fundraiser_name and
                            pd.notna(prev_row['Public RefID']) and
                            not str(prev_row['Public RefID']).startswith('Payout')):
                            # This payment belongs to our fundraiser
                            fundraiser_payment_info = pd.concat([fundraiser_payment_info, row.to_frame().T])
                            break

                # Check for TL bonus info
                elif ((pd.notna(row['Calendar week']) and str(row['Calendar week']) in ['Team Bonus', 'Milestones']) and
                      (pd.notna(row['Fundraiser Name']) and str(row['Fundraiser Name']) == fundraiser_name)):
                    fundraiser_tl_info = pd.concat([fundraiser_tl_info, row.to_frame().T])

                # Check for week headers in TL bonus section
                elif (pd.notna(row['Fundraiser Name']) and str(row['Fundraiser Name']).startswith('---')):
                    # Include week headers for context
                    if not fundraiser_tl_info.empty:  # Only if we already have TL info for this fundraiser
                        fundraiser_tl_info = pd.concat([fundraiser_tl_info, row.to_frame().T])

            pdf_path = generate_pdf_for_fundraiser(fundraiser_data, output_dir,
                                                 fundraiser_payment_info, fundraiser_tl_info)
            generated_files.append(pdf_path)
            print(f"✓ Generated: {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"✗ Error generating PDF for {fundraiser_name}: {e}")

    print(f"Completed! Generated {len(generated_files)} PDF files.")
    return generated_files

if __name__ == "__main__":
    # Test the PDF generation
    csv_path = "formatted_output.csv"

    if os.path.exists(csv_path):
        generated_files = generate_all_pdf_files(csv_path)
        print(f"\nGenerated {len(generated_files)} PDF files:")
        for file_path in generated_files:
            print(f"  - {file_path}")
    else:
        print("Required files not found. Please ensure formatted_output.csv exists.")