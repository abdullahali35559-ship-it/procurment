import re

with open(r'd:\Procurement agent\ui\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check what's there
print("Has sessionFrom:", "sessionFrom" in content)
print("Has Session Summary:", "Session Summary" in content)
print("Has Recent Activity comment:", "<!-- Recent Activity" in content)
print("Has activityList:", "activityList" in content)
print("Has System Started:", "System Started" in content)

# Find line numbers of relevant sections
lines = content.split('\n')
for i, l in enumerate(lines):
    if 'Recent Activity' in l or 'activityList' in l or 'Session Summary' in l or 'sessionFrom' in l:
        print(f"Line {i+1}: {l[:100]}")
