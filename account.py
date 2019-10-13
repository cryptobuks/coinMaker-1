import time
from threading import Thread

import oyaml
from requests import ReadTimeout

from bookFeed import BookFeed
from broker_max_amount import BrokerMaxAmount
from broker_node import BrokerNode
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
        self.last_update = None
        AuthenticatedClient.__init__(self, key, secret, passphrase, api_url=api_url)
        self.t_diff = time.time() - timestamp_from_date(self.get_time()["iso"])
        self.watched_currencies = self.get_watched_currencies()
        self._init_products()
        self.update()
        self._init_feed()
        self._init_brokers()
        Thread(target=self._check_update_thread).start()

    def _init_feed(self):
        self.feed = BookFeed(self, self.config["sandbox"], list(self.config["product_list"]), channels=["level2"])

    def _init_brokers(self):
        for broker_config in self.config["brokers"]:
            if broker_config["type"] == "max_amount":
                self.bookers.append(BrokerMaxAmount(self, broker_config))
            elif broker_config["type"] == "node":
                self.bookers.append(BrokerNode(self, broker_config))

    def _init_products(self):
        self.products = {}
        for product in self.get_products():
            if product["id"] in self.config["product_list"]:
                self.products[product["id"]] = product
            else:
                continue
            product["open_transactions"] = {
                "buy": [],
                "sell": []
            }
            product["done_transactions"] = {
                "buy": [],
                "sell": []
            }

    def _check_update_thread(self):
        while True:
            if time.time() - self.last_update >= 15:
                self.update()
                time.sleep(5)

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
        try:
            accounts = self.get_accounts()
        except ReadTimeout:
            print("Account update readout timeout")
            self.update()
            return
        print("Update wallet")
        for account in accounts:
            self.wallet[account["currency"]] = account
            self.wallet[account["currency"]]["in_products"] = list(
                filter(lambda p: account["currency"] in p, list(self.config["product_list"])))
        self.update_orders()
        self.last_update = time.time()

    def update_orders(self):
        for product in self.products.values():
            open_transactions = {
                "buy": [],
                "sell": []
            }
            for order in self.get_orders(product_id=product["id"]):
                open_transactions[order["side"]].append(order)
            done_transactions = {
                "buy": [],
                "sell": []
            }
            for order in self.get_fills(product_id=product["id"]):
                done_transactions[order["side"]].append(order)

            product["open_transactions"] = open_transactions
            product["done_transactions"] = done_transactions

    def has_funds(self, product_id, side, price, amount):
        base, quoted = product_id.split("-")
        if side == "buy" and float(self.wallet[quoted]["available"]) <= price * amount:
            return False
        elif side == "sell" and float(self.wallet[base]["available"]) <= amount:
            return False
        return True