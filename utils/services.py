from sqlalchemy import Table, schema
from sqlalchemy.orm import sessionmaker


def bulk_upload(engine, orig_df, dest_table):
    # Set up connection
    conn = engine.connect()

    # The orient='records' is the key of this, it allows to align with the format mentioned in the doc to insert in bulks.
    write_list = orig_df.to_dict(orient="records")

    metadata = schema.MetaData(bind=engine)
    table = Table(dest_table, metadata, autoload=True)

    # Open the session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Inser the dataframe into the database in one bulk
    conn.execute(table.insert(), write_list)

    # Commit the changes
    session.commit()

    # Close the session
    session.close()
