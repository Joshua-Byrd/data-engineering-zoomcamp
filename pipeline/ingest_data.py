import click

@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5432, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    import pandas as pd
    # SQLAlchemy is an ORM tool for python
    from sqlalchemy import create_engine
    from tqdm.auto import tqdm

    dtype = {
        "VendorID": "Int64",
        "passenger_count": "Int64",
        "trip_distance": "float64",
        "RatecodeID": "Int64",
        "store_and_fwd_flag": "string",
        "PULocationID": "Int64",
        "DOLocationID": "Int64",
        "payment_type": "Int64",
        "fare_amount": "float64",
        "extra": "float64",
        "mta_tax": "float64",
        "tip_amount": "float64",
        "tolls_amount": "float64",
        "improvement_surcharge": "float64",
        "total_amount": "float64",
        "congestion_surcharge": "float64"
    }

    parse_dates = [
        'tpep_pickup_datetime',
        'tpep_dropoff_datetime'
    ]
    df = pd.read_csv('ny_taxi_postgres_data/yellow_tripdata_2021-01.csv.gz', dtype = dtype, parse_dates=parse_dates)

    # create the databaseconnection
    engine_string = f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    engine = create_engine(engine_string)

    # get DDL schema
    print(pd.io.sql.get_schema(df, name=target_table, con=engine))

    # create the table without any data. Because its passing in 0 to the df.head() function
    # it only retrieves the headers, no rows, and uses them to create the table.
    df.head(n=0).to_sql(name=target_table, con=engine, if_exists='replace')

    
    # read_csv can act as an iterator to read the data in in chunks
    df_iter = pd.read_csv(
        'ny_taxi_postgres_data/yellow_tripdata_2021-01.csv.gz',
        dtype = dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=10000
    )

    # inserting the rows into the table, one chunk at a time
    first = True # flag to create the table if this is the first chunk

    #tdqm adds a progresss bar
    for df_chunk in tqdm(df_iter):
        if first:
            # create the table on the first chunk
            df.head(0).to_sql(
                name='yellow_taxi_data',
                con=engine,
                if_exists='replace'
            )
            first=False
            print('table created')

        # insert chunk
        df_chunk.to_sql(
            name='yellow_taxi_data',
            con=engine,
            if_exists='append'
        )

        print(f'Inserted chunk of length: {len(df_chunk)}')
    
if __name__ == '__main__':
    run()





