#!/usr/bin/env python3
"""
Simple Artwork Testing Script for Art Backend API
Tests artwork retrieval for a specific user with JWT authentication
"""

import requests
import json
import sys
import os
from typing import Optional, Dict, Any


class ArtworkTester:
    """Simple tester for artwork retrieval with JWT auth"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_user_artworks(
        self, user_id: str, jwt_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get artworks for a specific user with optional JWT authentication"""
        endpoint = f"/api/user/{user_id}/artworks"
        url = f"{self.base_url}{endpoint}"

        # Prepare headers
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
            print(f"🔐 Using JWT authentication")
            print(f"🎫 Token: {jwt_token[:50]}...")
        else:
            print(f"🔓 No authentication token provided")

        try:
            print(f"🔍 Fetching artworks for user: {user_id}")
            print(f"📡 Request URL: {url}")
            if headers:
                print(f"📋 Headers: {headers}")

            response = self.session.get(url, headers=headers)

            print(f"📊 Response Status: {response.status_code}")

            if response.status_code == 200:
                artworks = response.json()
                print(f"✅ Success! Found {len(artworks)} artworks")

                if artworks:
                    print(f"\n📋 Artwork Details:")
                    for i, artwork in enumerate(artworks, 1):
                        print(f"  {i}. Artwork ID: {artwork.get('artwork_id', 'N/A')}")
                        print(f"     Created: {artwork.get('created_at', 'N/A')}")
                        print(f"     Creator: {artwork.get('creator_user_id', 'N/A')}")
                        if artwork.get("image_url"):
                            print(f"     Image: {artwork.get('image_url')}")
                        print()
                else:
                    print("📭 No artworks found for this user")

                return artworks
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

    def test_health(self) -> bool:
        """Test if the API server is running"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print(f"✅ API server is running")
                return True
            else:
                print(f"⚠️  API server responded with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API server: {str(e)}")
            print(f"💡 Make sure the server is running on {self.base_url}")
            return False


def load_token_from_file() -> Optional[str]:
    """Load JWT token from file if it exists"""
    token_file = "supabase_token.txt"
    if os.path.exists(token_file):
        try:
            with open(token_file, "r") as f:
                token = f.read().strip()
                if token:
                    print(f"📁 Loaded token from {token_file}")
                    return token
        except Exception as e:
            print(f"⚠️  Could not read token file: {e}")
    return None


def main():
    """Main function"""
    print("🎨 Art Backend - Artwork Tester with JWT Auth")
    print("=" * 50)

    tester = ArtworkTester()

    # Test if server is running
    if not tester.test_health():
        return

    # Get JWT token
    jwt_token = None

    # Try to get token from command line arguments
    if len(sys.argv) > 1:
        # Check if first arg is a token (starts with eyJ)
        if sys.argv[1].startswith("eyJ"):
            jwt_token = sys.argv[1]
            print(f"🎫 Using provided JWT token: {jwt_token[:50]}...")
            user_id = sys.argv[2] if len(sys.argv) > 2 else None
        else:
            # First arg is user ID
            user_id = sys.argv[1]
            print(f"Using provided user ID: {user_id}")
            # Try to load token from file
            jwt_token = load_token_from_file()
    else:
        # Try to load token from file first
        jwt_token = load_token_from_file()

        # Get user ID from prompt
        user_id = input("\n👤 Enter user ID: ").strip()
        if not user_id:
            print("❌ User ID is required")
            return

    # If no token found, ask user
    if not jwt_token:
        print(f"\n🔐 JWT Token Options:")
        print(f"  1. Enter token manually")
        print(f"  2. Run 'python get_supabase_token.py' first to generate one")
        print(f"  3. Skip authentication (test without token)")

        choice = input("\nChoose option (1/2/3): ").strip()

        if choice == "1":
            jwt_token = input("Enter JWT token: ").strip()
            if not jwt_token:
                print("❌ Token cannot be empty")
                return
        elif choice == "2":
            print(
                "💡 Please run 'python get_supabase_token.py' first, then run this script again"
            )
            return
        elif choice == "3":
            print("🔓 Testing without authentication")
        else:
            print("❌ Invalid choice")
            return

    print()

    # Test artwork retrieval with JWT token
    tester.get_user_artworks(user_id, jwt_token)

    print(f"\n✅ Test completed!")
    print(f"💡 Check your server logs to see the middleware authentication details")


if __name__ == "__main__":
    main()
