# Ensure script is running with administrative privileges
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "You need to run this script as an Administrator!" -ForegroundColor Red
    exit
}

# Create a virtual environment
Write-Host "Creating a virtual environment..."
python -m venv venv

# Moving certain files to the virtual environment directory
Write-Host "Moving certain files to the virtual environment directory..."
mv 

# Activate the virtual environment
Write-Host "Activating the virtual environment..."
.\venv\Scripts\activate

# Navigate to the virtual environment directory
Write-Host "Navigating to the virtual environment directory..."
cd .\venv\

# Install application dependencies
Write-Host "Installing application dependencies..."
pip install -r .\requirements.txt

# Install application dependencies
Write-Host "Installing application dependencies..."
npm install

# Set up environment variables
Write-Host "Setting up environment variables..."
$env:APP_ENV = "development"
$env:DB_CONNECTION_STRING = "your_connection_string"

# Run database migrations
Write-Host "Running database migrations..."
npm run migrate

# Start the application
Write-Host "Starting the application..."
npm start

Write-Host "Setup complete!" -ForegroundColor Green