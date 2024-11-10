from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.decorators import task
from airflow.utils.dates import days_ago
import pandas as pd

# MySQL connection details
MYSQL_CONN_ID = 'MySQL80'  # Update with your connection ID if different

# Binance connection details
BINANCE_API_URL = "https://api.binance.com/api/v3"

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

with DAG(
    dag_id='binance_crypto_etl_pipeline',
    default_args=default_args,
    schedule_interval='@daily',  
    catchup=False,
) as dag:

    @task()
    def extract_binance_symbols():
        """Extract all available symbols from Binance API using Airflow Connection."""

        http_hook = HttpHook(http_conn_id='api_binance', method='GET')

        endpoint = '/exchangeInfo'
        response = http_hook.run(endpoint)

        if response.status_code == 200:
            exchange_info = response.json()
            symbols = [symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['status'] == 'TRADING']
            return symbols
        else:
            raise Exception(f"Failed to fetch symbol list: {response.status_code}")

    @task()
    def extract_24hr_ticker_price(symbols):
        """Extract order book data for all symbols from Binance API."""
        
        http_hook = HttpHook(http_conn_id='api_binance', method='GET')

        all_data = []

        for symbol in symbols:
            endpoint = f'/ticker/24hr?symbol={symbol}' 

            response = http_hook.run(endpoint)

            if response.status_code == 200:
                ticker_info = response.json()

                entry = {
                    'id': symbol,
                    'symbol': symbol,
                    'ask_price': float(ticker_info['askPrice']) if ticker_info['askPrice'] else None,
                    'ask_size': float(ticker_info['askQty']) if ticker_info['askQty'] else None,
                    'bid_price': float(ticker_info['bidPrice']) if ticker_info['bidPrice'] else None,
                    'bid_size': float(ticker_info['bidQty']) if ticker_info['bidQty'] else None,
                    'ts': pd.to_datetime('now').isoformat()
                }

                all_data.append(entry)
            else:
                print(f"Failed to fetch order book for {symbol}: {response.status_code}")

        return all_data

    @task()
    def transform_binance_data(order_book_data):
        """Transform the order book data into the desired structure."""
        transformed_data = []

        for entry in order_book_data:
            transformed_entry = {
                'id': entry['id'],
                'symbol': entry['symbol'],
                'ask_price': entry['ask_price'],
                'ask_size': entry['ask_size'],
                'bid_price': entry['bid_price'],
                'bid_size': entry['bid_size'],
                'time_coinapi': entry['ts'],
                'time_exchange': entry['ts'],
                'ts': entry['ts']
            }
            transformed_data.append(transformed_entry)

        return transformed_data

    @task()
    def load_binance_data(transformed_data):
        """Load transformed cryptocurrency data into MySQL."""
        
        mysql_hook = MySqlHook(mysql_conn_id=MYSQL_CONN_ID)
        conn = mysql_hook.get_conn()
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS binance_24hr_ticker_data (
            id VARCHAR(50),
            symbol VARCHAR(50),
            ask_price FLOAT,
            ask_size FLOAT,
            bid_price FLOAT,
            bid_size FLOAT,
            time_coinapi TIMESTAMP,
            time_exchange TIMESTAMP,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Insert transformed data into the table
        for data in transformed_data:
            cursor.execute("""
            INSERT INTO binance_24hr_ticker_data (id, symbol, ask_price, ask_size, bid_price, bid_size, time_coinapi, time_exchange, ts)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['id'], 
                data['symbol'], 
                data['ask_price'], 
                data['ask_size'], 
                data['bid_price'], 
                data['bid_size'], 
                data['time_coinapi'], 
                data['time_exchange'], 
                data['ts']
            ))

        conn.commit()
        cursor.close()

    # DAG Workflow - ETL Pipeline
    symbols = extract_binance_symbols()
    order_book_data = extract_24hr_ticker_price(symbols)
    transformed_data = transform_binance_data(order_book_data)
    load_binance_data(transformed_data)
