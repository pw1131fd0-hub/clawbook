"""PDF export service for ClawBook analytics and profiles."""
from io import BytesIO
from datetime import datetime, timezone
from typing import List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from backend.models.orm_models import Goal


class PDFExportService:
    """Service for exporting analytics and profiles to PDF format."""

    @staticmethod
    def export_growth_report(
        goals: List[Goal],
        user_name: str = "User",
        include_progress: bool = True
    ) -> BytesIO:
        """
        Export growth tracking data to PDF.

        Args:
            goals: List of Goal objects to include in the report
            user_name: Name of the user for personalization
            include_progress: Whether to include progress details

        Returns:
            BytesIO object containing the PDF data
        """
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("Growth Tracking Report", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Header info
        header_data = [
            ["Report Generated", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")],
            ["User", user_name],
            ["Total Goals", str(len(goals))],
        ]
        header_table = Table(header_data, colWidths=[2*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*inch))

        # Goals summary
        story.append(Paragraph("Goals Summary", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))

        if goals:
            goal_data = [["ID", "Title", "Category", "Target", "Status", "Progress"]]
            for goal in goals:
                progress_pct = f"{(goal.progress_percent or 0):.0f}%" if goal.progress_percent else "0%"
                goal_data.append([
                    str(goal.id)[:8],
                    goal.title[:30],
                    goal.category or "N/A",
                    goal.target_value or "N/A",
                    goal.status or "active",
                    progress_pct,
                ])

            goals_table = Table(goal_data, colWidths=[0.8*inch, 2*inch, 1*inch, 1*inch, 0.8*inch, 0.9*inch])
            goals_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            story.append(goals_table)
        else:
            story.append(Paragraph("No goals found.", styles['Normal']))

        story.append(Spacer(1, 0.2*inch))

        # Statistics
        story.append(Paragraph("Statistics", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))

        stats_data = []
        by_category = {}
        by_status = {}

        for goal in goals:
            category = goal.category or "Uncategorized"
            status = goal.status or "unknown"

            by_category[category] = by_category.get(category, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1

        stats_table_data = [
            ["Metric", "Count"],
        ]
        for cat, count in sorted(by_category.items()):
            stats_table_data.append([f"Category: {cat}", str(count)])
        for stat, count in sorted(by_status.items()):
            stats_table_data.append([f"Status: {stat}", str(count)])

        stats_table = Table(stats_table_data, colWidths=[3*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(stats_table)

        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer

    @staticmethod
    def export_personality_report(
        personality_data: dict,
        user_name: str = "User"
    ) -> BytesIO:
        """
        Export personality profile to PDF.

        Args:
            personality_data: Dictionary containing personality traits and archetypes
            user_name: Name of the user for personalization

        Returns:
            BytesIO object containing the PDF data
        """
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("Personality Profile Report", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Header
        header_data = [
            ["Report Generated", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")],
            ["User", user_name],
        ]
        header_table = Table(header_data, colWidths=[2*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*inch))

        # Archetype
        story.append(Paragraph("Primary Archetype", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))

        archetype = personality_data.get('archetype', {})
        archetype_data = [
            ["Archetype", archetype.get('name', 'Unknown')],
            ["Confidence", f"{archetype.get('confidence', 0):.1f}%"],
            ["Description", archetype.get('description', 'No description available')],
        ]
        archetype_table = Table(archetype_data, colWidths=[1.5*inch, 3.5*inch])
        archetype_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(archetype_table)
        story.append(Spacer(1, 0.3*inch))

        # Traits
        story.append(Paragraph("Personality Traits", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))

        traits = personality_data.get('traits', [])
        if traits:
            traits_data = [["Trait", "Score"]]
            for trait in traits:
                score = trait.get('score', 0)
                traits_data.append([
                    trait.get('name', 'Unknown'),
                    f"{score:.1f}",
                ])

            traits_table = Table(traits_data, colWidths=[3*inch, 1.5*inch])
            traits_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            story.append(traits_table)
        else:
            story.append(Paragraph("No trait data available.", styles['Normal']))

        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer
