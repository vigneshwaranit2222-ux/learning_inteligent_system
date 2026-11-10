import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class PDFReportGenerator:
    @staticmethod
    def generate_career_report_pdf(
        output_path: str,
        learner_name: str,
        job_title: str,
        company_name: str,
        readiness_score: float,
        matches: list,
        gaps: list,
        recommendations: list,
        calculation_trace: dict
    ) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1E293B'),
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#64748B')
        )
        section_style = ParagraphStyle(
            'ReportSection',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#0F172A'),
            fontName='Helvetica-Bold',
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155')
        )

        elements = []

        # Header
        elements.append(Paragraph("AI-POWERED CAREER READINESS AUDIT REPORT", title_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')} | Learner: <b>{learner_name}</b>", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6'), spaceAfter=15))

        # Executive Summary Box
        score_color = '#10B981' if readiness_score >= 75 else ('#F59E0B' if readiness_score >= 50 else '#EF4444')
        summary_data = [
            [
                Paragraph(f"<b>Target Position:</b> {job_title} ({company_name})", body_style),
                Paragraph(f"<b>Career Readiness Score:</b> <font color='{score_color}' size='16'><b>{readiness_score}%</b></font>", body_style)
            ]
        ]
        t_summary = Table(summary_data, colWidths=[340, 200])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(t_summary)
        elements.append(Spacer(1, 15))

        # Skill Matching Matrix
        elements.append(Paragraph("1. Skill Alignment Breakdown", section_style))
        match_table_data = [["Skill Name", "Category", "Status", "Demonstrated", "Required", "Weight"]]
        
        status_colors = {
            "matched": "#10B981",
            "exceeds": "#059669",
            "partial": "#F59E0B",
            "missing": "#EF4444",
            "insufficient": "#64748B"
        }

        for m in matches[:15]:
            status_tag = f"<font color='{status_colors.get(m['match_type'], '#334155')}'><b>{m['match_type'].upper()}</b></font>"
            match_table_data.append([
                Paragraph(m["skill_name"], body_style),
                Paragraph(m.get("category", "-"), body_style),
                Paragraph(status_tag, body_style),
                f"L{m['learner_level']}",
                f"L{m['required_level']}",
                f"{m.get('importance_weight', 1.0):.1f}x"
            ])

        t_matches = Table(match_table_data, colWidths=[140, 110, 90, 70, 65, 65])
        t_matches.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(t_matches)
        elements.append(Spacer(1, 15))

        # Skill Gaps
        elements.append(Paragraph("2. Critical Skill Gaps", section_style))
        if gaps:
            gap_data = [["Gap Skill", "Current Level", "Target Level", "Severity", "Requirement"]]
            for g in gaps[:10]:
                sev_color = "#EF4444" if g["gap_severity"] == "critical" else "#F59E0B"
                gap_data.append([
                    Paragraph(f"<b>{g['skill_name']}</b>", body_style),
                    f"Level {g['current_level']}",
                    f"Level {g['required_level']}",
                    Paragraph(f"<font color='{sev_color}'><b>{g['gap_severity'].upper()}</b></font>", body_style),
                    g.get("requirement_type", "mandatory").capitalize()
                ])
            t_gaps = Table(gap_data, colWidths=[160, 95, 95, 95, 95])
            t_gaps.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FEF2F2')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FCA5A5')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(t_gaps)
        else:
            elements.append(Paragraph("🎉 Congratulations! No skill gaps detected for this role requirements.", body_style))
        elements.append(Spacer(1, 15))

        # Recommendations
        elements.append(Paragraph("3. Personalized Actionable Learning Roadmap", section_style))
        if recommendations:
            for i, r in enumerate(recommendations[:5], 1):
                p_text = f"<b>{i}. {r.get('resource_title', r.get('title', 'Learning Item'))}</b> ({r.get('provider', 'Provider')}) - <i>{r.get('estimated_hours', 10)} hrs</i><br/>"
                p_text += f"<font color='#2563EB'>Outcome:</font> {r.get('expected_outcome', 'Acquire required capability.')}<br/>"
                p_text += f"<font color='#64748B'>Reason:</font> {r.get('reason', 'Addresses verified gap.')}"
                elements.append(Paragraph(p_text, body_style))
                elements.append(Spacer(1, 6))
        elements.append(Spacer(1, 15))

        # Disclaimer
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=8))
        elements.append(Paragraph(
            "<b>Disclaimer:</b> The Career Readiness Score is an indicative, evidence-grounded skill match calculation "
            "based strictly on validated learner artifacts and target employer requirements. It does not constitute a guarantee of employment.",
            ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.HexColor('#94A3B8'))
        ))

        doc.build(elements)
        return output_path

pdf_report_generator = PDFReportGenerator()
