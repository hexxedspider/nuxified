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

def count_commands_by_category():
    curses_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'curses')
    category_counts = {
        "Text Tools": 0,
        "Media": 0,
        "Utilities": 0,
        "Fun": 0,
        "Total": 0
    }
    
    file_mapping = {
        "text_tools.py": "Text Tools",
        "media.py": "Media",
        "utilities.py": "Utilities",
        "fun.py": "Fun"
    }
    
    if os.path.exists(curses_path):
        for filename in os.listdir(curses_path):
            if filename.endswith('.py') and filename != '__init__.py':
                file_path = os.path.join(curses_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    command_pattern = r'def cmd_\w+'
                    commands = re.findall(command_pattern, content)
                    count = len(commands)
                    
                    category_counts["Total"] += count
                    
                    if filename in file_mapping:
                        category_counts[file_mapping[filename]] = count
                        
    return category_counts

def update_html_with_stats(version, counts):
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_content = re.sub(
        r'<div class="stat-number">\d+\+</div>\s*<div class="stat-label">Commands</div>',
        f'<div class="stat-number">{counts["Total"]}+</div>\n                        <div class="stat-label">Commands</div>',
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
        f'Over {counts["Total"]} commands organized',
        html_content
    )
    
    html_content = re.sub(
        r'Advanced Discord Selfbot v[\d.]+',
        f'Advanced Discord Selfbot v{version_short}',
        html_content
    )

    for category, count in counts.items():
        if category == "Total": continue
        
        pattern = f'<h3>{category}</h3>\\s*<span class="category-count">\\d+\\+ commands</span>'
        replacement = f'<h3>{category}</h3>\n                        <span class="category-count">{count}+ commands</span>'
        
        html_content = re.sub(pattern, replacement, html_content)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[OK] Updated HTML with version {version_short}")
    for cat, count in counts.items():
        print(f"  - {cat}: {count}")

def main():
    print("Updating website statistics...")
    
    version = get_version_from_nuxified()
    counts = count_commands_by_category()
    
    print(f"Found version: {version}")
    
    update_html_with_stats(version, counts)
    print("\n[SUCCESS] Website updated successfully!")

if __name__ == "__main__":
    main()
