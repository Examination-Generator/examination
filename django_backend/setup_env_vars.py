#!/usr/bin/env python3
"""
Simplified script to set Vercel environment variables
This script helps you set up all required environment variables automatically

Usage:
    python setup_env_vars.py --token YOUR_VERCEL_TOKEN --postgres-url "YOUR_POSTGRES_URL"
"""

import sys
import json
import requests
import secrets
from argparse import ArgumentParser


class VercelEnvSetup:
    """Set up Vercel environment variables"""
    
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
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None
    
    def find_project(self, project_name=None):
        """Find the backend project"""
        print("\n🔍 Finding backend project...")
        
        projects = self._make_request("GET", "/v9/projects")
        if not projects:
            return None
        
        for project in projects.get('projects', []):
            name_lower = project['name'].lower()
            if project_name and project_name.lower() in name_lower:
                print(f"✅ Found project: {project['name']} (ID: {project['id']})")
                return project
            elif any(keyword in name_lower for keyword in ['examination', 'backend', 'django', 's3np']):
                print(f"✅ Found project: {project['name']} (ID: {project['id']})")
                return project
        
        print("\n📋 Available projects:")
        for i, project in enumerate(projects.get('projects', []), 1):
            print(f"  {i}. {project['name']} (ID: {project['id']})")
        
        return None
    
    def get_env_variables(self, project_id):
        """Get existing environment variables"""
        print("\n🔍 Checking existing environment variables...")
        
        result = self._make_request("GET", f"/v9/projects/{project_id}/env")
        if result and 'envs' in result:
            return result['envs']
        return []
    
    def delete_env_variable(self, project_id, env_id):
        """Delete an environment variable"""
        result = self._make_request("DELETE", f"/v9/projects/{project_id}/env/{env_id}")
        return result is not None
    
    def set_env_variable(self, project_id, key, value, target=None):
        """Set an environment variable"""
        if target is None:
            target = ["production", "preview", "development"]
        
        data = {
            "key": key,
            "value": value,
            "type": "encrypted",
            "target": target
        }
        
        result = self._make_request("POST", f"/v10/projects/{project_id}/env", data)
        return result is not None
    
    def setup_all_variables(self, project_id, postgres_url=None):
        """Set up all required environment variables"""
        print("\n" + "=" * 70)
        print("⚙️  SETTING UP ENVIRONMENT VARIABLES")
        print("=" * 70)
        
        # Get existing variables
        existing_vars = self.get_env_variables(project_id)
        existing_keys = {var['key']: var for var in existing_vars}
        
        # Define required variables
        variables = {
            "DJANGO_SETTINGS_MODULE": "examination_system.settings_production",
            "DEBUG": "False",
            "ALLOWED_HOSTS": ".vercel.app",
        }
        
        # Generate SECRET_KEY if not exists
        if "SECRET_KEY" not in existing_keys:
            variables["SECRET_KEY"] = secrets.token_urlsafe(50)
        else:
            print(f"  ℹ️  SECRET_KEY already exists, skipping")
        
        # Add POSTGRES_URL if provided
        if postgres_url:
            # Check if POSTGRES_URL already exists
            if "POSTGRES_URL" in existing_keys:
                print(f"  ⚠️  POSTGRES_URL already exists")
                choice = input("  Replace it? (y/n): ").strip().lower()
                if choice == 'y':
                    # Delete old one
                    print(f"  🗑️  Deleting old POSTGRES_URL...")
                    self.delete_env_variable(project_id, existing_keys["POSTGRES_URL"]['id'])
                    variables["POSTGRES_URL"] = postgres_url
            else:
                variables["POSTGRES_URL"] = postgres_url
        elif "POSTGRES_URL" not in existing_keys:
            print("\n⚠️  WARNING: POSTGRES_URL not provided and doesn't exist!")
            print("  You need to create a Vercel Postgres database first.")
            print("  Go to: https://vercel.com/dashboard/stores")
            print("  After creating, it will be automatically added to your project.")
        
        # Set each variable
        print()
        for key, value in variables.items():
            # Skip if already exists (except for ones we're replacing)
            if key in existing_keys and key not in ["POSTGRES_URL"]:
                print(f"  ℹ️  {key} already exists, skipping")
                continue
            
            print(f"  Setting {key}...", end=" ")
            if self.set_env_variable(project_id, key, value):
                print("✅")
            else:
                print("❌")
        
        print("\n" + "=" * 70)
        print("✅ ENVIRONMENT VARIABLES CONFIGURED!")
        print("=" * 70)
        
        return True


def main():
    parser = ArgumentParser(description="Set up Vercel environment variables")
    parser.add_argument("--token", required=True, help="Vercel API token")
    parser.add_argument("--project", help="Project name (optional, will auto-detect)")
    parser.add_argument("--postgres-url", help="Postgres connection URL (optional)")
    parser.add_argument("--team", help="Team ID (optional)")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🚀 VERCEL ENVIRONMENT VARIABLES SETUP")
    print("=" * 70)
    
    # Initialize setup
    setup = VercelEnvSetup(args.token, args.team)
    
    # Find project
    project = setup.find_project(args.project)
    if not project:
        print("\n❌ Could not find backend project")
        print("Please specify project name with --project flag")
        sys.exit(1)
    
    # Set up variables
    success = setup.setup_all_variables(project['id'], args.postgres_url)
    
    if success:
        print("\n✅ Setup completed!")
        print("\n📋 Next steps:")
        
        if not args.postgres_url:
            print("\n1. Create Vercel Postgres database:")
            print("   - Go to: https://vercel.com/dashboard/stores")
            print("   - Click 'Create Database' → 'Postgres'")
            print("   - Name: examination-db")
            print("   - Click 'Create'")
            print("\n2. Connect database to your project:")
            print(f"   - In database settings, click 'Connect Project'")
            print(f"   - Select: {project['name']}")
            print("   - This automatically adds POSTGRES_URL ✅")
        
        print("\n3. Trigger deployment:")
        print(f"   - Go to: https://vercel.com/{project['name']}")
        print("   - Click 'Redeploy' on latest deployment")
        print("   OR")
        print("   - Push new code: git push origin main")
        
        print(f"\n4. Verify setup:")
        print(f"   - Visit: https://{project['name']}.vercel.app/")
        print(f"   - Should show: 'connection': 'connected'")
        
        sys.exit(0)
    else:
        print("\n❌ Setup failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
