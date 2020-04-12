"""
Blockchain — Day 1 Project :: Client
"""

import hashlib
import json
from pprint import pprint
import sys

import requests


def proof_of_work(block):
    """Simple Proof of Work Algorithm.
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof.

    :return: A valid proof for the provided block.
    """
    # Create string from block
    block_string = json.dumps(block, sort_keys=True)
    proof = 0
    while not valid_proof(block_string, proof):
        proof += 1
    return proof


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


if __name__ == "__main__":
    # Fake wallet
    coins = 0
    print(f"Your wallet contains {coins} coins.")

    # What is the server address? IE `python3 miner.py https://server.com/api/`
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"

    # Load ID
    with open("tobias.txt", "r") as f:
        id = f.read().strip()
        print("ID is", id)

    # Run forever until interrupted
    while True:
        print("\nRequesting last block from server...")
        r = requests.get(url=node + "/last_block")
        # Handle non-json response
        try:
            data = r.json()
            print("Block received.")
            pprint(data)
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            break

        # TODO: Get the block from `data` and use it to look for a new proof
        print("\nStarting proof of work...")
        new_proof = proof_of_work(data)

        # When found, POST it to the server {"proof": new_proof, "id": id}
        print(f"Proof has been found: {new_proof}")
        post_data = {"proof": new_proof, "id": id}
        print("Sending to server...")
        r = requests.post(url=node + "/mine", json=post_data)

        data = r.json()  # Parse the response
        msg = data.get("message")
        print("\nResponse from server received.")

        success_msg = "New block successfully forged!"
        if msg == success_msg:  # Check if block was successfully forged
            coins += 1  # Add 1 to the number of coins mined and print it
            print(msg)
            print(f"Your wallet contains {coins} coins.")
        else:  # If not, print the message from the server
            print(msg)
