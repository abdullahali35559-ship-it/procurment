import re

with open(r'd:\Procurement agent\ui\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the old static activity content that remains after the session summary widget
# The old content appears as a SECOND recent-activity div
# Pattern: find any div with class "recent-activity" that does NOT contain sessionFrom
# Split into two sections on 'recent-activity' occurrences

# Strategy: if there are two .recent-activity divs, keep only the first one (the new one)
# Find all positions of 'recent-activity' class starts
positions = [m.start() for m in re.finditer(r'<div class="recent-activity"', content)]
print(f"Found {len(positions)} recent-activity divs at positions: {positions}")

if len(positions) >= 2:
    # Find a safe cut point: from the second div start to just before </main>
    second_start = positions[1]
    # Find the closing </main> after all this
    main_end = content.find('</main>', second_start)
    # Extract the second div content to see what it is
    print("Second div preview:", content[second_start:second_start+200])
    
    # Remove the second recent-activity div (keep everything after it)
    # Find the end of that div - it ends before </main>
    # We'll just delete from second_start to main_end (exclusive, keep </main>)
    content = content[:second_start] + content[main_end:]
    with open(r'd:\Procurement agent\ui\index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("REMOVED duplicate - saved")
else:
    print("Only one recent-activity div found - checking for activityList")
    if "activityList" in content:
        # Remove just the activityList div with old static content
        content = re.sub(r'\s*<div id="activityList">.*?</div>\s*(?=</div>)', '', content, flags=re.DOTALL)
        with open(r'd:\Procurement agent\ui\index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("REMOVED activityList - saved")
    else:
        print("Nothing to remove")
