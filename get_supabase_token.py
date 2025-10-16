#!/usr/bin/env python3
"""
Helper script to get Supabase JWT tokens for testing
This script demonstrates how to authenticate with Supabase and get a JWT token
"""

import requests
import json
import os
from typing import Optional, Dict, Any


class SupabaseTokenHelper:
    """Helper class to get Supabase JWT tokens"""

    def __init__(self, supabase_url: str, supabase_anon_key: str):
        self.supabase_url = supabase_url.rstrip("/")
        self.supabase_anon_key = supabase_anon_key
        self.session = requests.Session()
        self.session.headers.update(
            {"apikey": supabase_anon_key, "Content-Type": "application/json"}
        )

    def sign_up(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Sign up a new user"""
        url = f"{self.supabase_url}/auth/v1/signup"
        data = {"email": email, "password": password}

        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Sign up failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Sign up error: {str(e)}")
            return None

    def sign_in(self, email: str, password: str) -> Optional[str]:
        """Sign in and get JWT token"""
        url = f"{self.supabase_url}/auth/v1/token?grant_type=password"
        data = {"email": email, "password": password}

        try:
            response = self.session.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                return result.get("access_token")
            else:
                print(f"❌ Sign in failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Sign in error: {str(e)}")
            return None

    def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from JWT token"""
        url = f"{self.supabase_url}/auth/v1/user"
        headers = {"Authorization": f"Bearer {token}", "apikey": self.supabase_anon_key}

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"❌ Get user info failed: {response.status_code} - {response.text}"
                )
                return None
        except Exception as e:
            print(f"❌ Get user info error: {str(e)}")
            return None


def main():
    """Main function to demonstrate token retrieval"""
    print("🔑 Supabase JWT Token Helper")
    print("=" * 40)

    # Get Supabase configuration from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase configuration!")
        print("Please set SUPABASE_URL and SUPABASE_KEY environment variables")
        print("\nExample:")
        print("export SUPABASE_URL='https://your-project.supabase.co'")
        print("export SUPABASE_KEY='your-anon-key'")
        return

    print(f"✅ Supabase URL: {supabase_url}")
    print(f"✅ Supabase Key: {supabase_key[:20]}...")

    helper = SupabaseTokenHelper(supabase_url, supabase_key)

    # Get credentials from user
    print("\n📝 Enter your Supabase credentials:")
    email = input("Email: ").strip()
    password = input("Password: ").strip()

    if not email or not password:
        print("❌ Email and password are required")
        return

    # Try to sign in
    print(f"\n🔐 Attempting to sign in...")
    token = helper.sign_in(email, password)

    if token:
        print(f"✅ Successfully signed in!")
        print(f"🎫 JWT Token: {token[:50]}...")

        # Get user info
        print(f"\n👤 Getting user information...")
        user_info = helper.get_user_info(token)
        if user_info:
            print(f"✅ User ID: {user_info.get('id', 'N/A')}")
            print(f"✅ Email: {user_info.get('email', 'N/A')}")

        # Save token to file for easy testing
        token_file = "supabase_token.txt"
        with open(token_file, "w") as f:
            f.write(token)
        print(f"\n💾 Token saved to: {token_file}")
        print(f"\n🧪 Now you can test with:")
        print(f"   python test_jwt_auth.py {token}")

    else:
        print(f"\n❌ Sign in failed. You may need to:")
        print(f"   1. Create an account first")
        print(f"   2. Check your email/password")
        print(f"   3. Verify your Supabase configuration")


if __name__ == "__main__":
    main()
