"""
Quick test script to verify Gemini AI provider is configured correctly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Checking API Configuration...\n")

# Check Google Gemini
google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
    print("✓ Google Gemini API Key: Configured")
    print(f"  Key starts with: {google_key[:10]}...")
else:
    print("✗ Google Gemini API Key: NOT SET")
    print("  Add GOOGLE_API_KEY to your .env file")

print("\n" + "=" * 50)
print("Available Endpoints:")
print("=" * 50)
print("1. POST /ai/artwork/explain")
print("   Provider: Google Gemini 1.5 Pro")
print("   Status: " + ("✓ Ready" if google_key else "✗ Not Configured"))
print()
print("2. POST /ai/artwork/explain-from-image")
print("   Provider: Google Gemini 1.5 Pro")
print("   Status: " + ("✓ Ready" if google_key else "✗ Not Configured"))
print()
print("3. POST /ai/artwork/expand")
print("   Provider: Google Gemini 1.5 Pro")
print("   Status: " + ("✓ Ready" if google_key else "✗ Not Configured"))
print("=" * 50)
