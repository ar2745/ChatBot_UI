# Set-Location -Path $repoDir
$repoDir = $PSScriptRoot
Set-Location -Path $repoDir

# Create a virtual environment
Write-Host "Creating a virtual environment..."
python -m venv venv

# Moving certain files to the virtual environment directory
Write-Host "Moving certain files to the virtual environment directory..."
mv .\src\ .\venv\
mv .\requirements.txt .\venv\
mv .\package.json .\venv\
mv .\public\ .\venv\
mv .\ollama\ .\venv\
rm .\setup.ps1

# Activate the virtual environment
Write-Host "Activating the virtual environment..."
.\venv\Scripts\activate

# Navigate to the virtual environment directory
Write-Host "Navigating to the virtual environment directory..."
cd .\venv\

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install application dependencies
Write-Host "Installing application dependencies..."
pip install -r .\requirements.txt

# Install npm dependencies
Write-Host "Installing npm dependencies..."
npm install

Write-Host "Setup complete!" -ForegroundColor Green
# Keep the PowerShell window open
Read-Host -Prompt "Press Enter to exit"