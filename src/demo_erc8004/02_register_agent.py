"""02 - Register Agent via IdentityRegistry

Registers a new agent with a URI on the IdentityRegistry contract.
Parses the Transfer event (mint) to extract the agent ID, then verifies
by calling ownerOf, tokenURI, and getAgentWallet.
"""

import os
import re
import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

from demo_erc8004.abi import IDENTITY_REGISTRY_ABI

warnings.filterwarnings("ignore", category=UserWarning, module="eth_utils.functional")

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def main():
    load_dotenv()

    rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
    identity_registry_address = os.environ.get(
        "IDENTITY_REGISTRY_ADDRESS",
        "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    )
    private_key = os.environ.get(
        "PRIVATE_KEY",
        "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
    )
    agent_uri = os.environ.get("AGENT_URI", "https://example.com/agent")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"ERROR: Cannot connect to RPC at {rpc_url}")
        sys.exit(1)

    account = w3.eth.account.from_key(private_key)
    print(f"Signer address: {account.address}")

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(identity_registry_address),
        abi=IDENTITY_REGISTRY_ABI,
    )

    print(f"Registering agent with URI: {agent_uri}")

    tx = contract.functions.register(agent_uri).build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
        }
    )
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Transaction sent: {tx_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction confirmed in block {receipt['blockNumber']}")

    # Parse Transfer event to find the minted agent ID
    transfer_events = contract.events.Transfer().process_receipt(receipt)
    agent_id = None
    for event in transfer_events:
        if event["args"]["from"] == ZERO_ADDRESS:
            agent_id = event["args"]["tokenId"]
            break

    if agent_id is None:
        print("ERROR: Transfer (mint) event not found in receipt")
        sys.exit(1)

    print(f"Agent registered with ID: {agent_id}")

    # Verify registration
    owner = contract.functions.ownerOf(agent_id).call()
    token_uri = contract.functions.tokenURI(agent_id).call()
    agent_wallet = contract.functions.getAgentWallet(agent_id).call()

    print(f"  Owner:        {owner}")
    print(f"  Token URI:    {token_uri}")
    print(f"  Agent Wallet: {agent_wallet}")

    # Update AGENT_ID in .env file
    env_path = Path(".env")
    if env_path.exists():
        env_content = env_path.read_text()
        env_content = re.sub(
            r"^AGENT_ID=.*$", f"AGENT_ID={agent_id}", env_content, flags=re.MULTILINE
        )
        env_path.write_text(env_content)
        print(f"\n.env updated with AGENT_ID={agent_id}")
    else:
        print(f"\nNo .env file found. Add this manually:")
        print(f"  AGENT_ID={agent_id}")


if __name__ == "__main__":
    main()
