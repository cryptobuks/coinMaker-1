import copy
from statistics import mean, StatisticsError

from cbpro import WebsocketClient
from snippets.date_time import timestamp_from_date


class BookFeed(WebsocketClient):

    def __init__(self, broker, sandbox=False, products=None, message_type="subscribe",
                 mongo_collection=None, should_print=True, auth=False, api_key="", api_secret="", api_passphrase="", *,
                 channels):
        url = "wss://ws-feed.pro.coinbase.com"
        self.order_book = {}
        self.broker = broker
        if sandbox:
            url = "wss://ws-feed-public.sandbox.pro.coinbase.com"
        self.product_last_tick = {}
        super().__init__(url, products, message_type, mongo_collection, should_print, auth, api_key, api_secret,
                         api_passphrase, channels=channels)
        self.should_print = False
        self.start()

    @staticmethod
    def map_float(input):
        price, volume = input
        return [float(price), float(volume)]

    def on_message(self, msg):
        if msg["type"] == "snapshot":
            self.order_book[msg["product_id"]] = {
                "asks": list(map(self.map_float, msg["asks"])),
                "bids": list(map(self.map_float, msg["bids"])),
                "speed": [0, 0],
                "amount": [0, 0],
                "price": [0, 0],
                "ts_buffer": [],
                "speed_buffer": [[], []],
                "amount_buffer": [[], []],
                "price_buffer": [[], []]
            }
        elif msg["type"] == "l2update":
            self.merge_update(self.order_book[msg["product_id"]], msg["changes"])
            self.calculate_speed(msg)
            self.broker.notify(msg["product_id"])

    def calculate_speed(self, msg):
        ob = self.order_book[msg["product_id"]]
        tick_speed = {"buy": 0, "sell": 0}
        tick_amount = {"buy": 0, "sell": 0}
        tick_price = {"buy": 0, "sell": 0}
        bs_kw = (("speed_buffer", tick_speed), ("amount_buffer", tick_amount), ("price_buffer", tick_price))
        for change in msg["changes"]:
            tick_speed[change[0]] += 1
            tick_amount[change[0]] += float(change[2])
            tick_price[change[0]] += float(change[1])
        if tick_speed["buy"] > 0:
            tick_price["buy"] /= tick_speed["buy"]
        if tick_speed["sell"] > 0:
            tick_price["sell"] /= tick_speed["sell"]
        ob["ts_buffer"].append(timestamp_from_date(msg["time"]))
        for kw, kv in bs_kw:
            ob[kw][0].append(kv["buy"])
            ob[kw][1].append(kv["sell"])

        while ob["ts_buffer"][-1] - ob["ts_buffer"][0] > 60:
            ob["ts_buffer"].pop(0)
            for kw, _ in bs_kw:
                ob[kw][0].pop(0)
                ob[kw][1].pop(0)
        ob["speed"] = [sum(ob["speed_buffer"][0]), -sum(ob["speed_buffer"][1])]
        ob["amount"] = [sum(ob["amount_buffer"][0]), -sum(ob["amount_buffer"][1])]
        try:
            a = mean(filter(lambda i: i > 0, ob["price_buffer"][0]))
        except StatisticsError:
            a = 0
        try:
            b = -mean(filter(lambda i: i > 0, ob["price_buffer"][1]))
        except StatisticsError:
            b = 0
        ob["price"] = [a, b]

    def merge_update(self, product, changes):
        for change in changes:
            price, amount = float(change[1]), float(change[2])
            list_of_changes = product["asks"] if change[0] == "sell" else product["bids"]
            for index, (book_price, book_amount) in enumerate(copy.copy(list_of_changes)):
                if price == float(book_price) and amount == 0:
                    del list_of_changes[index]
                    break
                elif price == float(book_price):
                    list_of_changes[index] = self.map_float(change[1:])
                    break
                elif change[0] == "sell" and price < float(book_price):
                    list_of_changes.insert(index, self.map_float(change[1:]))
                    break
                elif change[0] == "buy" and price > float(book_price):
                    list_of_changes.insert(index, self.map_float(change[1:]))
                    break
