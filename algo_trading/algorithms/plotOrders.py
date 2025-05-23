import requests
import json
import matplotlib.pyplot as plt


def main():
    def fetch_order_book(symbol):
        url = "https://api.hyperliquid.xyz/info"
        headers = {"Content-Type": "application/json"}
        payload = {
            "type": "l2Book",
            "coin": symbol
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"Error: API returned status code {response.status_code}")
                print(f"Response Content: {response.text}")
                return [], []

            # Parse the response JSON
            response_data = response.json()
            if "levels" not in response_data:
                print("Error: 'levels' key not found in the response.")
                return [], []

            data = response_data["levels"]
            bids, asks = data[0], data[1]

            # Convert px and sz from strings to floats
            bids = [(float(bid["px"]), float(bid["sz"])) for bid in bids]
            asks = [(float(ask["px"]), float(ask["sz"])) for ask in asks]

            print(f"Fetched {len(bids)} bids and {len(asks)} asks for {symbol}.")
            return bids, asks

        except Exception as e:
            print(f"An error occurred while fetching the order book: {e}")
            return [], []

    def plot_order_book(bids, asks, symbol):
        if not bids or not asks:
            print("No data to plot.")
            return

        bid_prices = [b[0] for b in bids]
        bid_sizes = [b[1] for b in bids]
        ask_prices = [a[0] for a in asks]
        ask_sizes = [a[1] for a in asks]

        plt.figure(figsize=(10, 6))
        plt.plot(bid_prices, bid_sizes, label="Bids", color="green", marker='o')
        plt.plot(ask_prices, ask_sizes, label="Asks", color="red", marker='x')
        plt.xlabel("Price")
        plt.ylabel("Size")
        plt.title(f"{symbol} Order Book Depth")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # Fetch and plot the order book
    symbol = "TAO"
    bids, asks = fetch_order_book(symbol)
    plot_order_book(bids, asks, symbol)


if __name__ == "__main__":
    main()