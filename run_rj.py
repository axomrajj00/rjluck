#!/usr/bin/env python3
"""
RJ Assistant Launcher
Quick launcher for Advanced RJ Assistant
"""

import sys
import os

def main():
    print("🎙️ RJ Assistant Launcher")
    print("=" * 40)
    print("1. Advanced RJ (GUI Mode) - Recommended")
    print("2. Advanced RJ (Console Mode)")
    print("3. Basic RJ Assistant")
    print("4. Exit")
    print()
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == "1":
        print("🚀 Starting Advanced RJ with GUI...")
        os.system("python3 advanced_rj.py")
    elif choice == "2":
        print("🚀 Starting Advanced RJ in Console Mode...")
        os.system("python3 advanced_rj.py --no-gui")
    elif choice == "3":
        print("🚀 Starting Basic RJ Assistant...")
        os.system("python3 rj_assistant.py")
    elif choice == "4":
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please select 1-4.")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)