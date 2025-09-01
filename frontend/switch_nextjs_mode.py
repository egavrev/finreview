#!/usr/bin/env python3
"""
Script to switch Next.js between network and localhost modes
"""

import os
import sys
import subprocess

def get_local_ip():
    """Get the local IP address"""
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'inet ' in line and '127.0.0.1' not in line:
                return line.split()[1]
    except:
        pass
    return "192.168.0.6"  # fallback

def update_package_json(mode):
    """Update package.json scripts for the specified mode"""
    package_json_path = "package.json"
    
    with open(package_json_path, 'r') as f:
        content = f.read()
    
    if mode == "network":
        # Network mode - enable network access
        content = content.replace(
            '"dev": "next dev"',
            '"dev": "next dev -H 0.0.0.0"'
        )
        content = content.replace(
            '"dev:localhost": "next dev"',
            '"dev:localhost": "next dev"'
        )
    else:
        # Localhost mode - restrict to localhost
        content = content.replace(
            '"dev": "next dev -H 0.0.0.0"',
            '"dev": "next dev"'
        )
        content = content.replace(
            '"dev:localhost": "next dev"',
            '"dev:localhost": "next dev"'
        )
    
    with open(package_json_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Next.js package.json updated for {mode} mode")

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["network", "localhost"]:
        print("Usage: python switch_nextjs_mode.py [network|localhost]")
        print("")
        print("  network    - Enable Next.js access from mobile devices")
        print("  localhost  - Restrict Next.js to localhost only")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    print(f"🔄 Switching Next.js to {mode} mode...")
    
    # Update package.json
    update_package_json(mode)
    
    if mode == "network":
        local_ip = get_local_ip()
        print(f"📱 Next.js network mode enabled!")
        print(f"   Your local IP: {local_ip}")
        print(f"   Mobile access: http://{local_ip}:3000")
        print("")
        print("To start Next.js with network access:")
        print("   npm run dev")
    else:
        print("🔒 Next.js localhost mode enabled!")
        print("   Access restricted to localhost only")
        print("")
        print("To start Next.js with localhost only:")
        print("   npm run dev")
    
    print("")
    print("Note: You'll need to restart Next.js for changes to take effect.")

if __name__ == "__main__":
    main()

