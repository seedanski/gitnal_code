Gitnal: Git-Based Digital Diary

Gitnal is a private digital journal manager that utilizes Git and GitHub to securely store journal entries as Git commits. This application, built with Python and Tkinter, offers a simple interface for managing a private repository to store journal entries over time.
Features

    Journal Entry Management: Create and submit journal entries that are committed directly to a Git repository.
    GitHub Repository Integration: Check if a GitHub repository exists, create a private repository if necessary, and securely connect for remote storage.
    Local Git Setup: Automatically sets up a local Git repository if not already present.
    Date-Based Display: Shows a list of all journal entries by date in a read-only text box.
    Simple UI with Status Indicators: A Tkinter GUI provides a user-friendly interface for managing entries and repository connectivity.

Requirements

    Python 3.8+
    Libraries:
        requests
        tkinter (typically bundled with Python installations)

Setup Instructions

    Clone this repository:

    bash

git clone https://github.com/your-username/gitnal_code.git
cd gitnal

Install dependencies: You can use pip to install any missing libraries:

bash

Set up a GitHub Personal Access Token (PAT):

    Go to your GitHub settings under Developer Settings > Personal Access Tokens.
    Generate a new token with repo and workflow permissions.

Run the Application:

bash

    python gitnal.py

Usage

    Enter GitHub Credentials:
        Enter your GitHub username and the personal access token (PAT) created above.
        The application will check if the gitnal repository exists on GitHub.
        If the repository is missing, it will create it automatically.

    Add a Journal Entry:
        Type a new journal entry in the "Journal Entry" text box.
        Click Submit Entry to commit and push the entry to the repository.

    View Previous Entries:
        The top text box displays previous entries by date and time when the application is started.

Files

    gitnal.py: Main application file.
    config.json: Stores GitHub credentials locally for easy access.

Error Handling

    Repository Already Exists: The application checks if the gitnal repository already exists and will connect to it without recreating.
    Local Git Repository Check: If a Git repository already exists in the directory, setup will stop to avoid conflicts.
    Connection and Status Updates: The left panel displays connection status and any messages related to repository setup.

Security

    GitHub credentials are stored in config.json for quick access, but please ensure this file is stored securely and not committed to the public repository.

License

This project is licensed under the MIT License. See the LICENSE file for details.
