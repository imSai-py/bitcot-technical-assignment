#!/usr/bin/env bash
set -e

echo "========================================"
echo "1. Testing debug-warmup (Python)..."
echo "========================================"
(cd debug-warmup && python -m pytest tests)

echo ""
echo "========================================"
echo "2. Testing python-ticket-summary (Python)..."
echo "========================================"
(cd python-ticket-summary && python -m pytest tests)

echo ""
echo "========================================"
echo "3. Testing typescript-sla-library (Node/Vitest)..."
echo "========================================"
(cd typescript-sla-library && npm test)

echo ""
echo "========================================"
echo "VERIFICATION SUCCESS: All Python and TypeScript tests passed!"
echo "========================================"
