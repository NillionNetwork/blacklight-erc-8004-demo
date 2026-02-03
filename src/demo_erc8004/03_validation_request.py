"""03 - Submit Validation Request via ValidationRegistry

Computes a request hash from agent_uri and snapshot_id, then calls
validationRequest on the ValidationRegistry contract.
Parses and prints the ValidationRequest event.
"""

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from web3 import Web3

VALIDATION_REGISTRY_ABI = [
    {
        "name": "validationRequest",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "validatorAddress", "type": "address"},
            {"name": "agentId", "type": "uint256"},
            {"name": "requestURI", "type": "string"},
            {"name": "requestHash", "type": "bytes32"},
            {"name": "snapshotId", "type": "uint64"},
        ],
        "outputs": [],
    },
    {
        "name": "ValidationRequest",
        "type": "event",
        "anonymous": False,
        "inputs": [
            {"name": "validatorAddress", "type": "address", "indexed": True},
            {"name": "agentId", "type": "uint256", "indexed": True},
            {"name": "requestURI", "type": "string", "indexed": False},
            {"name": "requestHash", "type": "bytes32", "indexed": True},
        ],
    },
]


def main():
    load_dotenv()

    rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
    validation_registry_address = os.environ.get(
        "VALIDATION_REGISTRY_ADDRESS",
        "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
    )
    private_key = os.environ.get(
        "PRIVATE_KEY",
        "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
    )
    validator_address = os.environ.get(
        "VALIDATOR_ADDRESS",
        "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
    )
    agent_id_str = os.environ.get("AGENT_ID", "")
    agent_uri = os.environ.get("AGENT_URI", "https://example.com/agent")

    if not agent_id_str:
        print("ERROR: AGENT_ID must be set in .env (run 02_register_agent.py first)")
        sys.exit(1)

    agent_id = int(agent_id_str)

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"ERROR: Cannot connect to RPC at {rpc_url}")
        sys.exit(1)

    account = w3.eth.account.from_key(private_key)
    print(f"Signer address: {account.address}")

    # Compute snapshot_id from current block
    block_number = w3.eth.block_number
    snapshot_id = max(block_number - 1, 0)
    print(f"Current block: {block_number}, using snapshot_id: {snapshot_id}")

    # Compute request_hash = keccak256("agent_uri:snapshot_id")
    hash_input = f"{agent_uri}:{snapshot_id}"
    request_hash = Web3.keccak(text=hash_input)
    print(f"Request hash input: {hash_input}")
    print(f"Request hash: {request_hash.hex()}")

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(validation_registry_address),
        abi=VALIDATION_REGISTRY_ABI,
    )

    print(
        f"Submitting validation request: validator={validator_address}, "
        f"agent_id={agent_id}, snapshot_id={snapshot_id}"
    )

    tx = contract.functions.validationRequest(
        Web3.to_checksum_address(validator_address),
        agent_id,
        agent_uri,
        request_hash,
        snapshot_id,
    ).build_transaction(
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

    # Parse ValidationRequest event
    events = contract.events.ValidationRequest().process_receipt(receipt)
    for event in events:
        args = event["args"]
        print(f"ValidationRequest event:")
        print(f"  Validator:    {args['validatorAddress']}")
        print(f"  Agent ID:     {args['agentId']}")
        print(f"  Request URI:  {args['requestURI']}")
        print(f"  Request Hash: {args['requestHash'].hex()}")

    # Update REQUEST_HASH in .env file
    env_path = Path(".env")
    if env_path.exists():
        env_content = env_path.read_text()
        env_content = re.sub(
            r"^REQUEST_HASH=.*$",
            f"REQUEST_HASH={request_hash.hex()}",
            env_content,
            flags=re.MULTILINE,
        )
        env_path.write_text(env_content)
        print(f"\n.env updated with REQUEST_HASH={request_hash.hex()}")
    else:
        print(f"\nNo .env file found. Add this manually:")
        print(f"  REQUEST_HASH={request_hash.hex()}")


if __name__ == "__main__":
    main()
