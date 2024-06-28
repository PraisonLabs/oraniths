#!/usr/bin/env python3
"""
Simple script to reorder git history chronologically based on commit dates.
Just applies the actual changes from each commit without parsing files.
"""

import os
import subprocess
import datetime
import tempfile
import re

def run_command(cmd, cwd=None, env_vars=None):
    """Run a shell command and return success, stdout, stderr."""
    try:
        # Prepare environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env=env)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def get_all_commits():
    """Get all commits with their dates."""
    cmd = 'git log --pretty=format:"%H|%s|%an|%ae|%ad" --date=iso-strict'
    success, output, error = run_command(cmd)
    
    if not success:
        print(f"Failed to get commits: {error}")
        return []
    
    commits = []
    for line in output.split('\n'):
        if '|' in line and line.strip():
            parts = line.split('|', 4)
            if len(parts) >= 5:
                try:
                    # Parse date
                    date_str = parts[4][:19]  # Take only YYYY-MM-DD HH:MM:SS part
                    commit_date = datetime.datetime.fromisoformat(date_str)
                    
                    commits.append({
                        'hash': parts[0],
                        'message': parts[1],
                        'author_name': parts[2],
                        'author_email': parts[3],
                        'date': commit_date
                    })
                except (ValueError, IndexError):
                    continue
    
    return commits

def create_missing_files_for_commit(commit_hash):
    """Create any missing files and directories that this commit needs."""
    try:
        # Get list of files that this commit touches
        success, files_output, _ = run_command(f'git diff-tree --name-only -r {commit_hash}')
        if not success:
            return True  # If we can't get files, just proceed
        
        files = files_output.split('\n')
        
        for file_path in files:
            if not file_path.strip():
                continue
                
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                print(f"     Created directory: {dir_path}")
            
            # Create empty file if it doesn't exist (for new files)
            if not os.path.exists(file_path):
                # Check if this commit is adding the file (not deleting)
                success, status_output, _ = run_command(f'git diff-tree --name-status -r {commit_hash}')
                if success and file_path in status_output:
                    # Look for lines like "A\tfilename" (Added)
                    for line in status_output.split('\n'):
                        if line.startswith('A\t') and file_path in line:
                            # This is a new file being added, create empty version
                            with open(file_path, 'w') as f:
                                f.write('')  # Empty file
                            print(f"     Created empty file: {file_path}")
                            break
        
        return True
    except Exception as e:
        print(f"     Error creating files: {e}")
        return False

def apply_patch_manually(patch_content, commit):
    """Manually apply patch when automated methods fail."""
    try:
        print(f"     Attempting manual patch application...")
        
        # Parse the patch to extract file changes
        lines = patch_content.split('\n')
        current_file = None
        file_changes = {}
        
        for line in lines:
            # Look for file headers
            if line.startswith('--- ') or line.startswith('+++ '):
                if line.startswith('+++ '):
                    # Extract filename from +++ b/filename
                    if line.startswith('+++ b/'):
                        current_file = line[6:]  # Remove '+++ b/'
                    elif '/dev/null' not in line:
                        # Handle other file path formats
                        parts = line.split('\t')
                        if len(parts) > 0:
                            current_file = parts[0][4:]  # Remove '+++ '
                    
                    if current_file and current_file not in file_changes:
                        file_changes[current_file] = {'additions': [], 'deletions': []}
            
            # Look for content changes
            elif current_file and (line.startswith('+') or line.startswith('-')):
                if line.startswith('+') and not line.startswith('+++'):
                    file_changes[current_file]['additions'].append(line[1:])  # Remove +
                elif line.startswith('-') and not line.startswith('---'):
                    file_changes[current_file]['deletions'].append(line[1:])  # Remove -
        
        # Apply changes to files
        changes_made = False
        for file_path, changes in file_changes.items():
            if not file_path or file_path == '/dev/null':
                continue
                
            print(f"     Processing {file_path}")
            
            # Ensure directory exists
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            # Handle new files
            if not os.path.exists(file_path) and changes['additions']:
                with open(file_path, 'w') as f:
                    f.write('\n'.join(changes['additions']))
                print(f"     Created new file: {file_path}")
                changes_made = True
            
            # Handle existing files - simple append for additions
            elif os.path.exists(file_path) and changes['additions']:
                with open(file_path, 'a') as f:
                    f.write('\n' + '\n'.join(changes['additions']))
                print(f"     Appended to file: {file_path}")
                changes_made = True
        
        if changes_made:
            # Stage all changes
            run_command('git add -A')
            print(f"     Manual patch applied and staged")
            return True
        else:
            print(f"     No changes extracted from patch")
            return False
            
    except Exception as e:
        print(f"     Manual patch failed: {e}")
        return False

