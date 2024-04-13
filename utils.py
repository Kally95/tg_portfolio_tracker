def format_trade_data(portfolio_data_list):
    messages = []
    for data in portfolio_data_list:
        message = (
            f"Symbol: {data['symbol']}\n"
            f"Price paid ($): {data['price']}\n"
            f"Total amount of asset: {data['total_amount']}\n"
            f"Current price ($): {data['current_price']}\n"
            f"Calculated Win/Loss: {data['win_loss']}%\n"
            "**********************\n"
        )
        messages.append(message)
    return "\n".join(messages)

async def format_losing_trade_data(losing_trades):
    losing = "Losers:"
    for trade in losing_trades:
        losing += f" {trade['symbol']}: {trade['win_loss']},"
    return losing.rstrip(',')

async def format_winning_trade_data(winning_trades):
    winning = "Winners:"
    for trade in winning_trades:
        winning += f" {trade['symbol']}: {trade['win_loss']},"
    return winning.rstrip(',')

