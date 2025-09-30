"""
GitHub API interaction module for fetching repositories and README files.
"""

import base64
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GITHUB_API_BASE = "https://api.github.com"


def fetch_json(url: str, headers: dict = None) -> dict | None:
    """
    Fetch JSON data from a URL.
    
    Args:
        url: The URL to fetch from
        headers: Optional HTTP headers
    
    Returns:
        Parsed JSON data or None if error occurs
    """
    if headers is None:
        headers = {"Accept": "application/vnd.github.v3+json"}
    
    request = Request(url, headers=headers)
    try:
        with urlopen(request) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} for {url}", file=sys.stderr)
        return None
    except URLError as e:
        print(f"URL Error: {e.reason} for {url}", file=sys.stderr)
        return None


def get_repositories(org: str, repo_type: str = "public") -> list[dict]:
    """
    Get all repositories for a GitHub organization.
    
    Args:
        org: GitHub organization name
        repo_type: Repository type filter (default: "public")
    
    Returns:
        List of repository dictionaries from GitHub API
    """
    repos = []
    page = 1
    per_page = 100
    
    while True:
        url = f"{GITHUB_API_BASE}/orgs/{org}/repos?type={repo_type}&per_page={per_page}&page={page}"
        data = fetch_json(url)
        
        if not data:
            break
            
        repos.extend(data)
        
        if len(data) < per_page:
            break
            
        page += 1
    
    return repos


def get_readme_content(org: str, repo_name: str) -> tuple[bool, str, str]:
    """
    Fetch the README content for a specific repository.
    
    Args:
        org: GitHub organization name
        repo_name: Repository name
    
    Returns:
        Tuple of (success: bool, content: str, filename: str)
    """
    url = f"{GITHUB_API_BASE}/repos/{org}/{repo_name}/readme"
    data = fetch_json(url)
    
    if not data:
        return False, "", ""
    
    try:
        content = base64.b64decode(data["content"]).decode("utf-8")
        filename = data.get("name", "README.md")
        return True, content, filename
    except Exception as e:
        print(f"Error decoding README for {repo_name}: {e}", file=sys.stderr)
        return False, "", ""


def download_readme(
    org: str,
    repo_name: str,
    output_dir: Path,
    skip_existing: bool = True
) -> tuple[bool, str, str]:
    """
    Download and save the README file for a specific repository.
    
    Args:
        org: GitHub organization name
        repo_name: Repository name
        output_dir: Directory to save the README file
        skip_existing: If True, skip download if file already exists
    
    Returns:
        Tuple of (success: bool, content: str, file_path: str)
    """
    # Check if README already exists
    if skip_existing:
        existing_files = list(output_dir.glob(f"{repo_name}_*"))
        if existing_files:
            try:
                content = existing_files[0].read_text()
                return True, content, str(existing_files[0])
            except Exception as e:
                print(f"Could not read existing file: {e}", file=sys.stderr)
                return False, "", ""
    
    # Fetch README content
    success, content, filename = get_readme_content(org, repo_name)
    
    if not success:
        return False, "", ""
    
    # Save to file
    try:
        output_file = output_dir / f"{repo_name}_{filename}"
        output_file.write_text(content)
        return True, content, str(output_file)
    except Exception as e:
        print(f"Error saving README for {repo_name}: {e}", file=sys.stderr)
        return False, "", ""

