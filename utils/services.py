from typing import Optional
from sqlalchemy import Table, schema, or_
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session
from threading import Timer

from db.connector import engine
from db.db import Exchange, Price, Stock, StockPrice

from utils.yahoo import (
    get_yahoo_autocomplete_stock_ticker,
    get_yahoo_stock_price,
    get_yahoo_stock_metadata,
)


def debounce(wait):
    """Postpone a functions execution until after some time has elapsed

    :type wait: int
    :param wait: The amount of Seconds to wait before the next call can execute.
    """

    def decorator(fun):
        def debounced(*args, **kwargs):
            def call_it():
                fun(*args, **kwargs)

            try:
                debounced.t.cancel()
            except AttributeError:
                pass

            debounced.t = Timer(wait, call_it)
            debounced.t.start()

        return debounced

    return decorator


def bulk_upload(orig_df, dest_table) -> list[Row]:
    # Set up connection
    conn = engine.connect()

    # The orient='records' is the key of this, it allows to align with the format mentioned in the doc to insert in bulks.
    write_list = orig_df.to_dict(orient="records")

    metadata = schema.MetaData(bind=engine)
    table = Table(dest_table.__tablename__, metadata, autoload=True)

    with Session(engine, expire_on_commit=False) as session:
        # Insert the dataframe into the database in one bulk
        conn.execute(table.insert(), write_list)
        # Query to return rows as insert does not
        results = session.query(dest_table)

        # Commit the changes
        session.commit()

    return results.all()


def get_all_stocks() -> list[Stock]:
    with Session(engine) as session:
        results = session.query(Stock)
    return results


def get_stock_with_search(search: str) -> list[Stock]:
    with Session(engine) as session:
        results = session.query(Stock).filter(
            or_(Stock.ticker.ilike(f"%{search}%"), Stock.name.ilike(f"%{search}%"))
        )
    return results


@debounce(5)
def get_stock_from_yahoo(search: str) -> Optional[Stock]:
    ticker = get_yahoo_autocomplete_stock_ticker(search)
    stock = None
    if ticker:
        metadata = get_yahoo_stock_metadata(ticker)
        with Session(engine, expire_on_commit=False) as session:
            value = metadata["exchange"]["short_name"]
            exchange: Exchange = (
                session.query(Exchange)
                .filter(Exchange.short_name.like(f"%{value}%"))
                .first()
            )
            if exchange:
                # BUG: This code adds duplicates we need to prevent that
                stock = Stock(**metadata["stock"], exchange_id=exchange.id)
                session.add(stock)
                session.commit()

        # TODO: Add Extra code to calculate indicators
        if stock:
            stock_data = get_yahoo_stock_price(ticker)
            rows = bulk_upload(stock_data, Price)
            stock_prices = [
                StockPrice(stock_id=stock.id, price_id=row.id) for row in rows
            ]
            with Session(engine) as session:
                session.add_all(stock_prices)
                session.commit()
    return stock
