import os
import json
import importlib.metadata
import re
import tomllib
from packaging.requirements import Requirement


def _get_manual_licenses():
    """Load manually defined dependencies from JSON file."""
    manual_path = os.path.join(os.getcwd(), 'src', 'data', 'manual_dependencies.json')
    if not os.path.exists(manual_path):
        return []
    with open(manual_path, "r") as f:
        return json.load(f)


def _get_js_direct_dependencies():
    """Get the set of direct JS/CSS dependencies from package.json."""
    package_json_path = os.path.join(os.getcwd(), 'package.json')
    if not os.path.exists(package_json_path):
        return set()
    
    js_direct_dependencies = set()
    with open(package_json_path, "r") as f:
        pj = json.load(f)
        js_direct_dependencies.update(pj.get('dependencies', {}).keys())
        js_direct_dependencies.update(pj.get('devDependencies', {}).keys())

    return js_direct_dependencies


def _get_py_direct_dependencies():
    """Get the set of direct Python dependencies from pyproject.toml."""
    pyproject_toml_path = os.path.join(os.getcwd(), 'pyproject.toml')
    if not os.path.exists(pyproject_toml_path):
        return set()

    py_direct_dependencies = set()
    with open(pyproject_toml_path, "rb") as f:
        py_toml = tomllib.load(f)
        deps = py_toml.get('project', {}).get('dependencies', [])
        for dep in deps:
            name = Requirement(dep).name
            py_direct_dependencies.add(name.lower().replace('_', '-'))

    return py_direct_dependencies


def _get_js_licenses(js_direct_dependencies, seen):
    """Load JS/CSS dependencies from package-lock.json or package.json."""
    js_licenses = []
    package_lock_path = os.path.join(os.getcwd(), 'package-lock.json')

    if os.path.exists(package_lock_path):
        with open(package_lock_path, "r") as f:
            pl = json.load(f)
            packages = pl.get('packages', {})
            for pkg_path, pkg_info in packages.items():
                # Only include packages in node_modules, and ignore the root package (empty string)
                if not pkg_path.startswith('node_modules/') or pkg_info.get('peer'):
                    continue

                name = pkg_path.replace('node_modules/', '')
                
                # Only include direct dependencies if we have the list
                if js_direct_dependencies and name not in js_direct_dependencies:
                    continue
                    
                version = pkg_info.get('version', 'Unknown')

                # Avoid duplicates/allow overrides
                js_key = (name.lower(), version)
                if js_key in seen:
                    continue
                
                seen.add(js_key)
                
                license_name = pkg_info.get('license', 'Unknown')
                
                # Handle multiple licenses or complex license expressions
                if isinstance(license_name, list):
                    license_name = " AND ".join(license_name)
                
                # Try to get a URL from the package info
                url = ""
                license_url = ""
                
                # Try to get more info from the package's own package.json if available
                pkg_json_path = os.path.join(os.getcwd(), pkg_path, 'package.json')
                if os.path.exists(pkg_json_path):
                    with open(pkg_json_path, "r") as fj:
                        pj_info = json.load(fj)
                        # Get repository URL
                        repo = pj_info.get('repository')
                        if isinstance(repo, dict):
                            url = repo.get('url', '')
                        elif isinstance(repo, str):
                            url = repo
                        
                        if url:
                            # Clean up git URLs
                            url = url.replace('git+', '').replace('git://', 'https://').replace('.git', '')
                            if 'github.com' in url and not url.startswith('http'):
                                url = 'https://' + url.replace('github.com:', 'github.com/')
                        
                        # Fallback to homepage
                        if not url:
                            url = pj_info.get('homepage', '')
                        
                        # Heuristic for license URL
                        if url and 'github.com' in url:
                            # Standard GitHub license locations
                            license_name_lower = name.lower()
                            license_file = "LICENSE"
                            if 'fontawesome' in license_name_lower:
                                license_file = "LICENSE.txt"
                            
                            license_url = f"{url.rstrip('/')}/blob/main/{license_file}"

                # Common source for URL in package-lock.json is resolved, 
                # but it's the tarball URL. 
                if not url:
                    resolved = pkg_info.get('resolved', '')
                    if 'github.com' in resolved:
                        # Heuristic for GitHub URL from resolved
                        pass

                # If not available, we'll use npm as default
                if not url:
                    url = f"https://www.npmjs.com/package/{name}"

                js_licenses.append({
                    "name": name,
                    "version": version,
                    "license": license_name,
                    "license_url": license_url,
                    "url": url,
                    "type": "JS/CSS",
                    "display_name": name,
                })
    elif os.path.exists(os.path.join(os.getcwd(), 'package.json')):
        # Fallback to package.json if lockfile is missing
        with open(os.path.join(os.getcwd(), 'package.json'), "r") as f:
            pj = json.load(f)
            deps = pj.get('dependencies', {})
            for name, version in deps.items():
                js_licenses.append({
                    "name": name,
                    "version": version.lstrip('^~'),
                    "license": "Unknown",
                    "license_url": "",
                    "url": f"https://www.npmjs.com/package/{name}",
                    "type": "JS/CSS",
                    "display_name": name,
                })
    return js_licenses


