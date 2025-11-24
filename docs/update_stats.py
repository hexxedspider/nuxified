import re
import os

def get_version_from_nuxified():
    nuxified_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nuxified.py')
    
    with open(nuxified_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    version_match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if version_match:
        return version_match.group(1)
    return "Unknown"

def count_commands_from_nuxified():
    nuxified_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nuxified.py')
    
    with open(nuxified_path, 'r', encoding='utf-8') as f:
        content = f.read()

    command_pattern = r'"(?:nux|all)\s+[^"]+"\s*:\s*self\.cmd_'
    commands = re.findall(command_pattern, content)
    
    return len(commands)

def update_html_with_stats(version, command_count):
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_content = re.sub(
        r'<div class="stat-number">\d+\+</div>\s*<div class="stat-label">Commands</div>',
        f'<div class="stat-number">{command_count}+</div>\n                        <div class="stat-label">Commands</div>',
        html_content
    )
    
    version_short = '.'.join(version.split('.')[:3])
    html_content = re.sub(
        r'<div class="stat-number">v[\d.]+</div>\s*<div class="stat-label">Latest Version</div>',
        f'<div class="stat-number">v{version_short}</div>\n                        <div class="stat-label">Latest Version</div>',
        html_content
    )
    
    html_content = re.sub(
        r'Over \d+ commands organized',
        f'Over {command_count} commands organized',
        html_content
    )
    
    html_content = re.sub(
        r'Advanced Discord Selfbot v[\d.]+',
        f'Advanced Discord Selfbot v{version_short}',
        html_content
    )
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[OK] Updated HTML with version {version_short} and {command_count} commands")

def main():
    print("Updating website statistics...")
    
    version = get_version_from_nuxified()
    command_count = count_commands_from_nuxified()
    
    print(f"Found version: {version}")
    print(f"Found {command_count} commands")
    
    update_html_with_stats(version, command_count)
    print("\n[SUCCESS] Website updated successfully!")

if __name__ == "__main__":
    main()
