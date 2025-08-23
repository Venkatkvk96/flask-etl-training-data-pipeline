import pandas as pd
import pymysql
import smtplib
import warnings
from email.message import EmailMessage
from email.utils import formatdate
from email.mime.application import MIMEApplication
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT, EMAIL_USER, EMAIL_PASSWORD

warnings.filterwarnings("ignore", category=UserWarning, module="pandas.io.sql")

# DB Connection
connection = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
    port=MYSQL_PORT
)

# Fetch Today's Training Data
query = """
SELECT Training_Date, Department, Course, Training_Mode, Training_Hours
FROM training_employee_records
WHERE Training_Date = CURDATE();
"""

df = pd.read_sql(query, connection)
connection.close()

# Prepare Email
msg = EmailMessage()
msg['Subject'] = "Daily Training Report"
msg['From'] = EMAIL_USER
msg['To'] = "venkatkvk96@gmail.com"
msg['Date'] = formatdate(localtime=True)

if df.empty:
    # Handle empty dataset
    msg.set_content("No training sessions recorded today.")
    msg.add_alternative(f"""
    <html><body>
    <p>Hello Team,</p>
    <p>No training sessions were recorded for today.</p>
    <p>Regards,<br>HRT Automated System</p>
    </body></html>
    """, subtype='html')
else:
    # Save to Excel
    file_path = "daily_training_report.xlsx"
    df.to_excel(file_path, index=False)

    html_table = df.to_html(index=False)
    msg.set_content("Attached is the daily training summary.")
    msg.add_alternative(f"""
    <html><body>
    <p>Hello Team,</p>
    <p>Here is the training summary for today:</p>
    {html_table}
    <p>Regards,<br>HRT Automated System</p>
    </body></html>
    """, subtype='html')

    # Attach Excel
    with open(file_path, 'rb') as f:
        part = MIMEApplication(f.read(), Name="Training_Report.xlsx")
        part['Content-Disposition'] = 'attachment; filename="Training_Report.xlsx"'
        msg.attach(part)

# Send Email (Gmail SMTP)
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    server.send_message(msg)

print("Email sent successfully.")
