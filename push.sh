#!/bin/bash
read -p "Enter your GitHub username: " USERNAME
git init
git add README.md
git commit -m "Add GitHub profile README"
git remote add origin https://github.com/$USERNAME/$USERNAME.git
git branch -M main
git push -u origin main
echo "Done! Visit https://github.com/$USERNAME to see your profile."