def _get_python_licenses(py_direct_dependencies, seen):
    """Load and parse Python packages using importlib.metadata."""
    python_licenses = []
    # Get all installed distributions
    for dist in importlib.metadata.distributions():
        metadata = dist.metadata
        name = metadata.get('Name')
        version = dist.version
        license_name = metadata.get('License') or metadata.get('License-Expression') or "Unknown"
        project_urls = metadata.get_all('Project-URL', [])
        home_page = metadata.get('Home-page', "")
        
        if not name or not version:
            continue

        # Avoid duplicates
        py_key = (name.lower(), version)
        if py_key in seen:
            continue
        
        # Only include direct dependencies if we have the list
        if py_direct_dependencies and name.lower().replace('_', '-') not in py_direct_dependencies:
            continue

        seen.add(py_key)

        display_name = name
        
        license_url = ""
        url = ""
        
        # Extract Project-URLs for website and license
        if project_urls:
            links = {}
            for project_url in project_urls:
                # Split at first comma or colon.
                parts = re.split(r'[,:]', project_url, maxsplit=1)
                if len(parts) == 2:
                    links[parts[0].strip().lower()] = parts[1].strip()

            # Find website URL
            for priority_label in ['source', 'repository', 'homepage', 'home-page', 'documentation']:
                if priority_label in links:
                    url = links[priority_label]
                    break
            if not url and links:
                url = list(links.values())[0]

            # Find license URL
            for label, link in links.items():
                if 'license' in label:
                    license_url = link
                    break

        # Fallback for homepage if not in Project-URL
        if not url:
            url = home_page

        # Fallback for GitHub license URL
        if not license_url and url and 'github.com' in url:
            base_url = url.rstrip('/')
            if '/tree/' not in base_url and '/blob/' not in base_url:
                license_url = f"{base_url}/blob/main/LICENSE"

        # Last resort: PyPI URL
        if not url:
            url = f"https://pypi.org/project/{name}/"

        python_licenses.append({
            "name": name,
            "version": version,
            "license": license_name,
            "license_url": license_url,
            "url": url,
            "type": "Python",
            "display_name": display_name,
        })
    return python_licenses


def get_licenses_data():
    """Aggregate license data from manual, JS/CSS, and Python dependencies."""
    # 1. Load manual dependencies
    manual_licenses = _get_manual_licenses()
    
    # Track seen packages to avoid duplicates with manual entries
    # manual entries can override both js and py dependencies
    seen = {(item['name'].lower(), item.get('version')) for item in manual_licenses}
    
    # 2. Load JS/CSS dependencies
    js_direct_dependencies = _get_js_direct_dependencies()
    js_licenses = _get_js_licenses(js_direct_dependencies, seen)
    
    # 3. Load Python dependencies
    py_direct_dependencies = _get_py_direct_dependencies()
    python_licenses = _get_python_licenses(py_direct_dependencies, seen)

    # Union all together
    all_licenses = manual_licenses + js_licenses + python_licenses
    
    return sorted(all_licenses, key=lambda x: (x['type'], x['name'].lower()))
