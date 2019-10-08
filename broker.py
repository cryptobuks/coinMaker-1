import logging
import time
from threading import Thread

import oyaml

from bookFeed import BookFeed
from snippets.date_time import timestamp_from_date


class Broker():
    order_max_lifetime = 600

    def __init__(self, account, config):
        self.logger = logging.getLogger("Broker")
        self.config = config
        self.account = account
        self.products = {}
        self._init_products()
        self.order_book = {}
        self.open_transactions = 0
        self.t_diff = time.time() - timestamp_from_date(self.account.get_time()["iso"])
        self.feed = None
        self.wallet = {}
        self.watched_currencies = self.get_watched_currencies()
        for currency in self.watched_currencies:
            self.wallet[currency] = {
                "account": None,
                "total": 0,
                "free": 0,
                "allocated": 0,
                "in_products": 0,
            }
        self._init_feed()
        self._init_wallet()
        Thread(target=self.check_market).start()

    def get_watched_currencies(self):
        watched_currencies = []
        for product in self.products.keys():
            base, quoted = product.split("-")
            if base not in watched_currencies:
                watched_currencies.append(base)
            if quoted not in watched_currencies:
                watched_currencies.append(quoted)
        return watched_currencies

    def _init_feed(self):
        self.feed = BookFeed(self, self.account.sandbox, list(self.products.keys()), channels=["level2"])
        self.order_book = self.feed.order_book

    def _init_products(self):
        for product in self.account.get_products():
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

    def _init_wallet(self):
        for account in self.account.get_accounts():
            if account["currency"] in self.watched_currencies:
                wallet = self.wallet[account["currency"]]
                wallet["account"] = account["id"]
                wallet["total"] = float(account["balance"])
                wallet["free"] = float(account["available"])
                wallet["allocated"] = float(account["hold"])
                wallet["in_products"] = list(filter(lambda p: account["currency"] in p, list(self.products.keys())))
        self.update_orders()

    def time(self):
        return time.time() - self.t_diff

    def save(self):
        with open("config.yml", "w") as fp:
            oyaml.dump(self.config, fp)

    def check_market(self):
        wallet_check_count = 0
        while True:
            if wallet_check_count == 20:
                self._init_wallet()
                wallet_check_count = 0
            if not self.check_transaction_statuses():
                self.check_possible_new_transactions()
            wallet_check_count += 1
            time.sleep(1)

    def update_orders(self):
        for product in self.products.values():
            product["open_transactions"] = {
                "buy": [],
                "sell": []
            }
            for order in self.account.get_orders(product_id=product["id"]):
                product["open_transactions"][order["side"]].append(order)
            product["done_transactions"] = {
                "buy": [],
                "sell": []
            }
            for order in self.account.get_fills(product_id=product["id"]):
                product["done_transactions"][order["side"]].append(order)

    def check_transaction_statuses(self):
        refresh = False
        for product in self.products.values():
            for open_transaction in product["open_transactions"]["buy"] + product["open_transactions"]["sell"]:
                t_delta = self.time() - timestamp_from_date(open_transaction["created_at"])
                if t_delta >= self.order_max_lifetime:
                    self.account.cancel_order(open_transaction["id"])
                    refresh = True
        if refresh:
            self._init_wallet()
        return refresh

    def check_possible_new_transactions(self):
        raise NotImplemented()