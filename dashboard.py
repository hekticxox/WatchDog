from textual.app import App, ComposeResult # type: ignore
from textual.widgets import DataTable # type: ignore
import pandas as pd
import requests

class SignalTableApp(App):
    def compose(self) -> ComposeResult:
        self.table = DataTable(zebra_stripes=True)
        yield self.table

    def on_mount(self):
        self.set_interval(2, self.refresh_table)  # Refresh every 2 seconds
        self.refresh_table()

    def refresh_table(self):
        # Save scroll position and selection
        scroll_y = self.table.scroll_y
        selected_row = self.table.cursor_row

        df = pd.read_csv("signal_log.csv")
        df = df.sort_values("timestamp").drop_duplicates("symbol", keep="last")

        # Calculate proximity to support/resistance
        if {"SUPPORT", "RESISTANCE", "CLOSE"}.issubset(df.columns):
            df["PROX_SUPPORT"] = abs(df["CLOSE"] - df["SUPPORT"])
            df["PROX_RESIST"] = abs(df["RESISTANCE"] - df["CLOSE"])
        else:
            df["PROX_SUPPORT"] = float("inf")
            df["PROX_RESIST"] = float("inf")

        # Custom sort: buy first, then sell, then hold
        signal_order = {"buy": 0, "sell": 1, "hold": 2}
        df["SIGNAL_SORT"] = df["SIGNAL"].str.lower().map(signal_order).fillna(3)

        # Enhanced secondary sort: for buys, lowest RSI and closest to support; for sells, highest RSI and closest to resistance
        def secondary_sort(row):
            if str(row["SIGNAL"]).lower() == "buy":
                # Lower RSI and closer to support is better
                return (row["RSI"], row["PROX_SUPPORT"])
            elif str(row["SIGNAL"]).lower() == "sell":
                # Higher RSI (so negative for descending), closer to resistance is better
                return (-row["RSI"], row["PROX_RESIST"])
            else:
                return (0, float("inf"))

        df["SECONDARY_SORT"] = df.apply(secondary_sort, axis=1)
        df = df.sort_values(["SIGNAL_SORT", "SECONDARY_SORT"]).drop(columns=["SIGNAL_SORT", "SECONDARY_SORT", "PROX_SUPPORT", "PROX_RESIST"])

        self.table.clear(columns=True)
        self.table.add_columns(*df.columns)
        for _, row in df.iterrows():
            row_data = [str(x) if pd.notna(x) else "-" for x in row]
            signal = str(row_data[-1]).lower()
            if signal == "buy":
                row_data[-1] = "[green]buy[/green]"
            elif signal == "sell":
                row_data[-1] = "[red]sell[/red]"
            elif signal == "hold":
                row_data[-1] = "[yellow]hold[/yellow]"
            self.table.add_row(*row_data)

        # Restore scroll position and selection
        self.table.scroll_y = scroll_y
        self.table.move_cursor(row=selected_row, column=0)

    def fetch_klines_rest(symbol, start, end):
        # Dummy implementation, replace with actual KuCoin REST API call as needed
        # Return empty list to trigger Binance fallback for now
        return []

    def fetch_klines(symbol, start, end, interval="1m"):
        # Try KuCoin first
        data = SignalTableApp.fetch_klines_rest(symbol, start, end)
        if data and len(data) > 50:
            return data
        # Fallback to Binance
        binance_symbol = symbol.replace("USDTM", "USDT")  # Adjust symbol if needed
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={binance_symbol}&interval=1m&limit=1000"
        try:
            resp = requests.get(url, timeout=10)
            klines = resp.json()
            # Format: [open_time, open, high, low, close, volume, ...]
            return [
                [k[0], float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])]
                for k in klines
            ]
        except Exception as e:
            print(f"Binance fallback failed: {e}")
            return []

if __name__ == "__main__":
    SignalTableApp().run()