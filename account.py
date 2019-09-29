import cbpro
from cbpro import AuthenticatedClient


class Account(AuthenticatedClient):

    def __init__(self, key, secret, passphrase, sandbox=False):
        api_url = "https://api.pro.coinbase.com"
        if sandbox:
            api_url = "https://api-public.sandbox.pro.coinbase.com"
        self.sandbox = sandbox
        self.wallet = {}
        AuthenticatedClient.__init__(self, key, secret, passphrase, api_url=api_url)
        self.update_account_info()

    def update_account_info(self):
        accounts = self.get_accounts()
        for account in accounts:
            self.wallet[account["currency"]] = account
