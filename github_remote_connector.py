#!/usr/bin/env python3
"""
GitHub Account Remote Connector
Manages remotes for all repositories in a GitHub account.
Supports cloning, syncing, mirroring, listing, and reporting operations.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class GitHubRemoteConnector:
    def __init__(
        self,
        github_user: str,
        token: Optional[str] = None,
        base_path: str = "./github_repos",
    ) -> None:
        """
        Initialize the GitHub Remote Connector.

        Args:
            github_user: GitHub username
            token: Optional GitHub personal access token
            base_path: Base directory to store all repositories
        """
        self.github_user = github_user
        self.token = token
        self.base_path = Path(base_path)
        self.api_base = "https://api.github.com"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.log_file = self.base_path / "connector_log.txt"

        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self.headers["Authorization"] = f"token {token}"

    def log(self, message: str, level: str = "INFO") -> None:
        """Log messages to file and console."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        with self.log_file.open("a", encoding="utf-8") as file_handle:
            file_handle.write(log_message + "\n")

    def get_user_repos(self) -> List[Dict]:
        """
        Fetch all repositories for the GitHub user.

        Returns:
            List of repository dictionaries
        """
        try:
            self.log(f"Fetching repositories for user: {self.github_user}")
            repos: List[Dict] = []
            page = 1
            per_page = 100

            while True:
                url = f"{self.api_base}/users/{self.github_user}/repos"
                params = {"page": page, "per_page": per_page, "type": "all"}
                query = urlencode(params)
                request = Request(f"{url}?{query}", headers=self.headers)
                with urlopen(request, timeout=30) as response:
                    batch = json.load(response)
                if not batch:
                    break

                repos.extend(batch)
                page += 1

            self.log(f"Found {len(repos)} repositories")
            return repos
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            self.log(f"Error fetching repositories: {exc}", "ERROR")
            return []

    def clone_all_repos(self, use_ssh: bool = False) -> Dict[str, str]:
        """
        Clone all repositories to local machine.

        Args:
            use_ssh: Use SSH URLs instead of HTTPS

        Returns:
            Dictionary with repo names and status
        """
        repos = self.get_user_repos()
        results: Dict[str, str] = {}

        for repo in repos:
            repo_name = repo["name"]
            clone_url = repo["ssh_url"] if use_ssh else repo["clone_url"]
            repo_path = self.base_path / repo_name

            try:
                if repo_path.exists():
                    self.log(f"Repository already exists: {repo_name}, updating...")
                    self._run_command(
                        ["git", "-C", str(repo_path), "fetch", "--all"],
                        repo_name,
                    )
                    results[repo_name] = "updated"
                else:
                    self.log(f"Cloning: {repo_name}")
                    self._run_command(["git", "clone", clone_url, str(repo_path)], repo_name)
                    results[repo_name] = "cloned"
            except Exception as exc:
                self.log(f"Failed to clone {repo_name}: {exc}", "ERROR")
                results[repo_name] = f"failed: {exc}"

        return results

    def create_unified_remote(self, mirror_path: Optional[str] = None) -> bool:
        """
        Create a unified remote that connects all repositories.

        Args:
            mirror_path: Path to create a mirror repository

        Returns:
            Success status
        """
        try:
            resolved_mirror_path = Path(mirror_path) if mirror_path else self.base_path / "unified_mirror.git"
            if not resolved_mirror_path.exists():
                resolved_mirror_path.parent.mkdir(parents=True, exist_ok=True)
                self.log(f"Creating unified mirror at: {resolved_mirror_path}")
                self._run_command(
                    ["git", "init", "--bare", str(resolved_mirror_path)],
                    "unified_mirror",
                )
            else:
                self.log(f"Unified mirror already exists: {resolved_mirror_path}")

            repos = self.get_user_repos()
            remotes_config: Dict[str, str] = {}

            for idx, repo in enumerate(repos, start=1):
                repo_name = repo["name"]
                repo_path = self.base_path / repo_name

                if repo_path.exists() and (repo_path / ".git").exists():
                    self.log(f"Adding remote {idx}/{len(repos)}: {repo_name}")
                    self._run_command(
                        [
                            "git",
                            "-C",
                            str(repo_path),
                            "remote",
                            "remove",
                            "unified",
                        ],
                        repo_name,
                        ignore_error=True,
                    )
                    self._run_command(
                        [
                            "git",
                            "-C",
                            str(repo_path),
                            "remote",
                            "add",
                            "unified",
                            str(resolved_mirror_path),
                        ],
                        repo_name,
                    )
                    remotes_config[repo_name] = str(resolved_mirror_path)

            config_file = self.base_path / "remotes_config.json"
            with config_file.open("w", encoding="utf-8") as file_handle:
                json.dump(remotes_config, file_handle, indent=2)

            self.log(
                f"Unified mirror created successfully with {len(remotes_config)} repositories"
            )
            return True
        except Exception as exc:
            self.log(f"Error creating unified remote: {exc}", "ERROR")
            return False

    def sync_all_repos(self) -> Dict[str, str]:
        """
        Sync all repositories (fetch and pull).

        Returns:
            Dictionary with sync results
        """
        results: Dict[str, str] = {}
        repos_path = self._local_git_repos()

        for repo_path in repos_path:
            repo_name = repo_path.name
            try:
                self.log(f"Syncing: {repo_name}")
                self._run_command(["git", "-C", str(repo_path), "fetch", "--all"], repo_name)
                self._run_command(
                    ["git", "-C", str(repo_path), "pull", "--all"],
                    repo_name,
                    ignore_error=True,
                )
                results[repo_name] = "synced"
            except Exception as exc:
                self.log(f"Error syncing {repo_name}: {exc}", "ERROR")
                results[repo_name] = f"failed: {exc}"

        return results

    def push_all_repos(self, branch: str = "main") -> Dict[str, str]:
        """
        Push all repositories to their remotes.

        Args:
            branch: Branch to push

        Returns:
            Dictionary with push results
        """
        results: Dict[str, str] = {}

        for repo_path in self._local_git_repos():
            repo_name = repo_path.name
            try:
                self.log(f"Pushing: {repo_name} (branch: {branch})")
                self._run_command(
                    ["git", "-C", str(repo_path), "push", "origin", branch],
                    repo_name,
                )
                results[repo_name] = "pushed"
            except Exception as exc:
                self.log(f"Error pushing {repo_name}: {exc}", "WARNING")
                results[repo_name] = f"skipped: {exc}"

        return results

    def list_all_repos(self) -> List[Dict]:
        """List all cloned repositories with their status."""
        repo_info: List[Dict] = []

        for repo_path in self._local_git_repos():
            repo_name = repo_path.name
            try:
                current_branch = subprocess.check_output(
                    ["git", "-C", str(repo_path), "rev-parse", "--abbrev-ref", "HEAD"],
                    text=True,
                ).strip()

                remote_url = subprocess.check_output(
                    ["git", "-C", str(repo_path), "config", "--get", "remote.origin.url"],
                    text=True,
                ).strip()

                repo_info.append(
                    {
                        "name": repo_name,
                        "path": str(repo_path),
                        "branch": current_branch,
                        "remote": remote_url,
                    }
                )
            except Exception as exc:
                self.log(f"Error getting info for {repo_name}: {exc}", "WARNING")

        return repo_info

    def generate_report(self) -> str:
        """Generate a comprehensive report of all repositories."""
        report = [
            "=" * 80,
            "GITHUB REMOTE CONNECTOR - REPOSITORY REPORT",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"User: {self.github_user}",
            "=" * 80,
        ]

        repos = self.list_all_repos()
        report.append(f"\nTotal Repositories: {len(repos)}\n")

        for idx, repo in enumerate(repos, start=1):
            report.append(f"{idx}. {repo['name']}")
            report.append(f"   Path: {repo['path']}")
            report.append(f"   Branch: {repo['branch']}")
            report.append(f"   Remote: {repo['remote']}")
            report.append("")

        report_text = "\n".join(report)
        report_file = self.base_path / "repository_report.txt"
        with report_file.open("w", encoding="utf-8") as file_handle:
            file_handle.write(report_text)

        return report_text

    def _local_git_repos(self) -> List[Path]:
        """Return local git repositories in the base path."""
        return sorted(
            path
            for path in self.base_path.iterdir()
            if path.is_dir() and (path / ".git").exists()
        )

    def _run_command(
        self,
        cmd: List[str],
        context: str = "",
        ignore_error: bool = False,
    ) -> str:
        """
        Run a shell command and return output.

        Args:
            cmd: Command to run
            context: Context for logging
            ignore_error: Whether to ignore errors

        Returns:
            Command output
        """
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip()
            if not ignore_error:
                self.log(f"Command failed for {context}: {stderr}", "ERROR")
                raise RuntimeError(stderr) from exc
            return ""


def main() -> None:
    """Main execution function."""
    parser = argparse.ArgumentParser(description="GitHub Remote Connector")
    parser.add_argument("--user", required=True, help="GitHub username")
    parser.add_argument("--token", help="GitHub personal access token")
    parser.add_argument("--path", default="./github_repos", help="Base path for repositories")
    parser.add_argument(
        "--action",
        choices=["clone", "sync", "push", "list", "report", "mirror"],
        default="clone",
        help="Action to perform",
    )
    parser.add_argument("--ssh", action="store_true", help="Use SSH URLs for cloning")
    parser.add_argument("--branch", default="main", help="Branch for push operations")
    parser.add_argument("--mirror-path", help="Optional explicit mirror path")

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
        success = connector.create_unified_remote(args.mirror_path)
        print("Mirror created successfully" if success else "Mirror creation failed")


if __name__ == "__main__":
    main()
