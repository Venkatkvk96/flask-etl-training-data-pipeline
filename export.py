import pandas as pd
import mysql.connector
from datetime import datetime
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB


def export_employee_details(file_name="employee_details", file_format="csv"):
    """
    Exporting employee training records to CSV or Excel with today's date in filename.
    """
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )

        query = "SELECT * FROM Employee_Details"
        df = pd.read_sql(query, conn)

        today = datetime.today().strftime("%Y-%m-%d")
        if file_format.lower() == "csv":
            output_file = f"{file_name}_{today}.csv"
            df.to_csv(output_file, index=False)
        elif file_format.lower() in ["excel", "xlsx"]:
            output_file = f"{file_name}_{today}.xlsx"
            df.to_excel(output_file, index=False)
        else:
            raise ValueError("Unsupported file format. Use 'csv' or 'excel'.")

        print(f"Exported All records to {output_file} successfully.")

    except Exception as e:
        print(f"Export failed: {e}")

    finally:
        if conn.is_connected():
            conn.close()


if __name__ == "__main__":
    export_employee_details(file_name="employee_details", file_format="csv")
