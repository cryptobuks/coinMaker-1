import math
import time

from broker import Broker
from snippets.date_time import timestamp_from_date


class BrokerNode(Broker):
    check_timeout = 5
    order_max_lifetime = 3600

    def __init__(self, account, config):
        self.node_file = "nodes/{}.node".format(config["id"])
        self.transactions = self._read_nodes_transactions()
        super().__init__(account, config)
        if len(self.transactions) == 0:
            self.prepare_initial_transaction()

    def _read_nodes_transactions(self):
        try:
            with open(self.node_file, "r") as fp:
                return fp.readlines()
        except FileNotFoundError:
            return []

    def prepare_initial_transaction(self):
        order = self.account.place_limit_order(product_id=self.config["product"], side="sell",
                                               price=self.config["start_at"],
                                               size=self.config["amount"])
        with open(self.node_file, "a+") as fp:
            fp.write(order["id"] + "," + order["side"] + "\r\n")
        self.transactions.append(order["id"] + "," + order["side"])
        self.account.update()

    def check_transaction_statuses(self):
        if len(self.transactions) == 0:
            return
        last_transaction_id, last_transaction_side = self.transactions[-1].strip().split(",")
        order = self.account.get_order(last_transaction_id)
        if "message" in order:
            del self.transactions[-1]
            if len(self.transactions) == 0:
                self.prepare_initial_transaction()
        # elif order["status"] == "open":
        #     return False
        elif order["status"] == "done":
            self.check_possible_new_transactions(order)

        product = self.account.products[self.config["product"]]
        for open_transaction in product["open_transactions"]["buy"] + product["open_transactions"]["sell"]:
            t_delta = self.account.time() - timestamp_from_date(open_transaction["created_at"])
            if t_delta >= self.order_max_lifetime:
                self.account.cancel_order(open_transaction["id"])

    def check_market(self):
        while True:
            self.check_transaction_statuses()
            time.sleep(self.check_timeout)

    def check_possible_new_transactions(self, last_order):
        new_transaction_side = "buy"
        look_at = "bids"
        if last_order["side"] == "buy":
            new_transaction_side = "sell"
            look_at = "asks"
        product = self.account.products[self.config["product"]]
        decimals = int(-math.log10(float(product["quote_increment"])))
        try:
            orders = self.account.feed.order_book[self.config["product"]][look_at]
        except KeyError:
            print("Key error {}".format(self.config["product"]))
            return

        fee = float(last_order["fill_fees"])
        new_price = orders[0][0]
        if len(orders) >= 2:
            new_price = (orders[0][0] + orders[1][0]) / 2

        if last_order["side"] == "buy" and new_price <= float(last_order["price"]):
            return
        elif last_order["side"] == "sell" and new_price >= float(last_order["price"]):
            return

        new_price = round(new_price, decimals)
        new_amount = round((float(last_order["executed_value"]) - fee) / new_price, decimals) * (
                1 - float(self.account.fees["maker_fee_rate"]))
        if new_amount <= float(last_order["size"]):
            return
        order = self.account.place_limit_order(product_id=self.config["product"], side=new_transaction_side,
                                               price=new_price, size=new_amount)
        if "message" in order:
            return
        with open(self.node_file, "a+") as fp:
            fp.write(order["id"] + "," + order["side"] + "\r\n")
        self.transactions.append(order["id"] + "," + order["side"])
