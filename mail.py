

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email details
sender_email = "mollasheryfawaz@gmail.com"  # Replace with your Gmail address
receiver_email = "fawaz3762@yit.edu.in"  # Replace with the recipient's email
subject = "Test Email"
body = "This is a test email sent using Python."

# Create the email message
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

# SMTP server details for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587
email_address = "mollasheryfawaz@gmail.com"  # Replace with your Gmail address
email_password = "olhk hcnf oyow ibry"  # Replace with your Gmail App Password

# Connect to the SMTP server
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Upgrade the connection to secure
    server.login(email_address, email_password)

    # Send the email
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    server.quit()  # Close the connection