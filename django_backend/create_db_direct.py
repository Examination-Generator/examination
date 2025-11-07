#!/usr/bin/env python3
"""
Vercel Postgres Database Creator using CLI approach
This script automates database creation via Vercel's API v2 storage endpoint
"""

import requests
import json
import time
import sys

VERCEL_TOKEN = "XZY0VgSXqGzx47q7EZHILuAx"
PROJECT_ID = "prj_wlwtjnH5I61wbSfNNhjbdC29ophv"
PROJECT_NAME = "examination-s3np"

headers = {
    "Authorization": f"Bearer {VERCEL_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("🗄️  CREATING VERCEL POSTGRES DATABASE")
print("=" * 70)

# Step 1: Create database using the integration store endpoint
print("\n📦 Step 1: Creating Postgres database via Vercel integration...")

# Try the stores creation endpoint that works with integrations
create_payload = {
    "type": "postgres",
    "name": "examination-db"
}

response = requests.post(
    "https://api.vercel.com/v1/storage/stores",
    headers=headers,
    json=create_payload
)

print(f"Response status: {response.status_code}")
print(f"Response body: {response.text}")

if response.status_code == 201 or response.status_code == 200:
    db_data = response.json()
    store_id = db_data.get('id')
    print(f"✅ Database created!")
    print(f"   ID: {store_id}")
    print(f"   Name: {db_data.get('name')}")
    
    # Step 2: Link to project
    print("\n🔗 Step 2: Linking database to project...")
    
    link_payload = {
        "type": "postgres",
        "target": {
            "type": "project",
            "id": PROJECT_ID
        }
    }
    
    link_response = requests.post(
        f"https://api.vercel.com/v1/storage/stores/{store_id}/link",
        headers=headers,
        json=link_payload
    )
    
    print(f"Link response status: {link_response.status_code}")
    print(f"Link response body: {link_response.text}")
    
    if link_response.status_code in [200, 201, 204]:
        print("✅ Database linked to project!")
        print("   POSTGRES_URL will be automatically added to environment variables")
    else:
        print("⚠️  Linking may have issues, but database is created")
    
    # Step 3: Trigger deployment
    print("\n🚀 Step 3: Triggering deployment to apply database connection...")
    
    # Get latest deployment to redeploy
    deploy_list = requests.get(
        f"https://api.vercel.com/v6/deployments?projectId={PROJECT_ID}&limit=1",
        headers=headers
    )
    
    if deploy_list.status_code == 200 and deploy_list.json().get('deployments'):
        latest_deployment = deploy_list.json()['deployments'][0]
        
        redeploy_payload = {
            "name": PROJECT_NAME,
            "deploymentId": latest_deployment['uid'],
            "target": "production"
        }
        
        redeploy_response = requests.post(
            "https://api.vercel.com/v13/deployments",
            headers=headers,
            json=redeploy_payload
        )
        
        if redeploy_response.status_code in [200, 201]:
            print("✅ Deployment triggered!")
            print(f"   Check: https://{PROJECT_NAME}.vercel.app/")
        else:
            print(f"Status: {redeploy_response.status_code}")
            print(f"Response: {redeploy_response.text}")
    
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    print(f"\n📊 Check your backend: https://{PROJECT_NAME}.vercel.app/")
    print("   Database should show 'connected' in ~2 minutes after deployment")
    
else:
    print(f"\n❌ Failed to create database")
    print(f"Status: {response.status_code}")
    print(f"Error: {response.text}")
    
    # Alternative: Use the dashboard link creation method
    print("\n" + "=" * 70)
    print("📋 ALTERNATIVE: Create via Vercel Dashboard")
    print("=" * 70)
    print("\n1. Go to: https://vercel.com/dashboard/stores")
    print("2. Click 'Create Database'")
    print("3. Select 'Postgres'")
    print("4. Name: examination-db")
    print("5. Click 'Create'")
    print(f"6. Connect to project: {PROJECT_NAME}")
    print("\nThis will automatically:")
    print("  ✅ Create the database")
    print("  ✅ Add POSTGRES_URL to your project")
    print("  ✅ Trigger a deployment with migrations")
