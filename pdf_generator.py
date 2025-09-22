import pandas as pd
import os
from datetime import datetime
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_pdf_for_fundraiser(fundraiser_data, output_dir):
    """
    Generate PDF file for a specific fundraiser.

    Args:
        fundraiser_data: DataFrame containing data for one fundraiser
        output_dir: Directory to save the generated PDF files

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
            statuses = valid_rows['status_agency'].fillna('').astype(str)
            points = valid_rows['points'].fillna(0).astype(str).str.replace('.', ',')

            # Build table data efficiently
            for i in range(len(valid_rows)):
                table_data.append([ref_ids.iloc[i], ages.iloc[i], intervals.iloc[i],
                                 amounts.iloc[i], statuses.iloc[i], points.iloc[i]])

            # Calculate totals efficiently
            total_points = valid_rows['points'].fillna(0).sum()
            total_count = len(valid_rows)
            approved_count = (valid_rows['status_agency'].str.lower() == 'approved').sum()

        # Create table with properly balanced column widths
        data_table = Table(table_data, colWidths=[2.5*cm, 1.4*cm, 2.0*cm, 3.0*cm, 2.0*cm, 1.6*cm])
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

        # Week footer with totals
        points_total_str = str(total_points).replace('.', ',')
        bonus_granted = "Ja" if approved_count / total_count >= 0.7 else "Nein"

        footer_data = [
            [f'Punkte gesamt: {points_total_str}', f'Bonus gewährt: {bonus_granted}']
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

    # Filter out subtotal rows and empty rows - optimize filtering
    df = df[
        df['Public RefID'].notna() &
        (df['Public RefID'] != '') &
        (~df['Public RefID'].astype(str).str.contains('Total:', na=False))
    ]

    # Pre-process common data types for better performance
    numeric_columns = ['Public RefID', 'Age', 'Amount Yearly', 'points']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Get unique fundraisers
    fundraisers = df.groupby(['Fundraiser ID', 'Fundraiser Name'])
    total_fundraisers = len(fundraisers)
    print(f"Processing {total_fundraisers} fundraisers...")

    generated_files = []

    for i, ((fundraiser_id, fundraiser_name), fundraiser_data) in enumerate(fundraisers, 1):
        try:
            print(f"[{i}/{total_fundraisers}] Generating PDF for {fundraiser_name} (ID: {fundraiser_id})...")
            pdf_path = generate_pdf_for_fundraiser(fundraiser_data, output_dir)
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