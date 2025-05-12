#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== Stopping All Servers =====${NC}"

# Kill all servers by PID files
echo -e "${YELLOW}Stopping all servers...${NC}"

count=0
while IFS= read -r pidfile; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        server_name=$(basename "${pidfile%.pid}")
        echo -e "Stopping ${YELLOW}$server_name${NC} (PID: $pid)"
        
        # Try graceful termination first
        kill -15 "$pid" 2>/dev/null
        sleep 1
        
        # Check if process still exists, if yes, force kill
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${RED}Process still running, forcing termination${NC}"
            kill -9 "$pid" 2>/dev/null
        fi
        
        rm "$pidfile"
        ((count++))
    fi
done < <(find . -name "*.pid")

echo -e "${GREEN}$count servers stopped${NC}"

echo -e "${GREEN}All servers stopped${NC}"
