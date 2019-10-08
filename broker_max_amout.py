import math

from broker import Broker

class BrokerMaxAmount(Broker):

    def check_possible_new_transactions(self):
        refresh = False
        for currency, value in self.wallet.items():
            for product_id in value["in_products"]:
                product = self.products[product_id]
                if product["base_currency"] == currency:
                    side = "buy"
                    decimals = int(-math.log10(float(product["quote_increment"])))
                else:
                    side = "sell"
                    decimals = int(-math.log10(float(product["quote_increment"])))

                if len(product["open_transactions"][side]) == 0 and len(product["done_transactions"][side]) > 0:
                    last_done = product["done_transactions"][side][0]
                    min = float(product["base_min_size"])
                    last_price = float(last_done["price"])
                    new_price = None
                    if side == "buy":
                        second_lowest = self.order_book[product_id]["bids"][0][0]
                        price_diff = second_lowest - last_price
                        new_amount = min
                        if price_diff < 0:
                            new_price = second_lowest
                    else:
                        second_highest = self.order_book[product_id]["asks"][0][0]
                        price_diff = second_highest - last_price
                        new_amount = min
                        if price_diff > 0:
                            new_price = second_highest

                    refresh = True
                    # print(product_id, side, new_price, new_amount)
                    if new_price is not None:
                        print(self.account.place_limit_order(product_id=product_id, side=side, price=new_price,
                                                             size=new_amount))

        if refresh:
            self._init_wallet()