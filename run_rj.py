#!/usr/bin/env python3
"""
RJ Assistant Launcher - Easy way to start different versions of RJ
"""

import os
import sys
import subprocess

def show_menu():
    """Display launcher menu"""
    print("🤖 RJ ASSISTANT LAUNCHER")
    print("=" * 40)
    print("1. Super Advanced RJ (GUI Mode) - Full features with visual interface")
    print("2. Super Advanced RJ (Console Mode) - Full features, voice only")
    print("3. Text Command RJ - Type commands, smart AI questions")
    print("4. Advanced Coding RJ - VS Code, AI coding, ChatGPT, Screen reading")
    print("5. Advanced RJ (GUI Mode) - Memory + Tasks with GUI")
    print("6. Advanced RJ (Console Mode) - Memory + Tasks, voice only")
    print("7. Basic Enhanced RJ - Core features only")
    print("8. Exit")
    print("=" * 40)

def run_option(choice):
    """Run selected option"""
    try:
        if choice == "1":
            print("🚀 Starting Super Advanced RJ with GUI...")
            subprocess.run([sys.executable, "super_advanced_rj.py"])
        
        elif choice == "2":
            print("🚀 Starting Super Advanced RJ in Console Mode...")
            subprocess.run([sys.executable, "super_advanced_rj.py", "--no-gui"])
        
        elif choice == "3":
            print("🚀 Starting Text Command RJ...")
            subprocess.run([sys.executable, "text_command_rj.py"])
        
        elif choice == "4":
            print("🚀 Starting Advanced Coding RJ...")
            subprocess.run([sys.executable, "advanced_coding_rj.py"])
        
        elif choice == "5":
            print("🚀 Starting Advanced RJ with GUI...")
            subprocess.run([sys.executable, "advanced_rj.py"])
        
        elif choice == "6":
            print("🚀 Starting Advanced RJ in Console Mode...")
            subprocess.run([sys.executable, "advanced_rj.py", "--no-gui"])
        
        elif choice == "7":
            print("🚀 Starting Basic Enhanced RJ...")
            subprocess.run([sys.executable, "enhanced_jarvis.py"])
        
        elif choice == "8":
            print("👋 Goodbye!")
            sys.exit(0)
        
        else:
            print("❌ Invalid choice! Please select 1-8")
            return False
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Make sure all RJ files are in the current directory.")
        return False
    except Exception as e:
        print(f"❌ Error starting RJ: {e}")
        return False

def main():
    """Main launcher function"""
    print("🎯 Welcome to RJ Assistant!")
    print("Choose your preferred version:\n")
    
    while True:
        show_menu()
        choice = input("\n📝 Enter your choice (1-8): ").strip()
        
        if run_option(choice):
            # If option ran successfully, ask if user wants to restart
            restart = input("\n🔄 Start another version? (y/n): ").strip().lower()
            if restart not in ['y', 'yes', 'haan', 'ha']:
                print("👋 Thanks for using RJ Assistant!")
                break
        else:
            # If there was an error, continue the loop
            continue

if __name__ == "__main__":
    main()