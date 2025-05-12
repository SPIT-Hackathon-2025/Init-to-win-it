#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Path to virtual environment
VENV_PATH="./myenv"

# Log file
LOG_FILE="server_startup.log"
> "$LOG_FILE" # Clear log file

echo -e "${GREEN}===== Setting Up Environment and Starting All Servers =====${NC}"
echo "$(date): Setting up environment and starting all servers" >> "$LOG_FILE"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}Virtual environment doesn't exist at ${YELLOW}$VENV_PATH${NC}"
    echo "$(date): Virtual environment doesn't exist at $VENV_PATH" >> "$LOG_FILE"
    echo -e "${BLUE}Please ensure your virtual environment is properly set up${NC}"
    exit 1
else
    echo -e "${BLUE}Using existing virtual environment at ${YELLOW}$VENV_PATH${NC}"
    echo "$(date): Using existing virtual environment at $VENV_PATH" >> "$LOG_FILE"
fi

echo -e "${GREEN}===== Environment check complete. Starting servers... =====${NC}"
echo "$(date): Environment check complete. Starting servers..." >> "$LOG_FILE"

# Function to check if a file contains Flask app code
contains_flask_app() {
    grep -q "from flask import\|import flask\|Flask(" "$1" 2>/dev/null
}

# Function to start a Flask server
start_flask_server() {
    local file=$1
    local dir=$(dirname "$file")
    local filename=$(basename "$file")
    
    echo -e "${BLUE}Starting Flask server: ${YELLOW}$file${NC}"
    echo "$(date): Starting Flask server: $file" >> "$LOG_FILE"
    
    # Change to the directory and activate virtual environment
    cd "$dir" || return
    
    # Activate virtual environment
    source "$OLDPWD/$VENV_PATH/Scripts/activate"
    
    # Start the Flask server in background
    python "$filename" > "${filename%.py}.log" 2>&1 &
    local pid=$!
    echo $pid > "${filename%.py}.pid"
    echo -e "${GREEN}Started Flask server ${YELLOW}$filename${GREEN} (PID: $pid)${NC}"
    echo "$(date): Started Flask server $filename (PID: $pid)" >> "$OLDPWD/$LOG_FILE"
    
    # Return to the original directory
    cd "$OLDPWD" || return
    
    # Deactivate virtual environment
    deactivate
}

# Function to start Node.js servers
start_node_server() {
    local dir=$1
    local server_type=$2
    
    echo -e "${BLUE}Starting $server_type in ${YELLOW}$dir${NC}"
    echo "$(date): Starting $server_type in $dir" >> "$LOG_FILE"
    
    # Change to the directory
    cd "$dir" || return
    
    if [ "$server_type" = "client" ]; then
        # Use yarn if yarn.lock exists, otherwise npm
        if [ -f "yarn.lock" ]; then
            yarn dev > client.log 2>&1 &
        else
            npm run dev > client.log 2>&1 &
        fi
    else
        # For server.js files
        if [ -f "package.json" ]; then
            # Check if there's a start script in package.json
            if grep -q "\"start\":" "package.json"; then
                if [ -f "yarn.lock" ]; then
                    yarn start > server.log 2>&1 &
                else
                    npm start > server.log 2>&1 &
                fi
            else
                node server.js > server.log 2>&1 &
            fi
        else
            node server.js > server.log 2>&1 &
        fi
    fi
    
    local pid=$!
    echo $pid > "${server_type}.pid"
    echo -e "${GREEN}Started $server_type (PID: $pid)${NC}"
    echo "$(date): Started $server_type (PID: $pid)" >> "$OLDPWD/$LOG_FILE"
    
    # Return to the original directory
    cd "$OLDPWD" || return
}

# Ensure virtual environment exists at this point
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}Virtual environment setup failed${NC}"
    echo "$(date): Virtual environment setup failed" >> "$LOG_FILE"
    exit 1
fi

# Find and start all Flask servers
echo -e "${BLUE}Searching for Flask servers...${NC}"
echo "$(date): Searching for Flask servers" >> "$LOG_FILE"

# Array to store all found Flask servers
FLASK_SERVERS=()

# Find all Python files that contain Flask app
while IFS= read -r file; do
    if contains_flask_app "$file"; then
        FLASK_SERVERS+=("$file")
    fi
done < <(find . -type f -name "*.py" -not -path "*/\.*" -not -path "*/myenv/*" -not -path "*/node_modules/*")

# Start all Flask servers
for server in "${FLASK_SERVERS[@]}"; do
    start_flask_server "$server"
    # Add a small delay to avoid resource contention
    sleep 2
done

# Start client
if [ -d "./client" ]; then
    echo -e "${BLUE}Starting client...${NC}"
    echo "$(date): Starting client" >> "$LOG_FILE"
    start_node_server "./client" "client"
fi

# Start server
if [ -d "./server" ] && [ -f "./server/server.js" ]; then
    echo -e "${BLUE}Starting Node.js server...${NC}"
    echo "$(date): Starting Node.js server" >> "$LOG_FILE"
    start_node_server "./server" "server"
fi

# Check for any other Node.js servers
while IFS= read -r file; do
    dir=$(dirname "$file")
    if [ "$dir" != "./client" ] && [ "$dir" != "./server" ]; then
        echo -e "${BLUE}Starting additional Node.js server: ${YELLOW}$dir${NC}"
        echo "$(date): Starting additional Node.js server in $dir" >> "$LOG_FILE"
        start_node_server "$dir" "node-$(basename "$dir")"
    fi
done < <(find . -name "package.json" -not -path "*/node_modules/*" -not -path "./client/*" -not -path "./server/*")

echo -e "${GREEN}===== All servers started =====${NC}"
echo -e "Check ${YELLOW}$LOG_FILE${NC} for more details"
echo "$(date): All servers started" >> "$LOG_FILE"

# Create a stop script
cat > stop_all_servers.sh << 'EOF'
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
EOF

chmod +x stop_all_servers.sh
echo -e "${GREEN}Created ${YELLOW}stop_all_servers.sh${GREEN} to stop all servers${NC}"
echo "$(date): Created stop_all_servers.sh" >> "$LOG_FILE"