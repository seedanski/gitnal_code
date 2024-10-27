import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from requests.auth import HTTPBasicAuth
import json
import os
import subprocess

# Path for storing credentials
CONFIG_FILE = "config.json"

# Function to load saved credentials from file
def load_credentials():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
                data = json.load(f)
                return data.get("username", ""), data.get("token", "")
            except json.JSONDecodeError:
                return "", ""
    return "", ""

# Function to save credentials to file
def save_credentials(username, token):
    data = {
        "username": username,
        "token": token
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

# Function to check if the current directory is a Git repository
def is_git_repo():
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

# Function to check if a repository exists
def check_repository_exists(username, token, repo_name="gitnal"):
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    response = requests.get(url, auth=HTTPBasicAuth(username, token))
    if response.status_code == 200:
        return True, f"Repository '{repo_name}' exists."
    elif response.status_code == 404:
        return False, f"Repository '{repo_name}' does not exist."
    elif response.status_code == 403:
        return False, "Access forbidden. Check permissions or token scope."
    else:
        return False, f"Error: {response.status_code} - {response.json().get('message', '')}"


def create_private_repository(username, token, repo_name="gitnal"):
    # GitHub API URL for repository creation
    url = "https://api.github.com/user/repos"
    payload = {
        "name": repo_name,
        "description": "A private digital diary using Git commits as entries.",
        "private": True
    }
    headers = {"Accept": "application/vnd.github.v3+json"}

    # Initialize Git repository if it doesn't already exist
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "branch", "-m", "main"], check=True)  # Rename default branch to 'main'
    
    # Attempt to create the repository on GitHub
    response = requests.post(url, auth=HTTPBasicAuth(username, token), headers=headers, json=payload)
    if response.status_code == 201:
        print(f"Repository '{repo_name}' created on GitHub.")
    elif response.status_code == 422 and 'already exists' in response.json().get("message", ""):
        print(f"Repository '{repo_name}' already exists on GitHub.")
    else:
        print(f"Error: {response.status_code} - {response.json().get('message', '')}")
        return False, f"Error: {response.status_code} - {response.json().get('message', '')}"

    # Check if 'origin' remote exists, if not add it with embedded credentials in URL
    try:
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True)
        print("Remote 'origin' already exists:", result.stdout.strip())
    except subprocess.CalledProcessError:
        # Add remote with embedded credentials in URL
        remote_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)
        print("Remote 'origin' added:", remote_url)

    # Create an initial commit to set up the branch on GitHub
    try:
        # Create a placeholder file to commit (e.g., .gitignore)
        with open(".gitignore", "w") as f:
            f.write("# Ignore all log files\n*.log\n")
        
        # Stage and commit the file
        subprocess.run(["git", "add", ".gitignore"], check=True)
        subprocess.run(["git", "commit", "-m", "Your first gitnal journal entry. Happy gitnalling!"], check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)  # Push to create 'main' branch on GitHub
        print("Initial commit pushed to 'main' branch on GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to make an initial commit: {e}")
        return False, "Failed to make an initial commit."

    # Verify connection to the remote repository to ensure access rights
    try:
        subprocess.run(["git", "ls-remote", "origin"], check=True)
        print("Remote connection to 'origin' verified.")
    except subprocess.CalledProcessError:
        print("Failed to connect to the remote repository. Please ensure access rights are correct.")
        return False, "Failed to connect to the remote repository. Please ensure access rights are correct."
    
    return True, f"Repository '{repo_name}' is set up with remote 'origin'."


# Function to handle button click
def on_submit():
    username = username_entry.get()
    token = token_entry.get()
    repo_name = "gitnal"

    if not username or not token:
        #messagebox.showwarning("Input Required", "Please enter both username and token.")
        update_status_message("Input Required: Please enter both username and token.")
        return
    
    if is_git_repo():
        update_status_message("Error: A Git repository already exists in this directory.\n Move the script to a different empty directory or delete the git repo in the current directory.")
        return

    # Save the credentials for future use
    save_credentials(username, token)

    # Check repository status and update status panel
    exists = update_status_panel(username, token, repo_name)

    if not exists:
        created, creation_message = create_private_repository(username, token, repo_name)
        # Check repository status and update status panel
        update_status_panel(username, token, repo_name)
        #messagebox.showinfo("Repository Creation", creation_message)
        update_status_message("Repository Creation " + creation_message)
    

# Call `fetch_journal_entries` after updating the status
def update_status_panel(username, token, repo_name="gitnal"):
    exists, message = check_repository_exists(username, token, repo_name)
    if exists:
        status_label.config(text="Connected", fg="green")
        icon_label.config(image=green_check_icon)
        
        # Disable the create repo button
        submit_button.config(state="disabled")
        
        # Fetch and display journal entries if connected
        fetch_journal_entries()
    else:
        status_label.config(text="Not Connected", fg="red")
        icon_label.config(image=red_x_icon)

        setup_text =    "Setup instructions: \n" \
                        "1) Create a github account.\n" \
                        "2) Create a github personal access token.\n" \
                        "3) Enter the github user account and personal \n" \
                        "   above and press Create Repository.\n\n" \
                        "Journal entries are made by typing into the bottom\n" \
                        " right textbox and pressing Submit Entry."
        message_label.config(text=setup_text)


