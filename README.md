# Crypto Dashboard

## Project Description

At the core of this project is the development of a real-time cryptocurrency dashboard that fetches and visualizes cryptocurrency market data. The program extracts data from various APIs including Binance, CoinGecko, and Blockchain, and presents the data using interactive visualizations. The primary objectives of this project are to:

- Build a real-time dashboard for analyzing cryptocurrency market data.
- Display important metrics like 24h high, low, price changes, volume, and dominance.
- Allow users to select different cryptocurrencies and timeframes to analyze.
- Visualize historical price data using interactive charts.
- Provide insights into market trends, including open interest and cryptocurrency dominance.

## Technologies Used

**Programming Languages**: Python  
**Libraries**: Streamlit, Pandas, Requests, Plotly  
**Tools**: Binance API, CoinGecko API, Blockchain API  

## Data Extraction

Data is extracted from various cryptocurrency market APIs:
- **Binance API**: Used to fetch historical market data and real-time price data.
- **CoinGecko API**: Used to fetch global cryptocurrency dominance data.
- **Blockchain API**: Used to fetch Bitcoin blockchain statistics like difficulty and hashrate.
- **Binance Futures API**: Used to get open interest data for selected cryptocurrency pairs.

The result from each API call is processed and cleaned, and the data is then presented in real-time on the dashboard.

## Data Preprocessing

Python and Pandas are used to transform the extracted data. This includes:
- Parsing timestamps and converting them to readable datetime formats.
- Handling missing or inconsistent data by filtering and cleaning.
- Aggregating market data and preparing it for visualization.

## Data Loading

The extracted data is used to update the dashboard in real-time. The data is not loaded into a traditional database but is instead processed and displayed dynamically on the Streamlit dashboard.

## Analysis and Insights

Real-time metrics are calculated and displayed for the selected cryptocurrency pair, including:
- 24h high and low prices
- 24h volume in both the cryptocurrency and USD terms
- Market dominance and open interest data

## How to Use the Project

1. Clone the repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the Streamlit app using the command `streamlit run app.py`.
4. Select the cryptocurrency and timeframe from the sidebar to see real-time data and interactive visualizations.
5. Or simply go to this link: https://realtimecryptodashboard.streamlit.app/

## Project Structure

- **app.py**: Streamlit application for fetching and displaying real-time cryptocurrency data.
- **requirements.txt**: List of Python dependencies for the project.
- **README.md**: You're here!
- **utils.py**: Helper functions for API calls and data processing.

## Contributing

If you're interested in collaborating on this project, please feel free to reach out and discuss potential contributions.

## License

This project is open source under the [TBD] license. You can use and modify the code as needed.

## Contact Information

You can reach out to [Your Contact Information] for questions, collaboration, or more information about this project.
