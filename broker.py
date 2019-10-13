import logging
import time
from threading import Thread

import oyaml

from bookFeed import BookFeed
from snippets.date_time import timestamp_from_date


class Broker():
    order_max_lifetime = 600
    check_timeout = 1

    def __init__(self, account, config):
        self.logger = logging.getLogger("Broker")
        self.account = account
        self.config = config
        self.open_transactions = 0
        Thread(target=self.check_market).start()

    def check_market(self):
        while True:
            if not self.check_transaction_statuses():
                self.check_possible_new_transactions()
            time.sleep(self.check_timeout)

    def check_transaction_statuses(self):
        refresh = False
        for product_id in self.config["product_list"]:
            product = self.account.products[product_id]
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