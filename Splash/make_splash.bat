@echo off

echo "Making splash..."

pypy images.py
armips.exe splash.asm