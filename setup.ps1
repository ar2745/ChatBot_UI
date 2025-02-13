## cd back to the root directory
cd ..

# Remove the existing ChatBot_UI directory
Write-Host "Removing the existing ChatBot_UI directory..."
Remove-Item -Path .\ChatBot_UI -Recurse -Force

# Define the repository URL and the directory name
$repoUrl = "https://github.com/ar2745/ChatBot_UI.git"
$repoDir = "ChatBot_UI"

# Clone the repository
Write-Host "Cloning the repository..."
git clone $repoUrl

# Change to the newly cloned directory
Write-Host "Changing to the newly cloned directory..."
$repoDir = "ChatBot_UI"
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

# Activate the virtual environment
Write-Host "Activating the virtual environment..."
.\venv\Scripts\activate

# Navigate to the virtual environment directory
Write-Host "Navigating to the virtual environment directory..."
cd .\venv\

# Update pip
Write-Host "Updating pip..."
python -m pip install --upgrade pip

# Install application dependencies
Write-Host "Installing application dependencies..."
pip install -r .\requirements.txt

# Install npm dependencies
Write-Host "Installing npm dependencies..."
npm install

# Setup complete
Write-Host "Setup complete!" -ForegroundColor Green
# Keep the PowerShell window open
Read-Host -Prompt "Press Enter to exit"