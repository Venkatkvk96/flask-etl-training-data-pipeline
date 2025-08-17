import os
from datetime import datetime
import pandas as pd
import mysql.connector
from flask import Flask, request, render_template
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

@app.route("/")
def home():
    return render_template("uploads.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    if file and file.filename.endswith(".csv"):
        df = pd.read_csv(file)

        print("Columns in CSV:", list(df.columns))
        print("First row:", df.iloc[0].to_dict())

        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO training_employee_records (
                Employee_ID, Employee_Name, Department, Gender, Training_Date,
                Training_Category, Course, Training_Mode, No_of_Training_session, Training_Hours
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Employee_Name = VALUES(Employee_Name),
                Department = VALUES(Department),
                Gender = VALUES(Gender),
                Training_Category = VALUES(Training_Category),
                Course = VALUES(Course),
                Training_Mode = VALUES(Training_Mode),
                No_of_Training_session = VALUES(No_of_Training_session),
                Training_Hours = VALUES(Training_Hours)
        """

        summary = {"inserted": 0, "updated": 0, "failed": 0}

        for _, row in df.iterrows():
            try:
                # Convert Training_Date to MySQL format
                training_date = datetime.strptime(row['Training_Date'], "%d-%m-%Y").strftime("%Y-%m-%d")

                values = (
                    row['Employee_ID'],
                    row['Employee_Name'],
                    row['Department'],
                    row['Gender'],
                    training_date,
                    row['Training_Category'],
                    row['Course'],
                    row['Training_Mode'],
                    int(row['No_of_Training_session']),
                    int(row['Training_Hours'])
                )

                cursor.execute(insert_query, values)
                if cursor.rowcount == 1:
                    summary["inserted"] += 1
                else:
                    summary["updated"] += 1

            except Exception as e:
                summary["failed"] += 1
                print(f"Error inserting row {row.to_dict()}: {e}")

        connection.commit()
        cursor.close()
        connection.close()

        result_msg = f"Upload Summary: {summary['inserted']} inserted, {summary['updated']} updated, {summary['failed']} failed."
        print(result_msg)
        return result_msg, 200

    return "Invalid file format. Please upload a CSV.", 400


if __name__ == "__main__":
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=True)
