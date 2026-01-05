import os
import re

def fix_blog_images(directory, dry_run=True):
    # Regex to match raw R2 URLs on their own line
    # Matches: https://pub-141831e61e69445289222976a15b6fb3.r2.dev/insta_post/.../image_X.webp
    url_pattern = re.compile(r'^(https://pub-141831e61e69445289222976a15b6fb3\.r2\.dev/insta_post/[^/]+/image_\d+\.webp)$')

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                new_lines = []
                modified = False
                in_frontmatter = False
                
                for i, line in enumerate(lines):
                    stripped_line = line.strip()
                    
                    # Track frontmatter to avoid modifying heroImage
                    if i == 0 and stripped_line == '---':
                        in_frontmatter = True
                        new_lines.append(line)
                        continue
                    if in_frontmatter and stripped_line == '---':
                        in_frontmatter = False
                        new_lines.append(line)
                        continue
                    
                    if not in_frontmatter:
                        match = url_pattern.match(stripped_line)
                        if match:
                            url = match.group(1)
                            # Convert to markdown image syntax
                            new_line = f'![Image]({url})\n'
                            new_lines.append(new_line)
                            modified = True
                            if dry_run:
                                print(f"[DRY RUN] {file}: {stripped_line} -> {new_line.strip()}")
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)

                if modified and not dry_run:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    print(f"[FIXED] {file}")

if __name__ == "__main__":
    blog_dir = "/Users/bipulkumar/Documents/FreePrompt_Base/src/content/blog"
    # Run for real:
    fix_blog_images(blog_dir, dry_run=False)
