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
        self.account = account
        self.config = config
        self._init_products()
        self.open_transactions = 0
        self.update_orders()
        Thread(target=self.check_market).start()

    def _init_products(self):
        self.products = {}
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

    def check_market(self):
        while True:
            if not self.check_transaction_statuses():
                self.check_possible_new_transactions()
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
                t_delta = self.account.time() - timestamp_from_date(open_transaction["created_at"])
                if t_delta >= self.order_max_lifetime:
                    self.account.cancel_order(open_transaction["id"])
                    refresh = True
        if refresh:
            self.account.update()
        return refresh

    def check_possible_new_transactions(self):
        raise NotImplemented()