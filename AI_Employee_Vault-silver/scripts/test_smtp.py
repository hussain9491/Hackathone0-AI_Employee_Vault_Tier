#!/usr/bin/env python3
"""Test SMTP connection directly"""

import os
import smtplib
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get credentials
smtp_user = os.environ.get('SMTP_USER')
smtp_pass = os.environ.get('SMTP_PASS')
smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
smtp_port = int(os.environ.get('SMTP_PORT', 587))

print("=" * 60)
print("SMTP CONNECTION TEST")
print("=" * 60)

print(f"\nSMTP_USER: {smtp_user}")
print(f"SMTP_PASS: {'*' * len(smtp_pass) if smtp_pass else 'NOT SET'}")
print(f"SMTP_PASS length: {len(smtp_pass) if smtp_pass else 0} characters")
print(f"SMTP_HOST: {smtp_host}")
print(f"SMTP_PORT: {smtp_port}")

if not smtp_user or not smtp_pass:
    print("\n❌ ERROR: SMTP credentials not loaded!")
    print("Check that .env file exists and has correct format")
    exit(1)

try:
    print(f"\n🔌 Connecting to {smtp_host}:{smtp_port}...")
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    server.starttls()
    print(f"✅ Connected successfully")
    
    print(f"🔐 Authenticating as {smtp_user}...")
    server.login(smtp_user, smtp_pass)
    print(f"✅ Authentication successful!")
    
    server.quit()
    print("\n" + "=" * 60)
    print("✅ SMTP TEST PASSED - Real email sending should work!")
    print("=" * 60)
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentication failed!")
    print(f"Error code: {e.smtp_code}")
    print(f"Error message: {e.smtp_error}")
    print("\nThis usually means:")
    print("1. App Password is incorrect")
    print("2. Using regular password instead of App Password")
    print("3. 2FA not enabled on Google Account")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
