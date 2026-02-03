"""04 - Fetch ValidationResponse Events

Read-only script that queries ValidationResponse events from the
ValidationRegistry contract. Can optionally filter by REQUEST_HASH
and/or AGENT_ID.
"""

import os
import sys
import warnings

from dotenv import load_dotenv
from web3 import Web3

from demo_erc8004.abi import VALIDATION_REGISTRY_ABI

warnings.filterwarnings("ignore", category=UserWarning, module="eth_utils.functional")

def main():
    load_dotenv()

    rpc_url = os.environ.get("RPC_URL", "http://127.0.0.1:8545")
    validation_registry_address = os.environ.get(
        "VALIDATION_REGISTRY_ADDRESS",
        "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
    )
    request_hash_str = os.environ.get("REQUEST_HASH", "")
    agent_id_str = os.environ.get("AGENT_ID", "")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"ERROR: Cannot connect to RPC at {rpc_url}")
        sys.exit(1)

    # Default to ~10 minutes of blocks back (2s block time -> 300 blocks)
    current_block = w3.eth.block_number
    from_block = max(current_block - 3000, 0)

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(validation_registry_address),
        abi=VALIDATION_REGISTRY_ABI,
    )

    # Build filter arguments
    filter_args = {}
    if request_hash_str:
        request_hash_bytes = bytes.fromhex(request_hash_str.removeprefix("0x"))
        filter_args["requestHash"] = request_hash_bytes
    if agent_id_str:
        filter_args["agentId"] = int(agent_id_str)

    print(f"Querying ValidationResponse events from block {from_block} (current: {current_block})...")
    if filter_args:
        print(f"  Filters: {filter_args}")

    events = contract.events.ValidationResponse().get_logs(
        from_block=from_block,
        argument_filters=filter_args if filter_args else None,
    )

    if not events:
        print("No ValidationResponse events found.")
        return

    print(f"Found {len(events)} ValidationResponse event(s):\n")

    for event in events:
        args = event["args"]
        print(f"  Block:         {event['blockNumber']}")
        print(f"  Tx Hash:       {event['transactionHash'].hex()}")
        print(f"  Validator:     {args['validatorAddress']}")
        print(f"  Agent ID:      {args['agentId']}")
        print(f"  Request Hash:  {args['requestHash'].hex()}")
        print(f"  Response:      {args['response']} (0=invalid, 1=valid)")
        print(f"  Response URI:  {args['responseURI']}")
        print(f"  Response Hash: {args['responseHash'].hex()}")
        print(f"  Tag:           {args['tag']}")
        print()


if __name__ == "__main__":
    main()
