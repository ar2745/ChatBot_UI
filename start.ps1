# Start the chatbot application
Write-Host "Starting the chatbot application..."
Start-Process powershell -ArgumentList "cd `"$PWD\venv\src\app`"; python chatbot.py"

# Start the Ollama server
Write-Host "Starting the Ollama server..."
Start-Process powershell -ArgumentList "cd `"$PWD\venv\ollama`"; .\ollama.exe serve"

# Start the npm development server
Write-Host "Starting the npm development server..."
Start-Process powershell -ArgumentList "cd `"$PWD\venv`"; npm start"

# Setup complete
Write-Host "Setup complete!" -ForegroundColor Green