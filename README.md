# Blacklight ERC-8004 Demo

Python scripts demonstrating the [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) agent identity and validation protocol on the Nillion testnet.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- A funded wallet on the Nillion testnet
- (Optional) A nilAI API key for script 01

## Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.sample .env
# Edit .env with your PRIVATE_KEY and NILAI_API_KEY
```

## Scripts

Run the scripts in order. Scripts 02 and 03 automatically update `.env` with the values they produce (`AGENT_ID`, `REQUEST_HASH`).

### 01 - OpenAI / nilAI Request

```bash
uv run python src/demo_erc8004/01_openai_request.py
```

Makes a chat completion call to a nilAI-hosted OpenAI-compatible endpoint. Requires `NILAI_BASE_URL`, `NILAI_API_KEY`, and `NILAI_MODEL` in `.env`.

### 02 - Register Agent

```bash
uv run python src/demo_erc8004/02_register_agent.py
```

Registers an agent on the **IdentityRegistry** contract with the configured `AGENT_URI`. Parses the ERC-721 `Transfer` (mint) event to extract the agent ID, then verifies via `ownerOf`, `tokenURI`, and `getAgentWallet`. Writes `AGENT_ID` to `.env`.

### 03 - Submit Validation Request

```bash
uv run python src/demo_erc8004/03_validation_request.py
```

Computes `requestHash = keccak256("agentURI:snapshotId")` where `snapshotId = currentBlock - 1`, then calls `validationRequest` on the **ValidationRegistry** contract. Writes `REQUEST_HASH` to `.env`.

### 04 - Fetch Validation Responses

```bash
uv run python src/demo_erc8004/04_validation_response.py
```

Read-only script that queries `ValidationResponse` events from the last ~300 blocks (~10 minutes). Can filter by `REQUEST_HASH` and/or `AGENT_ID` from `.env`.

## Configuration

All configuration is in `.env`. See `.env.sample` for available variables and default values.

| Variable | Description |
|----------|-------------|
| `NILAI_BASE_URL` | nilAI API endpoint |
| `NILAI_API_KEY` | nilAI API key |
| `NILAI_MODEL` | Model name (e.g. `openai/gpt-oss-20b`) |
| `RPC_URL` | Ethereum RPC endpoint |
| `IDENTITY_REGISTRY_ADDRESS` | IdentityRegistry contract address |
| `VALIDATION_REGISTRY_ADDRESS` | ValidationRegistry contract address |
| `PRIVATE_KEY` | Private key for signing transactions |
| `AGENT_URI` | URI to register the agent with |
| `AGENT_ID` | Agent token ID (set automatically by script 02) |
| `VALIDATOR_ADDRESS` | Address authorized to submit validation responses |
| `REQUEST_HASH` | Validation request hash (set automatically by script 03) |
