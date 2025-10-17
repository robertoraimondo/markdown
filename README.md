# Markdown Editor

A modern desktop Markdown editor with WYSIWYG preview, advanced formatting, and Azure Boards integration.

<img width="1909" height="1028" alt="markdown" src="https://github.com/user-attachments/assets/67808159-f91a-4000-bed4-5835cf51083e" />


## Features
- Edit Markdown with live preview
- Context menu for formatting: bold, italic, underline, strikethrough, highlight, headings, lists, code, tables, images, and more
- Insert and resize images (fixed size or free-hand in preview)
- Table editor: choose between simple, pretty (tabulate), or grid-based editing
- Highlight text with background color
- File menu: New, Open, Save, Publish (create Azure Boards task)
- Azure Boards integration: create tasks directly from the editor
- Maximized window on launch, custom icon (md.ico)

## Requirements
- Python 3.x
- PyQt5
- markdown2
- tabulate
- requests

## Setup
1. Install dependencies:
   ```sh
   pip install pyqt5 markdown2 tabulate requests
   ```
2. Place `md.ico` in the same directory as `main.py` for the app icon.
3. (Optional) For Azure Boards integration, see `AZURE_SETUP.md` for setup instructions.

## Usage
- Run the editor:
  ```sh
  python md_editor/main.py
  ```
- Use the File menu for file operations and publishing to Azure Boards.
- Right-click in the editor for formatting options.
- Insert tables and images with advanced options.

## License

This project is open source and available under the MIT License.

**Author: Roberto Raimondo - IS Senior Systems Engineer II**

© 2025 All Rights Reserved.

