from flask import Flask, render_template, request
from alpha_vantage.foreignexchange import ForeignExchange
import os
import ccxt
import requests

app = Flask(__name__)

# Function to fetch news for different categories


def get_news(category):
    api_key = '3cc7955c26444fb8b59bb9ffa640ddb4'
    url = f'https://newsapi.org/v2/everything?q={category}&apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles')
        return articles[:7]  # Return first 7 articles
    else:
        return None


# Base URL for the ExchangeRate-API
EXCHANGE_RATE_API_BASE_URL = 'https://api.exchangerate-api.com/v4/latest/'

# Initialize Binance API
exchange = ccxt.binance()

# Initialize the Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '22MAMWKPFIG9RROL')
alpha_vantage_fx = ForeignExchange(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')

# Define dictionaries for financial instruments
coins = {
    'BTC/USDT': 'Bitcoin (BTC)',
    'ETH/USDT': 'Ethereum (ETH)',
    'XRP/USDT': 'Ripple (XRP)',
    'LTC/USDT': 'Litecoin (LTC)',
    'ARB/USDT': 'Arbitrum (ARB)',
    'MATIC/USDT': 'Polygon (MATIC)',
    'SHIB/USDT': 'Shiba Inu (SHIB)',
    'TENUP/USDT': 'Tenup (TENUP)'
}

stock_symbols = {
    'AAPL': 'Apple Inc.(AAPL)',
    'GOOGL': 'Alphabet Inc. (GOOGL)',
    'MSFT': 'Microsoft Corporation (MSFT)',
    'NFLX': 'Netflix Inc. (NFLX)',
    'NVDA': 'Nvidia Corporation (NVDA)',
    'INTC': 'Intel Corporation (INTC)'
}

indices = {
    'DJI': 'Dow Jones Industrial Average (DJI)',
    'INX': 'S&P 500 (INX)',
    'SPX': 'S&P 500 Index (SPX)',
    'NDQ': 'NASDAQ-100 Index (NDQ)',
    'VIX': 'CBOE Volatility Index (VIX)',
    'DXY': 'US Dollar Index (DXY)'
}

spots = {
    'XAUUSD': 'Gold/USD (XAU)',
    'XAGUSD': 'Silver/USD (XAG)'
}

# The Home index route


@app.route('/')
def index():
    crypto_news = get_news('crypto')
    stocks_news = get_news('stocks')
    indices_news = get_news('indices')
    spot_news = get_news('spot')
    futures_news = get_news('futures')
    return render_template('index.html',
                           crypto_news=crypto_news,
                           stocks_news=stocks_news,
                           indices_news=indices_news,
                           spot_news=spot_news,
                           futures_news=futures_news)

# CryptoCurrency Pnl calculator


@app.route('/crypto', methods=['GET', 'POST'])
def crypto():
    pnl = None
    current_price = None

    if request.method == 'POST':
        coin_pair = request.form['coin']
        entry_price = float(request.form['entry_price'])
        investment_amount = float(request.form['investment_amount'])

        mark_price = request.form['mark_price']

        if not mark_price:  # If no mark price provided by user, fetch from Binance
            try:
                ticker = exchange.fetch_ticker(coin_pair)
                mark_price = ticker['last']
            except Exception as e:
                return f"Error fetching data from Binance: {e}", 500
        else:
            mark_price = float(mark_price)

        # Calculate the quantity of the asset bought
        quantity = investment_amount / entry_price

        # Calculate the PnL
        pnl = (mark_price - entry_price) * quantity
        current_price = mark_price if isinstance(mark_price, float) else None

    return render_template('crypto.html', pnl=pnl, coins=coins, current_price=current_price)

# Stocks Pnl calculator


@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    pnl = None
    current_price = None

    if request.method == 'POST':
        stock_symbol = request.form['stock']
        entry_price = float(request.form['entry_price'])
        investment_amount = float(request.form['investment_amount'])

        mark_price = request.form['mark_price']

        if not mark_price:  # If no mark price provided by user, fetch from Alpha Vantage
            try:
                data, _ = alpha_vantage_fx.get_currency_exchange_rate(
                    from_currency=stock_symbol, to_currency='USD')
                mark_price = float(data['5. Exchange Rate'])
            except Exception as e:
                return f"Error fetching data from Alpha Vantage: {e}", 500
        else:
            mark_price = float(mark_price)

        # Calculate the quantity of the asset bought
        quantity = investment_amount / entry_price

        # Calculate the PnL
        pnl = (mark_price - entry_price) * quantity
        current_price = mark_price if isinstance(mark_price, float) else None

    return render_template('stocks.html', pnl=pnl, stock_symbols=stock_symbols, current_price=current_price)

# Futures Contracts Pnl calculator


@app.route('/futures', methods=['GET', 'POST'])
def futures():
    pnl = None
    current_price = None

    if request.method == 'POST':
        coin_pair = request.form['coin']
        entry_price = float(request.form['entry_price'])
        investment_amount = float(request.form['investment_amount'])
        leverage = float(request.form['leverage'])

        mark_price = request.form['mark_price']

        if not mark_price:  # If no mark price provided by user, fetch from Binance
            try:
                ticker = exchange.fetch_ticker(coin_pair)
                mark_price = ticker['last']
            except Exception as e:
                return f"Error fetching data from Binance: {e}", 500
        else:
            mark_price = float(mark_price)

        # Calculate the quantity of the asset bought with leverage
        quantity = (investment_amount * leverage) / entry_price

        # Calculate the PnL with leverage
        pnl = (mark_price - entry_price) * quantity
        current_price = mark_price if isinstance(mark_price, float) else None

    return render_template('futures.html', pnl=pnl, coins=coins, current_price=current_price)

# Indices Pnl calculator


@app.route('/indices', methods=['GET', 'POST'])
def calculate_indices():
    pnl = None
    current_price = None

    if request.method == 'POST':
        index_symbol = request.form['index']
        entry_price = float(request.form['entry_price'])
        investment_amount = float(request.form['investment_amount'])

        mark_price = request.form['mark_price']

        if not mark_price:  # If no mark price provided by user, fetch from Alpha Vantage
            try:
                data, _ = alpha_vantage_fx.get_currency_exchange_rate(
                    from_currency=index_symbol, to_currency='USD')
                mark_price = float(data['5. Exchange Rate'])
            except Exception as e:
                return f"Error fetching data from Alpha Vantage: {e}", 500
        else:
            mark_price = float(mark_price)

        # Calculate the quantity of the asset bought
        quantity = investment_amount / entry_price

        # Calculate the PnL
        pnl = (mark_price - entry_price) * quantity
        current_price = mark_price if isinstance(mark_price, float) else None

    return render_template('indices.html', pnl=pnl, indices=indices, current_price=current_price)

# Spot Pnl calculator


@app.route('/spot', methods=['GET', 'POST'])
def spot():
    pnl = None
    current_price = None

    if request.method == 'POST':
        spot_symbol = request.form['instrument']
        entry_price = float(request.form['entry_price'])
        investment_amount = float(request.form['investment_amount'])

        mark_price = request.form['mark_price']

        if not mark_price:  # If no mark price provided by user, fetch from Alpha Vantage
            try:
                # Example: Fetching exchange rate for spot symbol
                data, _ = alpha_vantage_fx.get_currency_exchange_rate(
                    from_currency='USD', to_currency=spot_symbol[:3])
                mark_price = float(data['5. Exchange Rate'])
            except Exception as e:
                return f"Error fetching data from Alpha Vantage: {e}", 500
        else:
            mark_price = float(mark_price)

        # Calculate the quantity of the asset bought
        quantity = investment_amount / entry_price

        # Calculate the PnL
        pnl = (mark_price - entry_price) * quantity
        current_price = mark_price if isinstance(mark_price, float) else None

    return render_template('spot.html', pnl=pnl, spots=spots, current_price=current_price)

# Currency Converter


@app.route('/converter', methods=['GET', 'POST'])
def converter():

    # Currencies dictionary with their full names and codes
    currencies = {
        'USD': 'US Dollar (USD)',
        'EUR': 'Euro (EUR)',
        'GBP': 'British Pound (GBP)',
        'CAD': 'Canadian Dollar (CAD)',
        'AUD': 'Australian Dollar (AUD)',
        'JPY': 'Japanese Yen (JPY)',
        'INR': 'Indian Rupee (INR)',
        'PKR': 'Pakistani Rupee (PKR)'
    }

    if request.method == 'POST':
        amount = float(request.form['amount'])
        base_currency = request.form['base_currency']
        target_currency = request.form['target_currency']

        if base_currency == target_currency:
            error_message = "Error: Base currency and target currency must be different."
            return render_template('converter.html', currencies=currencies, error_message=error_message)

        try:
            # Make API request to fetch exchange rates
            url = f'{EXCHANGE_RATE_API_BASE_URL}{base_currency}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and target_currency in data['rates']:
                    exchange_rate = data['rates'][target_currency]
                    converted_amount = amount * exchange_rate
                    return render_template('converter.html', currencies=currencies, converted_amount=converted_amount)
                else:
                    error_message = f"Error: Conversion rate for {
                        base_currency} to {target_currency} not found."
                    return render_template('converter.html', currencies=currencies, error_message=error_message)
            else:
                error_message = f"Error: Failed to fetch data from API (Status Code: {
                    response.status_code})"
                return render_template('converter.html', currencies=currencies, error_message=error_message)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            return render_template('converter.html', currencies=currencies, error_message=error_message)

    # If GET request, render the form with initial data
    return render_template('converter.html', currencies=currencies, converted_amount=None)


if __name__ == '__main__':
    app.run(debug=True)
