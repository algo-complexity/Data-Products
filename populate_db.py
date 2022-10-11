import csv
import argparse
from sqlalchemy.orm import Session
from db.connector import engine
from db.db import Country, Exchange

parser = argparse.ArgumentParser(
    prog="Populate DB Script", description="Import base data into db"
)
parser.add_argument(
    "country_filepath",
    type=str,
    help="file to import countries from",
    default="countries.csv",
)
parser.add_argument(
    "mic_filepath", type=str, help="file to import MIC codes from", default="mic.csv"
)
args = parser.parse_args()

with Session(engine) as session:
    with open(args.country_filepath) as f:
        reader = csv.DictReader(f)
        values = {
            row["alpha-2"]: Country(
                name=row["name"], alpha2=row["alpha-2"], alpha3=row["alpha-3"]
            )
            for row in reader
        }
        session.add_all(list(values.values()))
    session.commit()

    with open(args.mic_filepath) as f:
        reader = csv.DictReader(f)
        values = [
            Exchange(
                short_name=row["OPERATING MIC"],
                name=row["NAME-INSTITUTION DESCRIPTION"],
                country=values[row["ISO COUNTRY CODE (ISO 3166)"]].id,
            )
            for row in reader
            if row["ISO COUNTRY CODE (ISO 3166)"] in values.keys()
        ]
        session.add_all(values)
    session.commit()
