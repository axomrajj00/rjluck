#!/usr/bin/env python3
"""
RJ Assistant Launcher
Quick launcher for Advanced RJ Assistant
"""

import sys
import os

def main():
    print("🎙️ RJ Assistant Launcher")
    print("=" * 50)
    print("1. 🚀 Super Advanced RJ (GUI Mode) - RECOMMENDED")
    print("2. 🎮 Super Advanced RJ (Console Mode)")
    print("3. 📱 Advanced RJ (GUI Mode)")
    print("4. 💻 Advanced RJ (Console Mode)")
    print("5. 📞 Basic RJ Assistant")
    print("6. 🚪 Exit")
    print()
    print("✨ New Features in Super Advanced RJ:")
    print("   • Sleep Mode (30 sec timeout)")
    print("   • 'Hello RJ' activation")
    print("   • 'RJ stop' to pause")
    print("   • Capabilities showcase")
    print("   • Enhanced entertainment")
    print("   • Smart wake/sleep system")
    print()
    
    choice = input("Select option (1-6): ").strip()
    
    if choice == "1":
        print("🚀 Starting Super Advanced RJ with GUI...")
        print("💡 Say 'Hello RJ' to activate!")
        print("💡 Say 'RJ kya kya kar sakte ho' to see capabilities!")
        os.system("python3 super_advanced_rj.py")
    elif choice == "2":
        print("🚀 Starting Super Advanced RJ in Console Mode...")
        print("💡 Say 'Hello RJ' to activate!")
        os.system("python3 super_advanced_rj.py --no-gui")
    elif choice == "3":
        print("📱 Starting Advanced RJ with GUI...")
        os.system("python3 advanced_rj.py")
    elif choice == "4":
        print("📱 Starting Advanced RJ in Console Mode...")
        os.system("python3 advanced_rj.py --no-gui")
    elif choice == "5":
        print("📞 Starting Basic RJ Assistant...")
        os.system("python3 rj_assistant.py")
    elif choice == "6":
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please select 1-6.")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)