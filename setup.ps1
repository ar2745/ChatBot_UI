# Ensure script is running with administrative privileges
# if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
#     Write-Host "You need to run this script as an Administrator!" -ForegroundColor Red
#     Start-Process powershell -ArgumentList "-File", $PSCommandPath -Verb RunAs
#     exit
# }

# Define the repository URL and the directory name
$repoUrl = "https://github.com/ar2745/ChatBot_UI.git"
$repoDir = "ChatBot_UI"

# Clone the repository
Write-Host "Cloning the repository..."
git clone $repoUrl

# Change to the newly cloned directory
Write-Host "Changing to the newly cloned directory..."
Set-Location -Path $repoDir

# Create a virtual environment
Write-Host "Creating a virtual environment..."
python -m venv venv

# Moving certain files to the virtual environment directory
Write-Host "Moving certain files to the virtual environment directory..."
mv .\src\ .\venv\
# mv .\requirements.txt .\venv\
# mv .\package.json .\venv\
# mv .\package-lock.json .\venv\
# mv .\tsconfig.json .\venv\
# mv .\public\ .\venv\
# mv .\ollama\ .\venv\

# Activate the virtual environment
# Write-Host "Activating the virtual environment..."
# .\venv\Scripts\activate

# Navigate to the virtual environment directory
# Write-Host "Navigating to the virtual environment directory..."
# cd .\venv\

# Install application dependencies
# Write-Host "Installing application dependencies..."
# pip install -r .\requirements.txt

# Install npm dependencies
# Write-Host "Installing npm dependencies..."
# npm install

# Start the chatbot application
# Write-host "Starting the chatbot application..."
# cd .\src\app
# python chatbot.py

# Start the Ollama server
# Write-Host "Starting the Ollama server..."
# cd ..
# cd .\ollama
# .\ollama.exe serve

# # Start the npm development server
# Write-Host "Starting the npm development server..."
# cd ..
# npm start

Write-Host "Setup complete!" -ForegroundColor Green
# Keep the PowerShell window open
Read-Host -Prompt "Press Enter to exit"