#!/usr/bin/env bash
set -e

# AI Governance Register — One-command launcher
# Usage: ./start.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== AI Governance Register ===${NC}"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    echo "Download from: https://www.python.org/downloads/"
    exit 1
fi

# Create virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -e "." 2>/dev/null || pip install -q fastapi uvicorn[standard] sqlalchemy pydantic python-dotenv anthropic reportlab python-docx requests streamlit plotly

# Create data directory
mkdir -p data

# Clean shutdown handler
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $API_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait $API_PID 2>/dev/null || true
    wait $FRONTEND_PID 2>/dev/null || true
    echo "Done."
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start API
echo "Starting API on port 8000..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for API to be ready
for i in {1..20}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# Start Streamlit
echo "Starting frontend on port 8501..."
streamlit run frontend/app.py --server.port 8501 --server.headless true &
FRONTEND_PID=$!

# Wait a moment, then open browser
sleep 2
echo ""
echo -e "${GREEN}Ready!${NC}"
echo "  Frontend: http://localhost:8501"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop."

# Open browser
if command -v open &>/dev/null; then
    open http://localhost:8501
elif command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:8501
fi

# Wait for processes
wait
