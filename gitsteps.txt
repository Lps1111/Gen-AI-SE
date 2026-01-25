Git Download in windows - https://git-scm.com/downloads/win

Git Bash download - https://gitforwindows.org/

ssh-keygen -t ed25519 -C "your_email@example.com
"

eval "$(ssh-agent -s)"

ssh-add ~/.ssh/id_ed25519

cat ~/.ssh/id_ed25519.pub

Add SSH Key to the GitHub and check it in the VS code

ssh -T git@github.com
 -- Verify the GitHub

git clone <url>

git branch

git branch -a

git checkout -b <branch name>

git add <file name>

git commit -m "message"
