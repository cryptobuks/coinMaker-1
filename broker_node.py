import math

from broker import Broker


class BrokerNode(Broker):
    check_timeout = 5

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
        product = self.account.products[self.config["product"]]
        decimals = int(-math.log10(float(product["quote_increment"])))
        order = self.account.place_limit_order(product_id=self.config["product"], side="sell", price=self.config["start_at"],
                                             size=self.config["amount"])
        with open(self.node_file, "a+") as fp:
            fp.write(order["id"]+","+order["side"]+"\r\n")
        self.account.update()

    def check_transaction_statuses(self):
        refresh = False
        product = self.account.products[self.config["product"]]
        last_transaction_id, last_transaction_side = self.transactions[-1][:-1].split(",")
        order = self.account.get_order(last_transaction_id)
        if "message" in order:
            print("filled or error")
        elif order["status"] == "open":
            print("pasing")
            return
        if refresh:
            self.account.update()
        return refresh

    def check_possible_new_transactions(self):
        print("check")