#!/usr/bin/env python3
"""
Interactive User Registration Script
Handles complete registration flow with OTP verification
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "https://examination-s3np.vercel.app/api"

def print_step(step_num, title):
    """Print formatted step header"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✓ {message}")

def print_error(message):
    """Print error message"""
    print(f"✗ ERROR: {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ {message}")

def make_request(method, endpoint, data=None, headers=None):
    """Make HTTP request and handle response"""
    url = f"{BASE_URL}/{endpoint}"
    
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    try:
        print_info(f"Sending {method} request to {url}")
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print_info(f"Response Status: {response.status_code}")
        
        # Try to parse JSON response
        try:
            json_response = response.json()
            print_info(f"Response: {json.dumps(json_response, indent=2)}")
            return response.status_code, json_response
        except:
            print_info(f"Response Text: {response.text}")
            return response.status_code, {"text": response.text}
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None, None

def main():
    """Main registration flow"""
    
    print("\n" + "="*60)
    print("EXAMINATION SYSTEM - USER REGISTRATION")
    print("="*60)
    
    # Gather user information
    print("\nPlease provide user details:")
    print("-" * 60)
    
    phone_number = input("Phone Number (e.g., 1234567890): ").strip()
    full_name = input("Full Name: ").strip()
    password = input("Password: ").strip()
    
    print("\nSelect Role:")
    print("1. user (regular user)")
    print("2. editor (can create/edit content)")
    print("3. admin (full access)")
    role_choice = input("Enter choice (1-3) [default: 2 for editor]: ").strip() or "2"
    
    role_map = {
        "1": "user",
        "2": "editor",
        "3": "admin"
    }
    role = role_map.get(role_choice, "editor")
    
    print(f"\n📋 Registration Summary:")
    print(f"   Phone: {phone_number}")
    print(f"   Name: {full_name}")
    print(f"   Role: {role}")
    print(f"   Password: {'*' * len(password)}")
    
    confirm = input("\nProceed with registration? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Registration cancelled.")
        return
    
    # STEP 1: Request OTP
    print_step(1, "REQUEST OTP")
    
    otp_request_data = {
        "phone_number": phone_number,
        "purpose": "registration"
    }
    
    status, response = make_request('POST', 'send-otp', otp_request_data)
    
    if status and status in [200, 201]:
        print_success("OTP sent successfully!")
        if response and 'message' in response:
            print_info(f"Message: {response['message']}")
    else:
        print_error("Failed to send OTP")
        if response:
            print_error(f"Details: {response}")
        return
    
    # STEP 2: Verify OTP
    print_step(2, "VERIFY OTP")
    print_info("Check your phone/console for the OTP code")
    
    otp_code = input("\nEnter the OTP code you received: ").strip()
    
    otp_verify_data = {
        "phone_number": phone_number,
        "otp": otp_code,
        "purpose": "registration"
    }
    
    status, response = make_request('POST', 'verify-otp', otp_verify_data)
    
    if status and status in [200, 201]:
        print_success("OTP verified successfully!")
        if response and 'message' in response:
            print_info(f"Message: {response['message']}")
    else:
        print_error("OTP verification failed")
        if response:
            print_error(f"Details: {response}")
        return
    
    # STEP 3: Complete Registration
    print_step(3, "COMPLETE REGISTRATION")
    
    registration_data = {
        "phone_number": phone_number,
        "full_name": full_name,
        "password": password,
        "role": role
    }
    
    status, response = make_request('POST', 'register', registration_data)
    
    if status and status in [200, 201]:
        print_success("Registration completed successfully!")
        print("\n" + "="*60)
        print("USER REGISTERED SUCCESSFULLY! 🎉")
        print("="*60)
        
        if response and 'data' in response:
            data = response['data']
            if 'user' in data:
                user = data['user']
                print(f"\nUser Details:")
                print(f"  ID: {user.get('id')}")
                print(f"  Name: {user.get('fullName')}")
                print(f"  Phone: {user.get('phoneNumber')}")
                print(f"  Role: {user.get('role')}")
            
            if 'token' in data:
                print(f"\nAuthentication Token:")
                print(f"  {data['token'][:50]}...")
                print("\n💾 Save this token for API requests!")
        
        print("\n✓ You can now login with these credentials")
        
    else:
        print_error("Registration failed")
        if response:
            print_error(f"Details: {response}")
        return
    
    print("\n" + "="*60)
    print("REGISTRATION PROCESS COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nRegistration cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
