from kucoin.client import Market
from kucoin.client import Trade, User, Market

class TradeAnalyser:
    def __init__(self, api_key, api_secret, api_passphrase):
        self.client = User(key=api_key, secret=api_secret, passphrase=api_passphrase)
        self.trade_client = Trade(key=api_key, secret=api_secret, passphrase=api_passphrase)
        self.market_client = Market(key=api_key, secret=api_secret, passphrase=api_passphrase)
    
    def get_account_list(self):
        return self.client.get_account_list()
    
    def get_fill_list_for_currency(self, currency):
        fill_list = self.trade_client.get_fill_list(currency=currency, tradeType="TRADE")
        return fill_list['items']

    def get_ticker_info(self, symbol):
        ticker_info = self.market_client.get_ticker(symbol)
        return float(ticker_info['price'])

def calculate_gain_loss_percentage(current_price, price_paid):
    percentage_gain_loss = ((current_price - price_paid) / price_paid) * 100
    return percentage_gain_loss

def analyse_trades(trade_analyzer):
    processed_symbols = set()
    currency_of_interest = []
    account_list = trade_analyzer.get_account_list()
    portfolio_data_list = []

    for account in account_list:
        balance = float(account['balance'])
        if balance != 0:
            currency_of_interest.append(account['currency'])

    for currency in currency_of_interest:
        fill_list = trade_analyzer.get_fill_list_for_currency(currency)
        for item in fill_list:
            symbol = item['symbol']
            if symbol not in processed_symbols:
                current_price = trade_analyzer.get_ticker_info(symbol)
                price_paid = float(item['price'])
                win_loss_percentage = round(calculate_gain_loss_percentage(current_price, price_paid), 2)

                symbol_dict = {
                    'symbol': symbol,
                    'price': item['price'],
                    'total_amount': item['size'],
                    'current_price': current_price,
                    'win_loss': win_loss_percentage
                }

                portfolio_data_list.append(symbol_dict)
                processed_symbols.add(symbol)
    
    return portfolio_data_list