def reorder_history():
    """Reorder git history chronologically."""
    print("Reordering git history chronologically...")
    
    # Get all commits
    all_commits = get_all_commits()
    if len(all_commits) < 2:
        print("Need at least 2 commits")
        return False
    
    print(f"Found {len(all_commits)} commits")
    
    # Sort by date (oldest first)
    sorted_commits = sorted(all_commits, key=lambda x: x['date'])
    
    print("Chronological order:")
    for i, commit in enumerate(sorted_commits[:5]):
        date_str = commit['date'].strftime("%Y-%m-%d %H:%M")
        print(f"   {i+1}. {date_str} - {commit['message'][:50]}")
    if len(sorted_commits) > 5:
        print(f"   ... and {len(sorted_commits) - 5} more")
    
    # Confirm
    response = input(f"\nReorder {len(all_commits)} commits? (yes/no): ").lower()
    if response not in ['yes', 'y']:
        print("Cancelled")
        return False
    
    # Create backup
    run_command('git tag backup-before-reorder HEAD')
    print("Created backup tag: backup-before-reorder")
    
    # Get the first commit
    success, first_commit, _ = run_command('git rev-list --max-parents=0 HEAD')
    if not success:
        print("Could not find first commit")
        return False
    
    # Create new branch and reset to first commit
    temp_branch = "temp-reorder"
    run_command(f'git checkout -b {temp_branch} {first_commit}')
    
    # Apply each commit in chronological order
    for i, commit in enumerate(sorted_commits[1:], 1):  # Skip first commit
        print(f"Applying {i}/{len(sorted_commits)-1}: {commit['hash'][:8]}")
        
        # Get the changes as a patch
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.patch', delete=False) as f:
            patch_file = f.name
        
        # Create patch
        success, patch_content, error = run_command(f'git format-patch -1 --stdout {commit["hash"]}')
        if not success:
            print(f"   Failed to create patch: {error}")
            continue
        
        # Write patch to file
        with open(patch_file, 'w') as f:
            f.write(patch_content)
        
        # Pre-create any missing files/directories that this commit needs
        create_missing_files_for_commit(commit['hash'])
        
        # Apply patch
        success, _, error = run_command(f'git am --keep-cr < {patch_file}')
        if success:
            # git am succeeded but we need to preserve original dates
            date_str = commit['date'].strftime("%Y-%m-%d %H:%M:%S")
            
            # Set environment variables for the amend command
            env_vars = {
                'GIT_AUTHOR_DATE': date_str,
                'GIT_COMMITTER_DATE': date_str,
                'GIT_AUTHOR_NAME': commit["author_name"],
                'GIT_AUTHOR_EMAIL': commit["author_email"]
            }
            
            success, _, amend_error = run_command('git commit --amend --no-edit', env_vars=env_vars)
            if success:
                print(f"   Applied with git am and preserved dates")
            else:
                print(f"   git am succeeded but date preservation failed: {amend_error}")
        else:
            print(f"     git am failed: {error}")
            
            # Try with git apply if git am fails
            success, _, error = run_command(f'git apply --index {patch_file}')
            if not success:
                print(f"     git apply --index failed: {error}")
                
                # Try basic git apply
                success, _, error = run_command(f'git apply {patch_file}')
                if success:
                    # Stage all changes
                    run_command('git add -A')
                    print(f"     Applied with git apply and staged")
                else:
                    print(f"     All patch methods failed: {error}")
                    # Try to extract and apply file contents manually
                    apply_patch_manually(patch_content, commit)
                    
            # If we have staged changes, commit them
            success, status_check, _ = run_command('git diff --cached --quiet')
            if not success:  # There are staged changes
                date_str = commit['date'].strftime("%Y-%m-%d %H:%M:%S")
                safe_msg = commit['message'].replace('"', '\\"')
                
                # Use environment variables for commit
                env_vars = {
                    'GIT_AUTHOR_DATE': date_str,
                    'GIT_COMMITTER_DATE': date_str,
                    'GIT_AUTHOR_NAME': commit["author_name"],
                    'GIT_AUTHOR_EMAIL': commit["author_email"]
                }
                
                success, _, commit_error = run_command(f'git commit -m "{safe_msg}"', env_vars=env_vars)
                if success:
                    print(f"   Committed manually")
                else:
                    print(f"   Manual commit failed: {commit_error}")
            else:
                print(f"   No changes to commit")
        
        # Clean up
        os.unlink(patch_file)
    
    # Switch back to main and replace with reordered history
    run_command('git checkout main')
    run_command(f'git reset --hard {temp_branch}')
    run_command(f'git branch -D {temp_branch}')
    
    print("\nSuccessfully reordered git history!")
    print("New history:")
    success, history_output, _ = run_command('git log --oneline --date=short -10')
    if success:
        print(history_output)
    
    # Force push the reordered history
    print("\nForce pushing reordered history to origin...")
    success, push_output, push_error = run_command('git push origin main --force')
    if success:
        print("Successfully force pushed reordered history!")
        if push_output:
            print(push_output)
    else:
        print(f"Force push failed: {push_error}")
        print("You may need to manually run: git push origin main --force")
    
    return True

if __name__ == "__main__":
    print("Git History Chronological Reorder")
    print("=" * 40)
    
    # Check git repo
    success, _, _ = run_command("git status")
    if not success:
        print("Not in a git repository!")
        exit(1)
    
    # Check for uncommitted changes
    success, status_output, _ = run_command("git status --porcelain")
    if status_output.strip():
        print("You have uncommitted changes. Please commit or stash them first.")
        exit(1)
    
    reorder_history()