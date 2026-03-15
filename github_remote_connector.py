#!/usr/bin/env python3
"""
GitHub Account Remote Connector
Manages remotes for all repositories in a GitHub account
Supports: cloning all repos, syncing, and mirroring operations
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
import requests
from typing import List, Dict, Optional

class GitHubRemoteConnector:
    def __init__(self, github_user: str, token: str, base_path: str = "./github_repos"):
        """
        Initialize the GitHub Remote Connector
        
        Args:
            github_user: GitHub username
            token: GitHub personal access token
            base_path: Base directory to store all repositories
        """
        self.github_user = github_user
        self.token = token
        self.base_path = Path(base_path)
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.log_file = self.base_path / "connector_log.txt"
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")
    
def get_user_repos(self) -> List[Dict]:
        """
        Fetch all repositories for the GitHub user
        
        Returns:
            List of repository dictionaries
        """
        try:
            self.log(f"Fetching repositories for user: {self.github_user}")
            repos = []
            page = 1
            per_page = 100
            
            while True:
                url = f"{self.api_base}/users/{self.github_user}/repos"
                params = {"page": page, "per_page": per_page, "type": "all"}
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                batch = response.json()
                if not batch:
                    break
                repos.extend(batch)
                page += 1
            
            self.log(f"Found {len(repos)} repositories")
            return repos
        except Exception as e:
            self.log(f"Error fetching repositories: {str(e)}", "ERROR")
            return []
    
def clone_all_repos(self, use_ssh: bool = False) -> Dict[str, str]:
        """
        Clone all repositories to local machine
        
        Args:
            use_ssh: Use SSH URLs instead of HTTPS
            
        Returns:
            Dictionary with repo names and status
        """
        repos = self.get_user_repos()
        results = {}
        
        for repo in repos:
            repo_name = repo["name"]
            clone_url = repo["ssh_url"] if use_ssh else repo["clone_url"]
            repo_path = self.base_path / repo_name
            
            try:
                if repo_path.exists():
                    self.log(f"Repository already exists: {repo_name}, updating...")
                    self._run_command(["git", "-C", str(repo_path), "fetch", "--all"], repo_name)
                    results[repo_name] = "updated"
                else:
                    self.log(f"Cloning: {repo_name}")
                    self._run_command(["git", "clone", clone_url, str(repo_path)], repo_name)
                    results[repo_name] = "cloned"
            except Exception as e:
                self.log(f"Failed to clone {repo_name}: {str(e)}", "ERROR")
                results[repo_name] = f"failed: {str(e)}"
        
        return results
    
def create_unified_remote(self, mirror_path: Optional[str] = None) -> bool:
        """
        Create a unified remote that connects all repositories
        
        Args:
            mirror_path: Path to create a mirror repository
            
        Returns:
            Success status
        """
        try:
            if mirror_path is None:
                mirror_path = self.base_path / "unified_mirror"
            
            mirror_path = Path(mirror_path)
            mirror_path.mkdir(parents=True, exist_ok=True)
            
            self.log(f"Creating unified mirror at: {mirror_path}")
            self._run_command(["git", "init", "--bare"], "unified_mirror")
            
            repos = self.get_user_repos()
            remotes_config = {}
            
            for idx, repo in enumerate(repos, 1):
                repo_name = repo["name"]
                repo_path = self.base_path / repo_name
                
                if repo_path.exists():
                    self.log(f"Adding remote {idx}/{len(repos)}: {repo_name}")
                    self._run_command(
                        ["git", "-C", str(repo_path), "remote", "add", "unified", str(mirror_path)],
                        repo_name,
                        ignore_error=True
                    )
                    remotes_config[repo_name] = str(mirror_path)
            
            # Save configuration
            config_file = self.base_path / "remotes_config.json"
            with open(config_file, "w") as f:
                json.dump(remotes_config, f, indent=2)
            
            self.log(f"Unified mirror created successfully with {len(remotes_config)} repositories")
            return True
        except Exception as e:
            self.log(f"Error creating unified remote: {str(e)}", "ERROR")
            return False
    
def sync_all_repos(self) -> Dict[str, str]:
        """
        Sync all repositories (fetch and pull)
        
        Returns:
            Dictionary with sync results
        """
        results = {}
        repos_path = [d for d in self.base_path.iterdir() if d.is_dir() and (d / ".git").exists()]
        
        for repo_path in repos_path:
            repo_name = repo_path.name
            try:
                self.log(f"Syncing: {repo_name}")
                self._run_command(["git", "-C", str(repo_path), "fetch", "--all"], repo_name)
                self._run_command(["git", "-C", str(repo_path), "pull", "--all"], repo_name, ignore_error=True)
                results[repo_name] = "synced"
            except Exception as e:
                self.log(f"Error syncing {repo_name}: {str(e)}", "ERROR")
                results[repo_name] = f"failed: {str(e)}"
        
        return results
    
def push_all_repos(self, branch: str = "main") -> Dict[str, str]:
        """
        Push all repositories to their remotes
        
        Args:
            branch: Branch to push
            
        Returns:
            Dictionary with push results
        """
        results = {}
        repos_path = [d for d in self.base_path.iterdir() if d.is_dir() and (d / ".git").exists()]
        
        for repo_path in repos_path:
            repo_name = repo_path.name
            try:
                self.log(f"Pushing: {repo_name} (branch: {branch})")
                self._run_command(
                    ["git", "-C", str(repo_path), "push", "origin", branch],
                    repo_name
                )
                results[repo_name] = "pushed"
            except Exception as e:
                self.log(f"Error pushing {repo_name}: {str(e)}", "WARNING")
                results[repo_name] = f"skipped: {str(e)}"
        
        return results
    
def list_all_repos(self) -> List[Dict]:
        """List all cloned repositories with their status"""
        repos_path = [d for d in self.base_path.iterdir() if d.is_dir() and (d / ".git").exists()]
        repo_info = []
        
        for repo_path in sorted(repos_path):
            repo_name = repo_path.name
            try:
                current_branch = subprocess.check_output(
                    ["git", "-C", str(repo_path), "rev-parse", "--abbrev-ref", "HEAD"],
                    text=True
                ).strip()
                
                remote_url = subprocess.check_output(
                    ["git", "-C", str(repo_path), "config", "--get", "remote.origin.url"],
                    text=True
                ).strip()
                
                repo_info.append({
                    "name": repo_name,
                    "path": str(repo_path),
                    "branch": current_branch,
                    "remote": remote_url
                })
            except Exception as e:
                self.log(f"Error getting info for {repo_name}: {str(e)}", "WARNING")
        
        return repo_info
    
def generate_report(self) -> str:
        """Generate a comprehensive report of all repositories"""
        report = []
        report.append("=" * 80)
        report.append("GITHUB REMOTE CONNECTOR - REPOSITORY REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"User: {self.github_user}")
        report.append("=" * 80)
        
        repos = self.list_all_repos()
        report.append(f"\nTotal Repositories: {len(repos)}\n")
        
        for idx, repo in enumerate(repos, 1):
            report.append(f"{idx}. {repo['name']}")
            report.append(f"   Path: {repo['path']}")
            report.append(f"   Branch: {repo['branch']}")
            report.append(f"   Remote: {repo['remote']}")
            report.append("")
        
        report_text = "\n".join(report)
        report_file = self.base_path / "repository_report.txt"
        with open(report_file, "w") as f:
            f.write(report_text)
        
        return report_text
    
def _run_command(self, cmd: List[str], context: str = "", ignore_error: bool = False) -> str:
        """Run a shell command and return output"""
        Args:
            cmd: Command to run
            context: Context for logging
            ignore_error: Whether to ignore errors
            
        Returns:
            Command output
        """
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            if not ignore_error:
                self.log(f"Command failed for {context}: {e.stderr}", "ERROR")
                raise
            return ""


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Remote Connector")
    parser.add_argument("--user", required=True, help="GitHub username")
    parser.add_argument("--token", required=True, help="GitHub personal access token")
    parser.add_argument("--path", default="./github_repos", help="Base path for repositories")
    parser.add_argument("--action", choices=["clone", "sync", "push", "list", "report", "mirror"],
                       default="clone", help="Action to perform")
    parser.add_argument("--ssh", action="store_true", help="Use SSH URLs for cloning")
    parser.add_argument("--branch", default="main", help="Branch for push operations")
    
    args = parser.parse_args()
    
    connector = GitHubRemoteConnector(args.user, args.token, args.path)
    
    if args.action == "clone":
        results = connector.clone_all_repos(use_ssh=args.ssh)
        print(json.dumps(results, indent=2))
    elif args.action == "sync":
        results = connector.sync_all_repos()
        print(json.dumps(results, indent=2))
    elif args.action == "push":
        results = connector.push_all_repos(args.branch)
        print(json.dumps(results, indent=2))
    elif args.action == "list":
        repos = connector.list_all_repos()
        print(json.dumps(repos, indent=2))
    elif args.action == "report":
        report = connector.generate_report()
        print(report)
    elif args.action == "mirror":
        success = connector.create_unified_remote()
        print("Mirror created successfully" if success else "Mirror creation failed")


if __name__ == "__main__":
    main()