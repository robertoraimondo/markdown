# Azure DevOps Integration Setup

To enable real Azure Boards integration, you need:

1. An Azure DevOps organization and project
2. A Personal Access Token (PAT) with Work Items (read/write) scope
3. The `requests` Python package (install with `pip install requests`)

## Steps

1. Go to https://dev.azure.com/ and sign in
2. Click your user icon > Personal access tokens > New Token
   - Organization: your org
   - Scopes: Work Items (read/write)
   - Copy the token (you won't see it again)
3. Store your org URL, project name, and PAT securely

## Example usage in code
- org_url: https://dev.azure.com/yourorg
- project: YourProject
- pat: <your PAT>

You will be prompted for these the first time you create a task.

---

This file is for reference only. The integration will be added to the app code next.
