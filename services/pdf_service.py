from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def _register_font():
    font_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts', 'SimSun.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('SimSun', font_path))
    else:
        # Fallback, English only
        pass

def generate_transcript(student, scores):
    _register_font()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm,
                            leftMargin=20*mm, rightMargin=20*mm)
    elements = []
    styles = getSampleStyleSheet()
    cn_style = ParagraphStyle('Chinese', parent=styles['Normal'], fontName='SimSun', fontSize=12, leading=18)
    title_style = ParagraphStyle('Title_CN', parent=styles['Title'], fontName='SimSun', fontSize=18, alignment=TA_CENTER)

    # 标题
    elements.append(Paragraph("学生成绩单", title_style))
    elements.append(Spacer(1, 5*mm))
    # 学生信息
    info = f"学号：{student.stu_id}　　姓名：{student.name}　　性别：{student.gender or ''}<br/>"
    if student.class_ and student.class_.major:
        info += f"专业：{student.class_.major.major_name}　　班级：{student.class_.class_name}"
    elements.append(Paragraph(info, cn_style))
    elements.append(Spacer(1, 5*mm))

    # 表格
    data = [['课程', '学分', '平时', '期末', '总评', '绩点']]
    total_credits = 0
    weighted_sum = 0
    for s in scores:
        gpa_pt = 4.0 if s['total_score'] >= 90 else 3.0 if s['total_score'] >= 80 else \
                 2.0 if s['total_score'] >= 70 else 1.0 if s['total_score'] >= 60 else 0
        data.append([s['course_name'], str(s['credit']),
                     str(s['regular']), str(s['final']), str(s['total']), str(gpa_pt)])
        total_credits += s['credit']
        weighted_sum += s['credit'] * gpa_pt
    gpa = round(weighted_sum / total_credits, 2) if total_credits else 0
    data.append(['合计', str(total_credits), '', '', '', f'GPA: {gpa}'])

    col_widths = [80, 40, 40, 40, 40, 50]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'SimSun'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F2F2F2')]),
        ('SPAN', (0,-1), (4,-1)),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#D9E2F3')),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer