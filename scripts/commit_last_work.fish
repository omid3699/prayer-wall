#!/usr/bin/env fish
# Script to stage and commit the recent changes made by the assistant.
# Run from the project root: ./scripts/commit_last_work.fish

# Stage the files we edited/created
git add apps/users/models.py apps/users/admin.py apps/users/migrations/0003_remove_user_usermae.py

# Commit with a short message
git commit -m "Fix admin: show username (remove misspelled 'usermae')"
