from algo_trading.utilities.utils import setup, get_user_orders, ask_bid
from algo_trading.algorithms.kill_switch import kill_switch

target = 10  # Target PnL %
max_loss = 5  # Max loss %

def pnl_close(target, max_loss):
    """
    Check PnL of open positions and close them if they reach the target or max loss.
    """
    address, info, exchange, account = setup()

    openPositions, hasOpenPositions = get_user_orders(address, info)
    print(openPositions)

    if not hasOpenPositions:
        print('No open positions...')
        return

    results = []

    for position in openPositions:
        symbol = position['symbol']
        long = position['long']
        size = position['size']
        entry_price = float(position['entry_price'])
        leverage = float(position['leverage'])
        side = 'long' if long else 'short'
        current_price = ask_bid(symbol)[1]
        initial_pos_value = size * entry_price
        target_dollar_value = initial_pos_value * (target / 100)
        dollar_pnl = (current_price - entry_price) * size if long else (entry_price - current_price) * size

        print(f'Side: {side} | Entry: {entry_price} | Leverage: {leverage} | Current Price: {current_price}')

        diff = (current_price - entry_price) if long else (entry_price - current_price)
        try:
            perc = round(((diff / entry_price) * leverage) * 100, 10)
        except ZeroDivisionError:
            perc = 0

        print(f'PNL % for {symbol}: {perc}%')

        pnlclose = False
        in_pos = False

        if perc > 0:
            in_pos = True
            print(f'Unrealized PnL: ${dollar_pnl:.4f} | Target: ${target_dollar_value:.4f}')
            if dollar_pnl >= target_dollar_value:
                print(f'Target reached: {target}% -> Closing position...')
                kill_switch(address, info, exchange, symbol)
                pnlclose = True
            else:
                print(f'Target not reached: {target}%')
        elif perc < 0:
            in_pos = True
            if perc <= -abs(max_loss):  # This is the fix
                print(f'Max loss reached: {max_loss}% -> Closing position...')
                kill_switch(address, info, exchange, symbol)
                pnlclose = True
            else:
                print(f'Max loss not reached: {max_loss}%. Current PnL: {perc}%')
        else:
            print('PNL is zero. No action taken.')

        print(f'Finished checking PnL for {symbol}\n')
        results.append((symbol, pnlclose, in_pos, size, long, initial_pos_value))

    return results

def main():
    pnl_close(target, max_loss)

if __name__ == "__main__":
    main()
