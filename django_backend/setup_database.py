#!/usr/bin/env python3
"""
Automatic Vercel Postgres Database Provisioning Script
This script automatically creates and configures a Vercel Postgres database

Usage:
    python setup_database.py --token YOUR_VERCEL_TOKEN
"""

import os
import sys
import json
import requests
import time
from argparse import ArgumentParser

class VercelDatabaseSetup:
    """Handles automatic Vercel Postgres database creation and configuration"""
    
    def __init__(self, token, team_id=None):
        self.token = token
        self.team_id = team_id
        self.base_url = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method, endpoint, data=None):
        """Make authenticated request to Vercel API"""
        url = f"{self.base_url}{endpoint}"
        if self.team_id:
            url += f"?teamId={self.team_id}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None
    
    def find_project(self, project_name=None):
        """Find the backend project"""
        print("\n🔍 Finding backend project...")
        
        projects = self._make_request("GET", "/v9/projects")
        if not projects:
            return None
        
        # If project name provided, search for it
        if project_name:
            for project in projects.get('projects', []):
                if project_name.lower() in project['name'].lower():
                    print(f"✅ Found project: {project['name']} (ID: {project['id']})")
                    return project
        
        # Otherwise, look for examination/backend related projects
        for project in projects.get('projects', []):
            name_lower = project['name'].lower()
            if any(keyword in name_lower for keyword in ['examination', 'backend', 'django', 's3np']):
                print(f"✅ Found project: {project['name']} (ID: {project['id']})")
                return project
        
        # If still not found, show all projects
        print("\n📋 Available projects:")
        for i, project in enumerate(projects.get('projects', []), 1):
            print(f"  {i}. {project['name']} (ID: {project['id']})")
        
        return None
    
    def check_existing_databases(self):
        """Check for existing Postgres databases"""
        print("\n🔍 Checking for existing databases...")
        
        stores = self._make_request("GET", "/v1/storage/stores")
        if not stores:
            return []
        
        postgres_dbs = [s for s in stores.get('stores', []) if s.get('type') == 'postgres']
        
        if postgres_dbs:
            print(f"✅ Found {len(postgres_dbs)} existing Postgres database(s):")
            for db in postgres_dbs:
                print(f"  - {db.get('name')} (ID: {db.get('id')})")
        else:
            print("ℹ️  No existing Postgres databases found")
        
        return postgres_dbs
    
    def create_database(self, name="examination-db", region="us-east-1"):
        """Create a new Vercel Postgres database"""
        print(f"\n🗄️  Creating Postgres database: {name}...")
        
        data = {
            "name": name,
            "type": "postgres",
            "region": region
        }
        
        result = self._make_request("POST", "/v1/storage/stores", data)
        if result:
            print(f"✅ Database created successfully!")
            print(f"  Name: {result.get('name')}")
            print(f"  ID: {result.get('id')}")
            print(f"  Region: {result.get('region')}")
            return result
        
        return None
    
    def link_database_to_project(self, store_id, project_id):
        """Link database to project (automatically adds environment variables)"""
        print(f"\n🔗 Linking database to project...")
        
        data = {
            "storeId": store_id,
            "projectId": project_id
        }
        
        result = self._make_request("POST", "/v1/storage/stores/link", data)
        if result:
            print(f"✅ Database linked successfully!")
            print(f"  ✅ Environment variables automatically added to project")
            return result
        
        return None
    
    def set_environment_variables(self, project_id, variables):
        """Set additional environment variables"""
        print(f"\n⚙️  Setting environment variables...")
        
        for key, value in variables.items():
            data = {
                "key": key,
                "value": value,
                "type": "encrypted",
                "target": ["production", "preview", "development"]
            }
            
            result = self._make_request("POST", f"/v10/projects/{project_id}/env", data)
            if result:
                print(f"  ✅ {key} set successfully")
            else:
                print(f"  ❌ Failed to set {key}")
    
    def trigger_deployment(self, project_id):
        """Trigger a new deployment to apply changes"""
        print(f"\n🚀 Triggering deployment...")
        
        # Get latest deployment
        deployments = self._make_request("GET", f"/v6/deployments?projectId={project_id}&limit=1")
        if not deployments or not deployments.get('deployments'):
            print("❌ No deployments found")
            return None
        
        latest = deployments['deployments'][0]
        
        # Trigger redeploy
        data = {
            "deploymentId": latest['uid'],
            "target": "production"
        }
        
        result = self._make_request("POST", f"/v13/deployments", data)
        if result:
            print(f"✅ Deployment triggered!")
            print(f"  URL: https://vercel.com/deployments/{result.get('id')}")
            return result
        
        return None
    
    def run_full_setup(self, project_name=None):
        """Run complete automatic setup"""
        print("=" * 70)
        print("🚀 AUTOMATIC VERCEL POSTGRES DATABASE SETUP")
        print("=" * 70)
        
        # Step 1: Find project
        project = self.find_project(project_name)
        if not project:
            print("\n❌ Could not find backend project automatically.")
            print("Please specify project name with --project flag")
            return False
        
        project_id = project['id']
        project_name = project['name']
        
        # Step 2: Check existing databases
        existing_dbs = self.check_existing_databases()
        
        database = None
        if existing_dbs:
            print("\n❓ Use existing database or create new?")
            print("  1. Use existing database")
            print("  2. Create new database")
            choice = input("Enter choice (1 or 2): ").strip()
            
            if choice == "1":
                database = existing_dbs[0]
                print(f"✅ Using existing database: {database['name']}")
            else:
                database = self.create_database()
        else:
            database = self.create_database()
        
        if not database:
            print("\n❌ Database setup failed")
            return False
        
        # Step 3: Link database to project
        link_result = self.link_database_to_project(database['id'], project_id)
        if not link_result:
            print("\n❌ Failed to link database to project")
            return False
        
        # Step 4: Set additional environment variables
        import secrets
        additional_vars = {
            "SECRET_KEY": secrets.token_urlsafe(50),
            "DJANGO_SETTINGS_MODULE": "examination_system.settings_production",
            "DEBUG": "False",
            "ALLOWED_HOSTS": ".vercel.app"
        }
        
        self.set_environment_variables(project_id, additional_vars)
        
        # Step 5: Trigger deployment
        print("\n" + "=" * 70)
        print("✅ DATABASE SETUP COMPLETED!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Deployment will start automatically")
        print("  2. Database migrations will run during build")
        print("  3. Your backend will be ready in ~2-3 minutes")
        print(f"\n📊 Check status: https://{project_name}.vercel.app/")
        print(f"🗄️  Database health: https://{project_name}.vercel.app/api/database/health")
        
        # Ask if user wants to trigger deployment now
        print("\n❓ Trigger deployment now? (y/n): ", end="")
        if input().strip().lower() == 'y':
            self.trigger_deployment(project_id)
        
        return True


def main():
    parser = ArgumentParser(description="Automatic Vercel Postgres Database Setup")
    parser.add_argument("--token", required=True, help="Vercel API token")
    parser.add_argument("--project", help="Project name (optional, will auto-detect)")
    parser.add_argument("--team", help="Team ID (optional)")
    parser.add_argument("--region", default="us-east-1", help="Database region (default: us-east-1)")
    
    args = parser.parse_args()
    
    # Initialize setup
    setup = VercelDatabaseSetup(args.token, args.team)
    
    # Run full setup
    success = setup.run_full_setup(args.project)
    
    if success:
        print("\n🎉 Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
