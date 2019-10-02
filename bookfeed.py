import copy

from cbpro import WebsocketClient


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

    def maper(self, input):
        price, volume = input
        return [float(price), float(volume)]

    def on_message(self, msg):
        if msg["type"] == "snapshot":
            self.order_book[msg["product_id"]] = {
                "asks": list(map(self.maper, msg["asks"])),
                "bids": list(map(self.maper, msg["bids"])),
            }
        elif msg["type"] == "l2update":
            self.merge_update(self.order_book[msg["product_id"]], msg["changes"])

    def merge_update(self, product, changes):
        for change in changes:
            price, amount = float(change[1]), float(change[2])
            l = product["asks"] if change[0] == "sell" else product["bids"]
            for index, (book_price, book_amount) in enumerate(copy.copy(l)):
                if price == float(book_price):
                    l[index] = self.maper(change[1:])
                    break
                elif change[0] == "sell" and price < float(book_price):
                    l.insert(index, self.maper(change[1:]))
                    break
                elif change[0] == "buy" and price > float(book_price):
                    l.insert(index, self.maper(change[1:]))
                    break
