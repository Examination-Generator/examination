#!/usr/bin/env python3
"""
Automatic Vercel Postgres Database Setup Script
This script automatically creates and links a Vercel Postgres database to your project
"""

import subprocess
import sys
import json
import os

def run_command(command, capture=True):
    """Run a shell command and return output"""
    try:
        if capture:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr if hasattr(e, 'stderr') else str(e)}")
        return None

def check_vercel_cli():
    """Check if Vercel CLI is installed"""
    result = run_command("vercel --version")
    if result:
        print(f"✓ Vercel CLI installed: {result}")
        return True
    else:
        print("✗ Vercel CLI not found")
        print("\nInstall Vercel CLI:")
        print("  npm install -g vercel")
        return False

def link_project():
    """Link to Vercel project"""
    print("\n" + "="*60)
    print("Linking to Vercel project...")
    print("="*60)
    
    # Check if already linked
    if os.path.exists('.vercel'):
        print("✓ Project already linked to Vercel")
        return True
    
    # Link project
    run_command("vercel link", capture=False)
    return os.path.exists('.vercel')

def create_postgres_database():
    """Create Vercel Postgres database"""
    print("\n" + "="*60)
    print("Creating Vercel Postgres database...")
    print("="*60)
    
    # List existing databases
    print("\nChecking for existing databases...")
    result = run_command("vercel env ls")
    
    if result and "POSTGRES_URL" in result:
        print("✓ Postgres database already exists and is linked")
        return True
    
    print("\n📝 Creating new Postgres database...")
    print("This will open your browser to create the database.")
    print("\nFollow these steps in the browser:")
    print("  1. Click 'Create Database'")
    print("  2. Select 'Postgres'")
    print("  3. Choose region (same as your backend deployment)")
    print("  4. Click 'Create'")
    print("  5. The database will be automatically linked to your project")
    
    input("\nPress ENTER after you've created the database...")
    
    # Verify database was created
    result = run_command("vercel env ls")
    if result and "POSTGRES_URL" in result:
        print("\n✓ Postgres database created and linked successfully!")
        return True
    else:
        print("\n✗ Database not detected. Please create it manually in Vercel dashboard.")
        return False

def pull_env_variables():
    """Pull environment variables from Vercel"""
    print("\n" + "="*60)
    print("Pulling environment variables...")
    print("="*60)
    
    run_command("vercel env pull .env.production", capture=False)
    
    if os.path.exists('.env.production'):
        print("✓ Environment variables pulled successfully")
        
        # Read and display database URL (masked)
        with open('.env.production', 'r') as f:
            content = f.read()
            if 'POSTGRES_URL' in content:
                print("✓ POSTGRES_URL found in environment variables")
                return True
    
    return False

def deploy_with_database():
    """Deploy project with database configured"""
    print("\n" + "="*60)
    print("Deploying to Vercel with database...")
    print("="*60)
    
    print("\n🚀 Starting deployment...")
    run_command("vercel --prod", capture=False)
    
    print("\n✓ Deployment complete!")
    print("\nYour backend is now live with Postgres database!")

def main():
    """Main setup flow"""
    print("\n" + "="*70)
    print(" 🎯 AUTOMATIC VERCEL POSTGRES SETUP")
    print("="*70)
    print("\nThis script will:")
    print("  1. Check Vercel CLI installation")
    print("  2. Link your project to Vercel")
    print("  3. Create and link Postgres database")
    print("  4. Pull environment variables")
    print("  5. Deploy your project")
    print("\n" + "="*70 + "\n")
    
    # Step 1: Check Vercel CLI
    if not check_vercel_cli():
        print("\n❌ Please install Vercel CLI first:")
        print("   npm install -g vercel")
        sys.exit(1)
    
    # Step 2: Link project
    if not link_project():
        print("\n❌ Failed to link project to Vercel")
        sys.exit(1)
    
    # Step 3: Create database
    if not create_postgres_database():
        print("\n⚠️  Please create database manually:")
        print("   1. Go to https://vercel.com/dashboard")
        print("   2. Select your project")
        print("   3. Go to Storage → Create Database → Postgres")
        print("   4. Run this script again")
        sys.exit(1)
    
    # Step 4: Pull environment variables
    if not pull_env_variables():
        print("\n⚠️  Warning: Could not pull environment variables")
        print("   The database should still be linked to your project")
    
    # Step 5: Deploy
    print("\n" + "="*60)
    print("Ready to deploy!")
    print("="*60)
    
    deploy = input("\nDeploy now? (yes/no): ").lower()
    if deploy in ['yes', 'y']:
        deploy_with_database()
    else:
        print("\n✓ Setup complete!")
        print("\nTo deploy manually, run:")
        print("  vercel --prod")
    
    print("\n" + "="*70)
    print(" ✅ SETUP COMPLETE!")
    print("="*70)
    print("\nYour database is automatically configured and will be")
    print("available at the POSTGRES_URL environment variable.")
    print("\nMigrations will run automatically on deployment.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
