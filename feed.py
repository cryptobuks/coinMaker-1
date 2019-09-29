from cbpro import WebsocketClient


class Feed(WebsocketClient):

    def __init__(self, broker, sandbox=False, products=None, message_type="subscribe",
                 mongo_collection=None, should_print=True, auth=False, api_key="", api_secret="", api_passphrase="", *,
                 channels):
        url = "wss://ws-feed.pro.coinbase.com"
        self.broker = broker
        if sandbox:
            url = "wss://ws-feed-public.sandbox.pro.coinbase.com"
        self.product_last_tick = {}
        super().__init__(url, products, message_type, mongo_collection, should_print, auth, api_key, api_secret,
                         api_passphrase, channels=channels)
        self._init_product_last_tick()

    def _init_product_last_tick(self):
        for product in self.products:
            trades = self.broker.account.get_product_order_book(product)
            self.product_last_tick[product] = [float(trades["bids"][-1][0]), float(trades["asks"][-1][0])]
        self.start()

    def on_message(self, msg):
        if "product_id" in msg and "side" in msg:
            if msg["side"] == "buy":
                self.product_last_tick[msg["product_id"]][0] = float(msg["price"])
            else:
                self.product_last_tick[msg["product_id"]][1] = float(msg["price"])
            self.broker.notify(msg["product_id"])