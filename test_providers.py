"""
Quick test script to verify both AI providers are configured correctly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Checking API Configuration...\n")

# Check OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    print("✓ OpenAI API Key: Configured")
    print(f"  Key starts with: {openai_key[:10]}...")
else:
    print("✗ OpenAI API Key: NOT SET")
    print("  Add OPENAI_API_KEY to your .env file")

print()

# Check Google
google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
    print("✓ Google API Key: Configured")
    print(f"  Key starts with: {google_key[:10]}...")
else:
    print("✗ Google API Key: NOT SET")
    print("  Add GOOGLE_API_KEY to your .env file")

print("\n" + "=" * 50)
print("Available Endpoints:")
print("=" * 50)
print("1. POST /api/interpret-art")
print("   Provider: OpenAI GPT-4o")
print("   Status: " + ("✓ Ready" if openai_key else "✗ Not Configured"))
print()
print("2. POST /api/interpret-art-gemini")
print("   Provider: Google Gemini 1.5 Pro")
print("   Status: " + ("✓ Ready" if google_key else "✗ Not Configured"))
print("=" * 50)
