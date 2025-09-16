#!/bin/bash

# Flight Service AI - Environment Setup Script
echo "Setting up environment variables for Flight Service AI..."

# Create .env file for backend
ENV_FILE="backend/.env"

# Check if .env file already exists
if [ -f "$ENV_FILE" ]; then
    echo "Environment file already exists at $ENV_FILE"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Create backend directory if it doesn't exist
mkdir -p backend

# Prompt for Azure AI credentials
echo ""
echo "Please provide your Azure AI credentials:"
read -p "Azure Project Endpoint (e.g., https://your-project.eastus2.ai.azure.com/): " project_endpoint
read -p "Agent ID (from Azure AI Foundry): " agent_id

# Validate inputs
if [ -z "$project_endpoint" ] || [ -z "$agent_id" ]; then
    echo "Error: Project Endpoint and Agent ID are required."
    echo ""
    echo "NOTE: This application uses Azure DefaultAzureCredential for authentication."
    echo "Please ensure you're logged in with 'az login' before running the service."
    exit 1
fi

# Create .env file
cat > "$ENV_FILE" << EOF
# Azure AI Configuration
PROJECT_ENDPOINT=$project_endpoint
AGENT_ID=$agent_id

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# CORS Configuration
CORS_ORIGINS=http://localhost:5173

# API Configuration
API_TIMEOUT=30
EOF

echo ""
echo "Environment file created successfully at $ENV_FILE"

# Create .env.example file for reference
cat > "backend/.env.example" << EOF
# Azure AI Configuration
PROJECT_ENDPOINT=https://your-project.eastus2.ai.azure.com/
AGENT_ID=your-agent-id-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# CORS Configuration
CORS_ORIGINS=http://localhost:5173

# API Configuration
API_TIMEOUT=30
EOF

echo "Example environment file created at backend/.env.example"

# Update .gitignore to exclude .env files
GITIGNORE_FILE=".gitignore"
if [ ! -f "$GITIGNORE_FILE" ]; then
    touch "$GITIGNORE_FILE"
fi

# Check if .env is already in .gitignore
if ! grep -q "\.env" "$GITIGNORE_FILE"; then
    echo "" >> "$GITIGNORE_FILE"
    echo "# Environment files" >> "$GITIGNORE_FILE"
    echo ".env" >> "$GITIGNORE_FILE"
    echo "backend/.env" >> "$GITIGNORE_FILE"
    echo "Updated .gitignore to exclude environment files"
fi

echo ""
echo "Setup completed successfully!"
echo "You can now run the backend with: cd backend && python backend.py"
echo ""
echo "Note: Make sure to install required Python packages:"
echo "pip install python-dotenv azure-ai-agents"