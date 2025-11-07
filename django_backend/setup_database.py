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
        """Make authenticated request to Vercel API.

        Returns parsed JSON on 2xx responses.
        On non-2xx responses returns a tuple: (status_code, text).
        Returns None on network errors.
        """
        url = f"{self.base_url}{endpoint}"
        params = {}
        if self.team_id:
            params['teamId'] = self.team_id

        try:
            response = requests.request(method, url, headers=self.headers, json=data, params=params, timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed (network): {e}")
            return None

        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except ValueError:
                return response.text

        # Non-successful
        print(f"❌ API request returned status {response.status_code} for {url}")
        try:
            print(f"Response: {response.status_code} {response.text}")
        except Exception:
            pass
        return (response.status_code, response.text)
    
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
        
        # Try multiple API versions
        endpoints = ["/v1/storage/stores", "/v2/storage/stores", "/v1/integrations/stores"]
        stores_data = None
        
        for endpoint in endpoints:
            stores_data = self._make_request("GET", endpoint)
            if stores_data and 'stores' in stores_data:
                break
        
        if not stores_data:
            print("ℹ️  Could not fetch database list (API might require team access)")
            return []
        
        postgres_dbs = [s for s in stores_data.get('stores', []) if s.get('type') == 'postgres']
        
        if postgres_dbs:
            print(f"✅ Found {len(postgres_dbs)} existing Postgres database(s):")
            for db in postgres_dbs:
                print(f"  - {db.get('name')} (ID: {db.get('id')})")
        else:
            print("ℹ️  No existing Postgres databases found")
        
        return postgres_dbs
    
    def create_database(self, name="examination-db", region="us-east-1"):
        """Create a new Vercel Postgres database using available API endpoints.

        Tries multiple endpoints. If all fail, returns None and caller should offer
        an interactive fallback to paste a POSTGRES_URL.
        """
        print(f"\n🗄️  Creating Postgres database: {name}...")
        print("ℹ️  Note: Vercel Postgres creation may require specific token scopes or integrations.")
        print("ℹ️  Attempting to create via API...")

        # Try different API endpoints that may exist across accounts
        endpoints = [
            ("/v1/storage/stores", {"name": name, "type": "postgres", "region": region}),
            ("/v2/storage/stores", {"name": name, "type": "postgres", "region": region}),
            ("/v8/integrations/configuration/stores", {"name": name, "type": "postgres", "region": region}),
        ]

        for endpoint, data in endpoints:
            print(f"Trying endpoint: {endpoint}")
            result = self._make_request("POST", endpoint, data)

            if result is None:
                # network error; try next
                continue

            if isinstance(result, tuple):
                status_code, text = result
                if status_code == 404:
                    print(f"Endpoint {endpoint} returned 404 - not available for this account/token.")
                    continue
                else:
                    print(f"Endpoint {endpoint} returned {status_code}: {text}")
                    # stop trying on other errors
                    return None

            # If result is dict, assume success
            if isinstance(result, dict) and result.get('id'):
                print(f"✅ Database created successfully via {endpoint}!")
                print(f"  Name: {result.get('name')}")
                print(f"  ID: {result.get('id')}")
                print(f"  Region: {result.get('region')}")
                return result

        # If we reach here, automatic creation failed
        print("\n⚠️  API creation failed for all attempted endpoints.")
        print("This likely means the Vercel token lacks Storage/Integrations scope or your account uses a different API surface.")
        print("You can either grant the token additional permissions or create the Postgres database via the Vercel Dashboard:")
        print("  - https://vercel.com/dashboard/stores")
        print("After creating the database in the dashboard, re-run this script to link it to the project, or paste the resulting POSTGRES_URL when prompted.")

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
            if result is None:
                print(f"  ❌ Network error when setting {key}")
            elif isinstance(result, tuple):
                status_code, text = result
                print(f"  ❌ Failed to set {key}: {status_code} - {text}")
            else:
                print(f"  ✅ {key} set successfully")
    
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
            print("\n⚠️  Database setup failed (automatic creation).")
            print("You can provide an existing POSTGRES_URL to continue (from Vercel Dashboard or another provider).")
            provided = input("Paste POSTGRES_URL now (or press Enter to abort): ").strip()
            if not provided:
                print("Aborting setup.")
                return False

            # Set POSTGRES_URL directly on project
            print("Setting POSTGRES_URL on project...")
            self.set_environment_variables(project_id, {"POSTGRES_URL": provided})
            print("✅ POSTGRES_URL configured. Continuing to set other env vars and trigger deployment.")
            database = {'id': 'manual-provided', 'name': 'manual-provided'}
        
        # Step 3: Link database to project
        link_result = self.link_database_to_project(database['id'], project_id)
        if not link_result:
            print("\n⚠️  Failed to link database to project automatically.")
            print("You can paste a POSTGRES_URL to set it manually and continue.")
            provided = input("Paste POSTGRES_URL now (or press Enter to abort): ").strip()
            if not provided:
                print("Aborting setup.")
                return False
            self.set_environment_variables(project_id, {"POSTGRES_URL": provided})
        
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
