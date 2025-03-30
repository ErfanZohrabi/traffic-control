# PowerShell script to prepare your project for GitHub
# Created for the Traffic Control System project

# Check if Git is installed
try {
    Get-Command git -ErrorAction Stop | Out-Null
    Write-Host "Git is installed. Continuing..." -ForegroundColor Green
} catch {
    Write-Host "Git is not installed. Please install it from https://git-scm.com/downloads" -ForegroundColor Red
    Write-Host "Then run this script again." -ForegroundColor Red
    exit 1
}

# Function to ensure directory exists
function EnsureDirectory {
    param (
        [string]$Directory
    )
    
    if (-not (Test-Path $Directory)) {
        New-Item -Path $Directory -ItemType Directory | Out-Null
        Write-Host "Created directory: $Directory" -ForegroundColor Green
    } else {
        Write-Host "Directory already exists: $Directory" -ForegroundColor Cyan
    }
}

# Ensure data and logs directories exist
EnsureDirectory -Directory "data"
EnsureDirectory -Directory "logs"

# Create .gitkeep files in empty directories
$emptyDirs = @("data", "logs")
foreach ($dir in $emptyDirs) {
    $gitkeepPath = Join-Path -Path $dir -ChildPath ".gitkeep"
    if (-not (Test-Path $gitkeepPath)) {
        "" | Set-Content -Path $gitkeepPath
        Write-Host "Created .gitkeep in $dir" -ForegroundColor Green
    }
}

# Check if directory is already a Git repository
if (Test-Path ".git") {
    Write-Host "This directory is already a Git repository." -ForegroundColor Yellow
} else {
    # Initialize Git repository
    git init
    Write-Host "Initialized Git repository." -ForegroundColor Green
}

# Add all files to Git
git add .
Write-Host "Added all files to Git staging area." -ForegroundColor Green

# Check if there are any changes to commit
$status = git status --porcelain
if ($status) {
    # Prompt for commit message
    $commitMessage = Read-Host "Enter commit message (or press Enter for 'Initial commit')"
    if (-not $commitMessage) {
        $commitMessage = "Initial commit"
    }
    
    # Commit changes
    git commit -m $commitMessage
    Write-Host "Committed changes with message: '$commitMessage'" -ForegroundColor Green
    
    Write-Host "`nYour repository is ready for GitHub!" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Create a new repository on GitHub: https://github.com/new" -ForegroundColor Yellow
    Write-Host "2. Run the following commands to link and push to GitHub:" -ForegroundColor Yellow
    Write-Host "   git remote add origin https://github.com/ErfanZohrabi/traffic-control-system.git" -ForegroundColor Cyan
    Write-Host "   git push -u origin master" -ForegroundColor Cyan
} else {
    Write-Host "`nNo changes to commit. Your repository is ready for GitHub!" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Create a new repository on GitHub: https://github.com/new" -ForegroundColor Yellow
    Write-Host "2. Run the following commands to link and push to GitHub:" -ForegroundColor Yellow
    Write-Host "   git remote add origin https://github.com/ErfanZohrabi/traffic-control-system.git" -ForegroundColor Cyan
    Write-Host "   git push -u origin master" -ForegroundColor Cyan
}

Write-Host "`nSee GITHUB_SETUP.md for detailed instructions on setting up GitHub." -ForegroundColor Magenta 