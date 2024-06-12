import requests
API_KEY = '1b28274d-1b90-43c3-ad36-dd730905b034'
headers = {'apikey': API_KEY}


test_info = requests.get('https://api.learnbasics.fun/training/test/info/',headers=headers).json()
student_details = requests.get('https://api.learnbasics.fun/training/students/', headers=headers).json()
test_data = requests.get('https://api.learnbasics.fun/training/test/data/', headers=headers).json()
concept_data = requests.get('https://api.learnbasics.fun/training/test/concepts/',headers=headers).json()

class_section=f"{test_info['class']}-{test_info['section']}"
subject=test_info['subject']
chapter_name=test_info['chapter_name']
test_name=test_info['test_name']
test_link=test_info['test_url']
start_time=test_info['start_time']
end_time=test_info['end_time']
concept=test_info['concept_coveblack']

import pandas as pd
df_students = pd.DataFrame(student_details)
df_test_data = pd.DataFrame(test_data)

def convert(x):
    days = int(x)
    return f'{days} Day Ago'
def convert_to_fraction(x):
    total_marks_test = len(test_df['question_id'].unique())
    if x == 'Absent':
        return x
    else:
        return f"{int(x)}/{total_marks_test}"

test_df=df_test_data
test_summary = test_df.groupby('learner_id').agg(
    total_score=('mark', 'sum'),
    total_time_taken=('time_taken', 'sum'),
    total_attempts=('attempt','mean')
)

#final_summary = pd.merge(test_summary, total_marks_test, on='learner_id')
test_summary['total_time_taken'] = pd.to_datetime(test_summary['total_time_taken'], unit='s').dt.strftime('%M:%S')

# Merge with the student table
final_output = pd.merge(df_students, test_summary, on='learner_id', how='left')

# Convert last_login to the desired format
final_output['last_login'] = final_output['last_login'].apply(convert)

# Fill NaN values in total_score and total_time_taken for absent students
final_output['total_score'] = final_output['total_score'].fillna('Absent')
final_output['total_time_taken'] = final_output['total_time_taken'].fillna('')
final_output['total_score']=final_output['total_score'].apply(convert_to_fraction)

class_performance=final_output
class_performance = class_performance[['student_name', 'last_login', 'total_score', 'total_time_taken']]


class_performance = class_performance.reset_index(drop=False)
class_performance['index']=class_performance['index']+1
class_performance.columns = ['S.no','Name', 'Last Login', 'Score', 'Time Taken (mm:ss)']

ques_summary = df_test_data.groupby('question_id').agg(
    total_score=('mark', 'sum'),
    total_attempts=('attempt','sum')
).reset_index()
ques_summary['percentage']=(ques_summary['total_score']/ques_summary['total_attempts']*100).astype('int64')
ques_summary=ques_summary.drop(['total_score','total_attempts'],axis=1)
ques_summary.columns=['Question Number', 'Performance']
ques_summary['Question Number'] = [f'Q{i+1}' for i in range(ques_summary.shape[0])]
ques_summary=ques_summary.transpose()
ques_summary.reset_index(inplace=True)



from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from time import localtime, strftime

def create_watermark(c):
    c.saveState()
    #c.translate(1 * inch, 1 * inch)  # for margin
    c.rotate(45)
    c.setFillColorCMYK(0, 0, 0, 0.08)
    c.setFont('Times-Bold', 100)
    c.drawString(2.8 * inch, 0.4 * inch, 'Learn Basics')
    c.restoreState()

def create_header_footer(c):
    #c.translate(1 * inch, 1 * inch)
    c.setStrokeColor('black')
    c.setLineWidth(2)
    c.line(0.2 * inch, 10 * inch, 8.3 * inch, 10 * inch)
    c.line(0.2 * inch, 0.5 * inch, 8.3* inch, 0.5 * inch)
    c.setFillColor('black')
    c.setFont('Times-Bold', 20)
    c.drawString(180, 750 , "Learn Basics - Learn Basics School")
    c.setFillColor('black')
    c.setFont('Times-Bold', 13)
    c.drawString(15, 18, "Learn Basics")
    c.setFillColor('black')
    c.setFont('Times-Bold', 13)
    c.drawString(485, 18, strftime("%Y-%m-%d %H:%M:%S", localtime()))
    c.drawImage('logo.jpg', 0 * inch, 10.05 * inch, width=2 * inch, height=1 * inch)
    #c.showPage()

def create_table(data):
    class_performance_data = [data.columns.tolist()] + data.values.tolist()
    c_width = [1.5*inch, 1*inch, 1*inch, 1*inch, 1.5*inch]
    t = Table(class_performance_data, rowHeights=20, colWidths=c_width)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ])
    for i, row in enumerate(class_performance_data[1:], start=1):
        if 'Absent' in row[3]:
            style.add('SPAN', (3, i), (4, i))
            style.add('TEXTCOLOR', (3, i), (3, i), colors.red)

    t.setStyle(style)
    return t

def create_table1(data):
    #ques_data = [data.columns.tolist()] + data.values.tolist()
    table_data = [data.columns.tolist()] + data.values.tolist()
    
    c_width = [1.5*inch,1*inch]
    t = Table(table_data[1:], rowHeights=None, colWidths=c_width)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ])
    t.setStyle(style)
    return t

def para1():
    data = [
        [Paragraph(f'<b>Class:</b> {class_section}'), 
         Paragraph(f'<b>Subject:</b> {subject}'), 
         Paragraph(f'<b>Chapter Name:</b> {chapter_name}')],
        [Paragraph(f'<b>Test Name:</b> {test_name}'), 
         Paragraph(f'<b>Start Time:</b> {start_time}'), 
         Paragraph(f'<b>End Time:</b> {end_time}')]
    ]
    table = Table(data, colWidths=[170,200,230])
    return table

def para2():
    data = [
        [Paragraph(f'<b>Chapter Name:</b> {chapter_name}')],
        [Paragraph(f'<b>Concept Covered:</b> {concept}')], 
        [Paragraph(f'<b>Test Name:</b> {test_name}')], 
        [Paragraph(f'<b>Test Link:</b> {test_link}')]
    ]
    table = Table(data, colWidths=[600],rowHeights=20)
    return table


def create_pdf(mypath):
    doc = SimpleDocTemplate(mypath, pagesize=letter)
    elements = []
    
    # Create tables
    table1 = create_table(class_performance)
    table2 = create_table1(ques_summary)
    para_1= para1()
    para_2 = para2()

    elements.append(para_1)
    elements.append(Spacer(0, 0.3 * inch))
    elements.append(table1)
    elements.append(PageBreak())
    elements.append(para_2)
    elements.append(Spacer(0, 0.3 * inch))
    elements.append(table2)
    
    # Build the PDF with the elements and canvas
    doc.build(elements, onFirstPage=add_canvas, onLaterPages=add_canvas)

def add_canvas(c, doc):
    create_watermark(c)
    create_header_footer(c)

mypath = "finaldoc.pdf"
create_pdf(mypath)



