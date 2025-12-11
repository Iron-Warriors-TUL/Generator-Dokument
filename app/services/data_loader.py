import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_csv_data(filename):
    file_path = os.path.join(DATA_DIR, f"{filename}.csv")

    if not os.path.exists(file_path):
        return []

    try:
        df = pd.read_csv(file_path)
        df = df.dropna(how="all")
        return df.to_dict(orient="records")
    except:
        return []


def get_students():
    return load_csv_data("students")


def get_signers():
    return load_csv_data("signers")
