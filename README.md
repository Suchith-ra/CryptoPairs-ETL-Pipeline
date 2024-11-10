# Cryptocurrency ETL Pipeline

This project is an automated **ETL pipeline** built using **Apache Airflow** that pulls real-time cryptocurrency data from **Binance** and loads it into a **MySQL** database for analysis and storage. The pipeline extracts the current ask and bid prices, sizes, and timestamps for various cryptocurrency pairs using Binance's 24hr Ticker API.

## Project Overview

The pipeline is designed to:
1. **Extract** real-time market data (ask price, bid price, ask size, bid size, timestamps) for all available trading pairs from the **Binance API**.
2. **Transform** the data into a structured format suitable for storage and analysis. ( Not a necessary step, but used when there are data manipulations involved )
3. **Load** the transformed data into a MySQL database.

### Key Features:
- Fetches ask/bid price and sizes from Binance.
- Handles real-time market data.
- Stores historical market data in a MySQL database.

## Project Structure

- **dags/**: Contains the Airflow Directed Acyclic Graph (DAG) Python files. The main pipeline script (`crypto_etl.py`) is defined here.
- **Dockerfile**: Defines the Docker image used for the Airflow environment.
- **requirements.txt**: List of Python dependencies required for the project.
- **airflow_settings.yaml**: Configuration for Airflow connections, variables, and pools.
- **docker-compose.yml**: Configures and orchestrates Docker containers for running Apache Airflow with MySQL.

## Requirements

- **Apache Airflow** for orchestrating the ETL pipeline.
- **MySQL** for storing the extracted data.
- **Binance API** for extracting market data.

## Data Sources

This project uses the **24hr Ticker API** from **Binance** to fetch real-time market data. The key data points are:
- **Ask Price**: The lowest price at which an asset is available for purchase.
- **Bid Price**: The highest price at which an asset is available for sale.
- **Ask Size**: The amount available for purchase at the ask price.
- **Bid Size**: The amount available for sale at the bid price.
- **Timestamp**: The time the data was recorded.

## Database Schema

The following table is used to store the market data:
- **binance_order_books**
    - **id**: Unique identifier for the symbol.
    - **symbol**: The cryptocurrency pair (e.g., BTCUSDT).
    - **ask_price**: Lowest price at which an asset is available for purchase.
    - **ask_size**: Amount available at the ask price.
    - **bid_price**: Highest price at which an asset is available for sale.
    - **bid_size**: Amount available at the bid price.
    - **time_coinapi**: Timestamp of the data recorded.
    - **time_exchange**: Timestamp of the Binance exchange data.
    - **ts**: Timestamp of the database entry.

## Running the Project Locally

1. **Start MySQL Container**:
    - Ensure that the MySQL Docker container is running.
    - Expose port `3306` or any custom port if required.

2. **Set Up Airflow**:
    - Install **Apache Airflow** locally, or use the provided Docker image to start the Airflow services:
      ```bash
      docker-compose up
      ```
    - This will start the Airflow webserver, scheduler, and worker containers.

3. **Access Airflow Web UI**:
    - Navigate to [http://localhost:8080](http://localhost:8080) to access the Airflow UI.
    - Login with the credentials you set up (default: `admin` / `admin`).

4. **Verify the DAG**:
    - Once the Airflow webserver is running, you should see the `binance_crypto_etl_pipeline` DAG in the UI.
    - Trigger the DAG to start the ETL process.

## DAG Workflow

The **ETL pipeline** consists of the following steps:

1. **Extract Binance Symbols**:
    - This task fetches a list of all active trading symbols from Binance using the `/exchangeInfo` API.

2. **Extract 24hr Ticker Price Data**:
    - This task pulls real-time market data (ask price, bid price, ask size, bid size, and timestamps) for each symbol using the `/ticker/24hr` API.

3. **Transform Data**:
    - The raw data is cleaned and transformed into a structured format for easy insertion into MySQL.

4. **Load Data into MySQL**:
    - The transformed data is inserted into a MySQL database table (`binance_24hr_ticker_data`).