def submit_journal_entry():
    entry_text = journal_text_entry.get("1.0", tk.END).strip()
    if not entry_text:
        #messagebox.showwarning("Empty Entry", "Please write something in the journal entry box before submitting.")
        update_status_message("Empty Entry: Please write something in the journal entry box before submitting.")
        return
    
    try:
        # Initialize repository and set up for commit
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        
        # Pull remote changes before committing to avoid conflicts
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
        # Commit and push the entry
        subprocess.run(["git", "commit", "--allow-empty", "-m", entry_text], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        #messagebox.showinfo("Success", "Journal entry submitted and pushed successfully.")
        update_status_message("Success: Journal entry submitted and pushed successfully.")

        # Clear the entry box after submission
        journal_text_entry.delete("1.0", tk.END)
        #display_welcome_entry("Entry submitted successfully.\n\n" + entry_text)
        fetch_journal_entries()

    except subprocess.CalledProcessError as e:
        # messagebox.showerror("Error", f"Failed to submit entry: {e}")
        update_status_message("Error:" + f"Failed to submit entry: {e}")

# Function to fetch existing journal entries with date and time
def fetch_journal_entries():
    try:
        # Run `git log` to get a list of commit messages with full timestamp
        result = subprocess.run(
            ["git", "log", "--pretty=format:%ad - %s", "--date=format:%Y-%m-%d %H:%M:%S"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Display fetched entries in the read-only text widget
        display_journal_entries(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to fetch journal entries: {e}")

# Function to display fetched journal entries
def display_journal_entries(entries):
    # Enable the text widget temporarily to insert text
    journal_text_display.config(state="normal")
    journal_text_display.delete("1.0", tk.END)  # Clear previous content
    journal_text_display.insert("1.0", entries)  # Insert fetched entries
    journal_text_display.config(state="disabled")  # Set back to read-only

# Function to display sample journal entry
def display_welcome_entry(entry_text):
    # Enable state temporarily to insert text
    journal_text_display.config(state="normal")
    journal_text_display.delete("1.0", tk.END)  # Clear previous content
    journal_text_display.insert("1.0", entry_text)  # Insert new entry text
    journal_text_display.config(state="disabled")  # Set back to read-only


def update_status_message(message):
    message_label.config(text=message)

# Load credentials at startup
saved_username, saved_token = load_credentials()

# Set up the Tkinter window
root = tk.Tk()
root.geometry("800x450")
root.title("GitHub Repository Manager")

# Main frame to hold the left and right panels
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

# Left panel for inputs and status
left_panel = tk.Frame(main_frame)
left_panel.pack(side="left", fill="y", padx=5)

# Username label and entry
username_label = tk.Label(left_panel, text="GitHub Username:")
username_label.pack()
username_entry = tk.Entry(left_panel)
username_entry.insert(0, saved_username)  # Load saved username if available
username_entry.pack()

# Token label and entry
token_label = tk.Label(left_panel, text="GitHub Token:")
token_label.pack()
token_entry = tk.Entry(left_panel, show="*")  # Hides token input
token_entry.insert(0, saved_token)  # Load saved token if available
token_entry.pack()

# Submit button
submit_button = tk.Button(left_panel, text="Check/Create Repository", command=on_submit)
submit_button.pack(pady=5)

# Status panel frame
status_frame = tk.Frame(left_panel)
status_frame.pack(pady=10)

# Load status icons
green_check_icon = ImageTk.PhotoImage(Image.open("green_check.png").resize((20, 20)))
red_x_icon = ImageTk.PhotoImage(Image.open("red_x.png").resize((20, 20)))

# Icon and label for connection status
icon_label = tk.Label(status_frame)
icon_label.pack(side="left")

status_label = tk.Label(status_frame, text="Checking connection...", font=("Arial", 12))
status_label.pack(side="left")

# New label for status messages
message_label = tk.Label(left_panel, text="", font=("Arial", 10), wraplength=200)  # Adjust wraplength as needed
message_label.pack(pady=5)

# Right panel for displaying and creating journal entries
right_panel = tk.Frame(main_frame)
right_panel.pack(side="right", fill="both", expand=True)

# Create a frame for the display text box and its scrollbar
display_frame = tk.Frame(right_panel)
display_frame.pack(fill="both", expand=True)

# Read-only Text widget for viewing journal entries
journal_text_display = tk.Text(display_frame, wrap="word", state="disabled", width=70, height=10, font=("Arial", 10))
journal_text_display.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)

# Scrollbar for the journal display
scrollbar = tk.Scrollbar(display_frame, command=journal_text_display.yview)
scrollbar.pack(side="right", fill="y")

# Link scrollbar to the text widget
journal_text_display.config(yscrollcommand=scrollbar.set)

# Create a frame for the entry text box and its scrollbar
entry_frame = tk.Frame(right_panel)
entry_frame.pack(fill="both", expand=True)

# Textbox for entering new journal entries
journal_text_entry = tk.Text(entry_frame, wrap="word", width=70, height=10, font=("Arial", 10))  # Adjust width as needed
journal_text_entry.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)

# Scrollbar for the journal entry box
entry_scrollbar = tk.Scrollbar(entry_frame, command=journal_text_entry.yview)
entry_scrollbar.pack(side="right", fill="y")

# Link scrollbar to the entry text widget
journal_text_entry.config(yscrollcommand=entry_scrollbar.set)

# Button frame for the submit button below textboxes
button_frame = tk.Frame(right_panel)
button_frame.pack(pady=5)

# Submit journal entry button
submit_journal_button = tk.Button(button_frame, text="Submit Entry", command=submit_journal_entry)
submit_journal_button.pack()

# Example: Call this to display a sample entry when needed
welcome_entry = "Welcome to your Git-based digital diary!\n\n" \
               "This panel will show your journal entries.\n" \
               "--------------------------------------------------------------------------"
display_welcome_entry(welcome_entry)

# Run initial connection check with saved credentials
update_status_panel(saved_username, saved_token)

# Run the Tkinter event loop
root.mainloop()
