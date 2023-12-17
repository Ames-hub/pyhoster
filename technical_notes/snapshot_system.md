# Snapshots / Backup System.
Do not remember how this works. Haven't had a look at it yet, but when I do I'll document it here.

So far I know that BASICALLY what it does is:
- It takes a snapshot of the website's folder (root, not just content)
- It stores the snapshot either internally in ./backups or externally in a folder of your choice or "%appdata%" on windows. Don't remember where it stores it on linux.
- When you want to revert, it just copies the snapshot back to the website's folder overwriting everything else.

There's also an auto-backup thread running somewhere.