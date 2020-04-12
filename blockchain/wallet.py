"""
Blockchain — Day 2 Project :: Wallet app

> MVP
* Allow the user to enter, save, or change the `user_id` used for the program
* Display the current balance for that user
* Display a list of all transactions for this user, including sender and recipient

> Stretch Goals
* Use styling to visually distinguish coins sent and coins received
* Paginate the list of transactions if there are more than ten
"""


import json
from pprint import pprint

import requests


class User:
    def __init__(
        self,
        user_id: str = "007",
        balance: float = 0.0,
        url: str = "http://localhost:5000",
    ):
        """Constructor for the user account management handler class."""
        self.user_id = user_id
        self.url = url
        self.cache = []
        self.last_index = 0
        self.balance = balance

    @property
    def user_id(self) -> str:
        """User's account identifier."""
        return self._user_id

    @user_id.setter
    def user_id(self, new_id) -> None:
        """Setter function for user_id property."""
        self._user_id = new_id
        print(f"User ID: {new_id}")

    @property
    def balance(self) -> None:
        """User's current number of coins."""
        return self._balance

    @balance.setter
    def balance(self, value: float) -> None:
        """Setter function for balance property."""
        self._balance = value

    def show_transactions(self) -> None:
        """Displays user's transactions."""
        pprint(self.cache)

    def post_transaction(self, recipient: str, amt: float) -> int:
        """Posts a new transaction from the user.
        Returns index of block into which transaction was posted."""
        # TODO: Check if user has enough coins
        if self.balance - amt < 0:
            print("Error: Not enough coins for transaction")
        else:
            # Construct the POST object
            post_data = {
                "sender": self.user_id,
                "recipient": recipient,
                "amount": amt,
            }
            # Post transaction to blockchain server
            r = requests.post(url=self.url + "/transactions/new", json=post_data)
            # Parse the response
            if r.status_code == 200:
                resp = r.json()
                print(resp.get("message"))
                return resp.get("index")
            else:
                print("Post failed.")

    def get_transactions(self) -> list:
        """Helper function for retrieving all transactions involving user."""
        # Retrieve full chain
        r = requests.get(url=self.url + "/chain")
        # Parse into list of dictionaries
        chain = r.json()["chain"]
        # Iterate through chain, starting after last processed block
        for block in chain[self.last_index :]:
            # Iterate through each block's transactions
            for transaction in block["transactions"]:
                # Look for transactions where user_id is recipient or sender
                if self.user_id in transaction.values():
                    # Add transaction to user's transaction cache
                    transaction["block_index"] = block["index"]
                    transaction["block_timestamp"] = block["timestamp"]
                    self.cache.append(transaction)
                    # Update user's balance
                    if transaction["recipient"] == self.user_id:
                        self.balance += transaction["amount"]
                    else:
                        self.balance -= transaction["amount"]

            self.last_index += 1  # Count block as processed

        print(f"Updated wallet up to block {self.last_index + 1}")


if __name__ == "__main__":
    # === Instantiate users
    james_bond = User(user_id="007", balance=100.0)
    jane_bond = User(user_id="008", balance=50.0)

    # === Update wallets
    james_bond.get_transactions()
    jane_bond.get_transactions()

    # === Print balances
    print(james_bond.balance)
    print(jane_bond.balance)

    # === Post transactions
    james_bond.post_transaction("008", 1.8)
    jane_bond.post_transaction("007", 0.7)

    # === Post transactions
    jane_bond.post_transaction("007", 7.7)
    james_bond.post_transaction("008", 8.8)

    # === Update wallets
    james_bond.get_transactions()
    jane_bond.get_transactions()

    # === Print balances
    print(james_bond.balance)
    print(jane_bond.balance)
