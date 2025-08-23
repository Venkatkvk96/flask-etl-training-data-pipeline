import os
import csv
import pandas as pd
from dateutil import parser
from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import config

# HTML path for waitress and flask
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Flask App Config
app = Flask(__name__, template_folder=TEMPLATE_FOLDER)
app.secret_key = config.SECRET_KEY

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ETL Functions
def extract_data(filepath):
    _, ext = os.path.splitext(filepath.lower())
    if ext == '.csv':
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            return list(reader)
    elif ext in ('.xls', '.xlsx'):
        df = pd.read_excel(filepath)
        return df.values.tolist()
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def transform_data(data):
    transformed = []
    for row in data:
        try:
            if len(row) > 4 and row[4]:
                parsed_date = parser.parse(str(row[4]))
                row[4] = parsed_date.strftime("%Y-%m-%d")
                transformed.append(row)
        except Exception as e:
            print(f"Skipped row: {row} --> {e}")
    return transformed

def load_data(rows):
    cur = mysql.connection.cursor()
    query = """
        INSERT INTO Employee_Details (
            Employee_ID, Employee_Name, Department, Gender, Training_Date,
            Training_Category, Course, Training_Mode, No_of_Training_session, Training_Hours
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            Employee_Name=VALUES(Employee_Name),
            Department=VALUES(Department),
            Gender=VALUES(Gender),
            Training_Date=VALUES(Training_Date),
            Training_Category=VALUES(Training_Category),
            Course=VALUES(Course),
            Training_Mode=VALUES(Training_Mode),
            No_of_Training_session=VALUES(No_of_Training_session),
            Training_Hours=VALUES(Training_Hours);
    """
    for row in rows:
        cur.execute(query, row)
    mysql.connection.commit()
    cur.close()

# FLASK Routes
@app.route('/')
def form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        flash('No file selected.')
        return redirect('/')

    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        raw_data = extract_data(filepath)
        cleaned_data = transform_data(raw_data)
        load_data(cleaned_data)
        flash('File uploaded and data inserted successfully!')
    except Exception as e:
        flash(f'Error: {e}')

    return redirect('/')
