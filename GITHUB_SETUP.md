# GitHub Setup Guide

This guide will help you set up your Traffic Control System project on GitHub.

## Prerequisites

1. [GitHub account](https://github.com/join) - Create one if you don't have it already
2. Git installed on your computer
   - [Download Git](https://git-scm.com/downloads)
   - Verify installation: `git --version`

## Option 1: Using GitHub Desktop (Easiest)

GitHub Desktop provides a user-friendly interface for Git operations.

1. Download and install [GitHub Desktop](https://desktop.github.com/)
2. Sign in with your GitHub account
3. In GitHub Desktop:
   - Click "File" > "Add local repository"
   - Browse to your traffic control project folder
   - Click "Add repository"
4. Create a repository on GitHub:
   - Click "Publish repository"
   - Enter repository name: `traffic-control-system`  
   - Add a description (optional)
   - Choose whether to keep the code private or public
   - Click "Publish Repository"

## Option 2: Using Git Command Line

If you prefer the command line:

1. Open a terminal or command prompt
2. Navigate to your traffic control project folder:
   ```bash
   cd path/to/traffic-control-system
   ```
3. Initialize a new Git repository (if you haven't already):
   ```bash
   git init
   ```
4. Add all project files to the staging area:
   ```bash
   git add .
   ```
5. Commit the files:
   ```bash
   git commit -m "Initial commit"
   ```
6. Create a new repository on GitHub:
   - Go to [https://github.com/new](https://github.com/new)
   - Name your repository `traffic-control-system`
   - Do NOT initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"
7. Link your local repository with the GitHub repository:
   ```bash
   git remote add origin https://github.com/ErfanZohrabi/traffic-control-system.git
   ```
8. Push your code to GitHub:
   ```bash
   git push -u origin main
   ```
   - Note: If you're using an older Git version, your default branch might be called "master" instead of "main":
     ```bash
     git push -u origin master
     ```

## Verify Your Repository

1. Visit your GitHub profile: [https://github.com/ErfanZohrabi](https://github.com/ErfanZohrabi)
2. You should see your new `traffic-control-system` repository
3. Click on it to view all your uploaded files

## Next Steps

After setting up your GitHub repository, consider:

1. Setting up GitHub Actions for continuous integration
2. Creating issue templates for bug reports and feature requests
3. Adding GitHub project boards to track development
4. Enabling GitHub Pages to host documentation

## Keeping Your Repository Updated

Whenever you make changes to your project:

1. Add modified files:
   ```bash
   git add .
   ```
2. Commit changes:
   ```bash
   git commit -m "Describe your changes here"
   ```
3. Push to GitHub:
   ```bash
   git push
   ```

## Help and Support

If you encounter any issues, contact:
- Project maintainer: [erfanzohrabi.ez@gmail.com](mailto:erfanzohrabi.ez@gmail.com)
- GitHub Support: [https://support.github.com/](https://support.github.com/) 