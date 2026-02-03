# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Demo application for the **ERC-8004 protocol** — an on-chain AI agent identity and validation standard built on Nillion. Four numbered Python scripts demonstrate a typical agent lifecycle: LLM connectivity → agent registration → validation request → response querying.

## Commands

```bash
# Install dependencies
uv sync

# Run individual scripts (must be run in order for first-time setup)
uv run python src/demo_erc8004/01_openai_request.py
uv run python src/demo_erc8004/02_register_agent.py
uv run python src/demo_erc8004/03_validation_request.py
uv run python src/demo_erc8004/04_validation_response.py
```

No test framework or linter is configured.

## Architecture

All configuration flows through `.env` (copy `.env.sample` to get started). Scripts 02 and 03 auto-update `.env` with values produced during execution (`AGENT_ID`, `REQUEST_HASH`), so the pipeline chains without manual editing.

**Scripts interact with two on-chain contracts via web3.py:**

- **IdentityRegistry** (`02_register_agent.py`): Calls `register(agentURI)`, parses the ERC-721 `Transfer` mint event to extract the agent ID, verifies via `ownerOf`/`tokenURI`/`getAgentWallet`.
- **ValidationRegistry** (`03_validation_request.py`, `04_validation_response.py`): Submits `validationRequest(validator, agentId, requestURI, requestHash, snapshotId)` where `requestHash = keccak256("agentURI:snapshotId")` and `snapshotId = currentBlock - 1`. Script 04 is read-only, querying `ValidationResponse` events from the last ~300 blocks.

Contract ABIs are defined inline in each script (not loaded from external files).

The `rust-original/` directory contains the Rust reference implementation these scripts are ported from. The Solidity interfaces (function signatures, events, struct definitions) are defined as `sol!` macros in those files.
