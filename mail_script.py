import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg.set_content('Please find attached Assignment 1 for AI Engineering 101.')

msg['Subject'] = 'Chinmay C Bhat - Intelligent AI Agents & RAG Systems for Real-World Applications - Week 1/Day 1'
msg['From'] = 'jules@example.com'
msg['To'] = 'karthikd@isparklearning.com'
msg['Cc'] = 'internships@isparklearning.com'

with open('Assignment_1.pdf', 'rb') as f:
    pdf_data = f.read()

msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename='Assignment_1.pdf')

# Cannot actually send without SMTP server, so we'll just save it to a file
with open('email.eml', 'wb') as f:
    f.write(bytes(msg))

print("Email saved to email.eml")
