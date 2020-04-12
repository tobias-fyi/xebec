"""
Blockchain — Day 1 Project :: Server
"""

import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """Create a new Block in the Blockchain.

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm.
        :param previous_hash: (Optional) <str> Hash of previous Block.
        :return: <dict> New Block.
        """

        if len(self.chain) > 0:
            block_string = json.dumps(self.last_block, sort_keys=True)
            guess = f"{block_string}{proof}".encode()
            current_hash = hashlib.sha256(guess).hexdigest()
        else:
            current_hash = ""

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
            "hash": current_hash,
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def new_transaction(self, sender: str, recipient: str, amount: float):
        """Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <float> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        self.current_transactions.append(
            {"sender": sender, "recipient": recipient, "amount": amount}
        )
        return self.last_block["index"] + 1

    def hash(self, block):
        """Creates a SHA-256 hash of a Block

        :param block": <dict> Block object.
        "return": <str> Hashed block string in hexadecimal format.
        """
        # Use json.dumps to convert json into a string
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        # Create the block_string
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        # Hash the string using sha256
        raw_hash = hashlib.sha256(block_string)

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand
        hex_hash = raw_hash.hexdigest()
        # Return the hashed block string in hexadecimal format
        return hex_hash

    @property
    def last_block(self):
        """Returns the block object currently at the end of the chain."""
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """Validates the Proof.
        Does hash(block_string, proof) contain 6 leading zeroes?
        Return true if the proof is valid.

        :param block_string: <string> The stringified block to use to
        check in combination with `proof`.
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise.
        """
        guess = f"{block_string}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:6] == "000000"


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace("-", "")

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint to test API is working."""
    return jsonify({"status": "active", "message": "pong!"})


@app.route("/mine", methods=["POST"])
def mine():
    # === Parse and validate request
    post_data = request.get_json()
    if "proof" in post_data and "id" in post_data:
        # If request is valid, get proof and id
        proof = post_data.get("proof")
        proof_id = post_data.get("id")

        # === Validate proof
        last_block_string = json.dumps(blockchain.last_block, sort_keys=True)
        if blockchain.valid_proof(last_block_string, proof):

            # Valid: Forge new Block by adding it to the chain with the proof
            previous_hash = blockchain.hash(blockchain.last_block)
            block = blockchain.new_block(proof, previous_hash)
            response = {
                "message": "New block successfully forged!",
                "index": block["index"],
                "transactions": block["transactions"],
                "proof": block["proof"],
                "previous_hash": block["previous_hash"],
            }
            return jsonify(response), 200

        else:  # Proof is not valid
            return jsonify({"message": "Error: Block already forged."}), 400

    else:  # If "proof" and/or "id" not in request
        return jsonify({"message": "Error: Invalid request"}), 400


@app.route("/chain", methods=["GET"])
def full_chain():
    """Returns the full chain of blocks."""
    response = {"length": len(blockchain.chain), "chain": blockchain.chain}
    return jsonify(response), 200


@app.route("/last_block", methods=["GET"])
def last_block():
    """Returns only the last block"""
    return jsonify(blockchain.last_block), 200


@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()

    required = ["sender", "recipient", "amount"]
    if not all(k in values for k in required):
        return jsonify("Error: Missing values"), 400

    index = blockchain.new_transaction(
        values["sender"], values["recipient"], values["amount"]
    )

    response = {
        "message": f"Transaction will be added to Block {index}",
        "index": index,
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
