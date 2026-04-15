#!/bin/bash
# Run this once after cloning to make 'git status' also execute all tests.
git config alias.status '!python3 -m pytest tests/ -v && git status --short'
echo "Git hook installed. 'git status' will now run all tests first."
