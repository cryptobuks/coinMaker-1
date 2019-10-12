import time

import oyaml

from bookFeed import BookFeed
from broker_max_amount import BrokerMaxAmount
from cbpro import AuthenticatedClient
from snippets.date_time import timestamp_from_date


class Account(AuthenticatedClient):

    def __init__(self, key, secret, passphrase, config):
        self.config = config
        api_url = "https://api.pro.coinbase.com"
        if self.config["sandbox"]:
            api_url = "https://api-public.sandbox.pro.coinbase.com"
        self.wallet = {}
        self.feed = None
        self.bookers = []
        AuthenticatedClient.__init__(self, key, secret, passphrase, api_url=api_url)
        self.t_diff = time.time() - timestamp_from_date(self.get_time()["iso"])
        self.watched_currencies = self.get_watched_currencies()
        self.update()
        self._init_feed()
        self._init_brokers()

    def _init_feed(self):
        self.feed = BookFeed(self, self.config["sandbox"], list(self.config["product_list"]), channels=["level2"])

    def _init_brokers(self):
        for broker_config in self.config["brokers"]:
            if broker_config["type"] == "max_amount":
                self.bookers.append(BrokerMaxAmount(self, broker_config))

    def time(self):
        return time.time() - self.t_diff

    def save(self):
        with open("config.yml", "w") as fp:
            oyaml.dump(self.config, fp)

    def get_watched_currencies(self):
        watched_currencies = []
        for product in self.config["product_list"]:
            base, quoted = product.split("-")
            if base not in watched_currencies:
                watched_currencies.append(base)
            if quoted not in watched_currencies:
                watched_currencies.append(quoted)
        return watched_currencies

    def update(self):
        accounts = self.get_accounts()
        for account in accounts:
            self.wallet[account["currency"]] = account
            self.wallet[account["currency"]]["in_products"] = list(
                filter(lambda p: account["currency"] in p, list(self.config["product_list"])))
