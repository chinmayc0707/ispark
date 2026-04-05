import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

# Create the email message
msg = MIMEMultipart()
msg['From'] = 'your_email@example.com'  # Replace with actual email
msg['To'] = 'karthikd@isparklearning.com'
msg['Cc'] = 'internships@isparklearning.com'
msg['Subject'] = 'AI System Design Assignment - [Your Name] - [Course Name] - Week [X]/Day [Y]'

body = """Dear Reviewer,

Please find attached my completed Assignment 2 covering the design and partial implementation of a production-grade agentic AI system for the Financial Research domain.

The attached PDF ('Assignment_2.pdf') includes all five parts, containing:
- The hand-drawn style architecture diagram and explanations (Part 1)
- The token budget allocation and RAG/Memory integration details (Part 2)
- The tool definitions, code snippets, and ReAct reasoning traces (Part 3)
- The hallucination failure testing results (Part 4)
- The system known limitations documentation (Part 5)

I have also attached the Python files used to generate the code sections and the diagram image file.

Thank you,
[Your Name]
"""
msg.attach(MIMEText(body, 'plain'))

# Attach PDF
with open("assignment/Assignment_2.pdf", "rb") as f:
    pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
    pdf_attachment.add_header('Content-Disposition', 'attachment', filename="Assignment_2.pdf")
    msg.attach(pdf_attachment)

# Attach Code Files
files_to_attach = [
    "assignment/part2_query_enrichment.py",
    "assignment/part3_react_loop.py",
    "assignment/architecture_diagram.png"
]

for filename in files_to_attach:
    with open(filename, "rb") as f:
        attachment = MIMEApplication(f.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
        msg.attach(attachment)

print("Email composed. In a real environment, you would use smtplib to send this.")
