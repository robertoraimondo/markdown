import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QSplitter, QWidget, QVBoxLayout, QToolBar, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import markdown2
from functools import partial

class MarkdownEditor(QMainWindow):
    def editor_context_menu(self, pos):
        menu = self.editor.createStandardContextMenu()
        menu.addSeparator()
        # Formatting actions
        menu.addAction("Normal Text", self.insert_normal_text)
        menu.addAction("Bold", self.make_bold)
        menu.addAction("Italic", self.make_italic)
        menu.addAction("Underline", self.insert_underline)
        menu.addAction("Strikethrough", self.insert_strikethrough)
        menu.addAction("Highlight", self.insert_highlight)
        menu.addAction("Quote", self.insert_quote)
        menu.addAction("Bulleted List", self.insert_bulleted_list)
        menu.addAction("Ordered List", self.insert_ordered_list)
        menu.addAction("Insert Link", self.insert_link)
        menu.addAction("Add Comment", self.insert_comment)
        for i in range(1, 6):
            menu.addAction(f"Heading {i}", partial(self.insert_heading, i))
        menu.addAction("Caption Header", self.insert_caption)
        menu.addAction("Code Block", self.insert_code_block)
        menu.addAction("Inline Code", self.insert_inline_code)
        menu.addAction("Checklist", lambda: self.editor.insertPlainText("- [ ] Task\n"))
        menu.addAction("Tasks", lambda: self.editor.insertPlainText("- [ ] Task 1\n- [x] Task 2\n"))
        menu.addAction("Table", self.insert_table)
        menu.addAction("Image", self.insert_image)
        menu.exec_(self.editor.mapToGlobal(pos))

    def new_file(self):
        self.editor.clear()
    def make_bold(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"**{text}**")
        else:
            cursor.insertText("****")
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 2)
            self.editor.setTextCursor(cursor)

    def make_italic(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"*{text}*")
        else:
            cursor.insertText("**")
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
            self.editor.setTextCursor(cursor)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Markdown Editor")
        self.setWindowIcon(QIcon("md.ico"))
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        # File Menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        # Rename 'Create a new task' to 'Publish'
        publish_action = QAction("Publish", self)
        publish_action.triggered.connect(self.create_azure_task)
        file_menu.addAction(publish_action)

        # Add all toolbar actions (Normal, Bold, Italic, etc.)
        # ...existing code for adding actions to format_toolbar...

        # Editor and Preview Splitter
        splitter = QSplitter(Qt.Horizontal)
        self.editor = QTextEdit()
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.editor_context_menu)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setSizes([600, 600])

        # Layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        # Remove open_btn from btn_layout and UI
        layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

        # Connect editor changes to preview
        self.editor.textChanged.connect(self.update_preview)

    def create_azure_task(self):
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        import requests
        import base64
        # Prompt for credentials if not set
        if not hasattr(self, '_azure_org_url'):
            org_url, ok = QInputDialog.getText(self, "Azure DevOps Org URL", "e.g. https://dev.azure.com/yourorg")
            if not ok or not org_url.strip():
                return
            self._azure_org_url = org_url.strip()
        if not hasattr(self, '_azure_project'):
            project, ok = QInputDialog.getText(self, "Azure Project Name", "Enter Azure DevOps project name:")
            if not ok or not project.strip():
                return
            self._azure_project = project.strip()
        if not hasattr(self, '_azure_pat'):
            pat, ok = QInputDialog.getText(self, "Azure Personal Access Token", "Enter Azure DevOps PAT:")
            if not ok or not pat.strip():
                return
            self._azure_pat = pat.strip()
        title, ok1 = QInputDialog.getText(self, "Azure Task Title", "Enter task title:")
        if not ok1 or not title.strip():
            return
        desc, ok2 = QInputDialog.getMultiLineText(self, "Azure Task Description", "Enter task description:")
        if not ok2:
            return
        # Azure Boards API call
        url = f"{self._azure_org_url}/{self._azure_project}/_apis/wit/workitems/$Task?api-version=6.0"
        headers = {
            'Content-Type': 'application/json-patch+json',
            'Authorization': 'Basic ' + base64.b64encode(f':{self._azure_pat}'.encode()).decode()
        }
        data = [
            {"op": "add", "path": "/fields/System.Title", "from": None, "value": title},
            {"op": "add", "path": "/fields/System.Description", "from": None, "value": desc}
        ]
        try:
            resp = requests.post(url, headers=headers, json=data)
            if resp.status_code == 200 or resp.status_code == 201:
                workitem = resp.json()
                task_id = workitem.get('id', 'Unknown')
                QMessageBox.information(self, "Azure Task", f"Task Created!\nID: {task_id}\nTitle: {title}")
            else:
                QMessageBox.warning(self, "Azure Task Error", f"Failed to create task.\nStatus: {resp.status_code}\n{resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Azure Task Error", f"Exception: {e}")

    def open_azure_task(self):
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        import requests
        import base64
        # Prompt for credentials if not set
        if not hasattr(self, '_azure_org_url'):
            org_url, ok = QInputDialog.getText(self, "Azure DevOps Org URL", "e.g. https://dev.azure.com/yourorg")
            if not ok or not org_url.strip():
                return
            self._azure_org_url = org_url.strip()
        if not hasattr(self, '_azure_project'):
            project, ok = QInputDialog.getText(self, "Azure Project Name", "Enter Azure DevOps project name:")
            if not ok or not project.strip():
                return
            self._azure_project = project.strip()
        if not hasattr(self, '_azure_pat'):
            pat, ok = QInputDialog.getText(self, "Azure Personal Access Token", "Enter Azure DevOps PAT:")
            if not ok or not pat.strip():
                return
            self._azure_pat = pat.strip()
        task_id, ok = QInputDialog.getText(self, "Azure Task ID", "Enter Azure Boards Task ID:")
        if not ok or not task_id.strip():
            return
        url = f"{self._azure_org_url}/{self._azure_project}/_apis/wit/workitems/{task_id.strip()}?api-version=6.0"
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(f':{self._azure_pat}'.encode()).decode()
        }
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                workitem = resp.json()
                title = workitem['fields'].get('System.Title', 'No Title')
                desc = workitem['fields'].get('System.Description', 'No Description')
                QMessageBox.information(self, "Azure Task", f"ID: {task_id}\nTitle: {title}\nDescription: {desc}")
            else:
                QMessageBox.warning(self, "Azure Task Error", f"Failed to fetch task.\nStatus: {resp.status_code}\n{resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Azure Task Error", f"Exception: {e}")

    def insert_inline_code(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f'`{text}`')
        else:
            cursor.insertText('``')
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 1)
            self.editor.setTextCursor(cursor)
    def insert_normal_text(self):
        import re
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            # Remove code blocks (```...```)
            text = re.sub(r'```[\s\S]*?```', '', text)
            # Remove inline code
            text = re.sub(r'`([^`]+)`', r'\1', text)
            # Remove bold, italic, strikethrough, highlight (nested and simple)
            text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # bold
            text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)     # italic
            text = re.sub(r'~~(.*?)~~', r'\1', text)           # strikethrough
            text = re.sub(r'==(.*?)==', r'\1', text)           # highlight
            # Remove headings
            text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)
            # Remove blockquotes
            text = re.sub(r'^\s*>\s*', '', text, flags=re.MULTILINE)
            # Remove unordered and ordered lists
            text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
            text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
            # Remove checklists
            text = re.sub(r'- \[[ xX]\] ', '', text)
            # Remove links/images, keep text
            text = re.sub(r'!\[([^\]]*)\]\([^\)]*\)', r'\1', text)  # images
            text = re.sub(r'\[([^\]]+)\]\([^\)]*\)', r'\1', text)   # links
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            # Remove comments
            text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
            # Remove table pipes and headers
            text = re.sub(r'\|', '', text)
            text = re.sub(r'^\s*-{3,}\s*$', '', text, flags=re.MULTILINE)  # table header lines
            # Remove extra whitespace and collapse newlines
            text = re.sub(r'\s+\n', '\n', text)
            text = re.sub(r'\n+', '\n', text)
            text = text.strip()
            # Replace selection with cleaned text
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(text)
            cursor.endEditBlock()
        else:
            cursor.insertText("Normal text")

    def insert_highlight(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"=={selected_text}==")
        else:
            cursor.insertText("==highlight==")

    def insert_quote(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"> {text}")
        else:
            cursor.insertText("> ")

    def insert_bulleted_list(self):
        self.editor.insertPlainText("- Item 1\n- Item 2\n")

    def insert_ordered_list(self):
        self.editor.insertPlainText("1. Item 1\n2. Item 2\n")

    def insert_link(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"[{text}](http://example.com)")
        else:
            cursor.insertText("[text](http://example.com)")

    def insert_comment(self):
        self.editor.insertPlainText("<!-- Comment -->\n")

    def insert_heading(self, level):
        cursor = self.editor.textCursor()
        hashes = '#' * level
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"{hashes} {text}")
        else:
            cursor.insertText(f"{hashes} Heading {level}\n")

    def insert_caption(self):
        self.editor.insertPlainText("### Caption Header\n")

    def insert_code_block(self):
        self.editor.insertPlainText("```python\n# code here\n```\n")

    # ...existing code for init_ui above...

    def insert_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            from PyQt5.QtWidgets import QInputDialog
            width, ok_w = QInputDialog.getText(self, "Image Width", "Enter width (px or %), or leave blank:")
            height, ok_h = QInputDialog.getText(self, "Image Height", "Enter height (px or %), or leave blank:")
            cursor = self.editor.textCursor()
            if width.strip() or height.strip():
                # Use HTML <img> tag for custom size
                width_attr = f' width=\"{width.strip()}\"' if width.strip() else ''
                height_attr = f' height=\"{height.strip()}\"' if height.strip() else ''
                cursor.insertText(f'<img src="{file_name}" alt="image"{width_attr}{height_attr} />')
            else:
                # Standard markdown
                cursor.insertText(f'![alt text]({file_name})')

    def insert_table(self):
        from PyQt5.QtWidgets import QInputDialog, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLabel
        import sys
        from tabulate import tabulate

        # Ask user for formatter type
        formatter, ok = QInputDialog.getItem(self, "Table Formatter", "Choose table formatter:", ["Grid Editor (GUI)", "Tabulate (Pretty Markdown)", "Simple Markdown"], 0, False)
        if not ok:
            return

        if formatter == "Tabulate (Pretty Markdown)":
            cols, ok1 = QInputDialog.getInt(self, "Table Columns", "Enter number of columns:", 2, 1, 20)
            if not ok1:
                return
            rows, ok2 = QInputDialog.getInt(self, "Table Rows", "Enter number of rows:", 2, 1, 50)
            if not ok2:
                return
            headers = [f"Header {i+1}" for i in range(cols)]
            data = [[f"Cell {r+1},{c+1}" for c in range(cols)] for r in range(rows)]
            table_md = tabulate(data, headers, tablefmt="github")
            self.editor.insertPlainText(table_md + "\n")
            return

        if formatter == "Simple Markdown":
            cols, ok1 = QInputDialog.getInt(self, "Table Columns", "Enter number of columns:", 2, 1, 20)
            if not ok1:
                return
            rows, ok2 = QInputDialog.getInt(self, "Table Rows", "Enter number of rows:", 2, 1, 50)
            if not ok2:
                return
            header = '| ' + ' | '.join([f'Header {i+1}' for i in range(cols)]) + ' |\n'
            separator = '| ' + ' | '.join(['---'] * cols) + ' |\n'
            body = ''
            for r in range(rows):
                body += '| ' + ' | '.join([f'Cell {r+1},{c+1}' for c in range(cols)]) + ' |\n'
            table_md = header + separator + body
            self.editor.insertPlainText(table_md)
            return

        # Grid Editor (GUI)
        class TableDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Table Editor")
                self.resize(600, 400)
                layout = QVBoxLayout(self)
                self.label = QLabel("Double-click cells to edit. Click 'Insert' when done.")
                layout.addWidget(self.label)
                self.table = QTableWidget(rows, cols)
                self.table.setHorizontalHeaderLabels([f"Header {i+1}" for i in range(cols)])
                for r in range(rows):
                    for c in range(cols):
                        self.table.setItem(r, c, QTableWidgetItem(f"Cell {r+1},{c+1}"))
                layout.addWidget(self.table)
                btns = QHBoxLayout()
                self.insert_btn = QPushButton("Insert")
                self.insert_btn.clicked.connect(self.accept)
                btns.addWidget(self.insert_btn)
                self.cancel_btn = QPushButton("Cancel")
                self.cancel_btn.clicked.connect(self.reject)
                btns.addWidget(self.cancel_btn)
                layout.addLayout(btns)
            def get_table(self):
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                data = []
                for r in range(self.table.rowCount()):
                    row = []
                    for c in range(self.table.columnCount()):
                        item = self.table.item(r, c)
                        row.append(item.text() if item else "")
                    data.append(row)
                return headers, data
        # Ask for size
        cols, ok1 = QInputDialog.getInt(self, "Table Columns", "Enter number of columns:", 2, 1, 20)
        if not ok1:
            return
        rows, ok2 = QInputDialog.getInt(self, "Table Rows", "Enter number of rows:", 2, 1, 50)
        if not ok2:
            return
        dlg = TableDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            headers, data = dlg.get_table()
            table_md = tabulate(data, headers, tablefmt="github")
            self.editor.insertPlainText(table_md + "\n")

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", "Markdown Files (*.md)")
        if file_name:
            with open(file_name, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Markdown File", "", "Markdown Files (*.md)")
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())

    def update_preview(self):
        md_text = self.editor.toPlainText()
        import markdown2
        html = markdown2.markdown(md_text)
        import re
        # Strikethrough: ~~text~~ -> <s>text</s>
        html = re.sub(r'~~(.*?)~~', r'<s>\1</s>', html, flags=re.DOTALL)
        # Highlight: ==text== -> <mark>text</mark>
        html = re.sub(r'==([^=\n][^=]*?)==', r'<mark>\1</mark>', html, flags=re.DOTALL)
        # Inject CSS for <mark> and resizable images
        html = '''<style>\nmark { background-color: yellow; color: black; }\nimg.resizable {\n  resize: both;\n  overflow: auto;\n  max-width: 100%;\n  max-height: 100%;\n  min-width: 20px;\n  min-height: 20px;\n  display: inline-block;\n}\n</style>''' + html
        # Add resizable class to all <img> tags
        html = re.sub(r'<img ', '<img class="resizable" ', html)
        self.preview.setHtml(html)

    def insert_underline(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            # QTextEdit.selectedText() replaces newlines with unicode U+2029, restore them
            text = text.replace("\u2029", "\n")
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(f"<u>{text}</u>")
            cursor.endEditBlock()
        else:
            cursor.insertText("<u></u>")
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 4)
            self.editor.setTextCursor(cursor)

    def insert_strikethrough(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            text = text.replace("\u2029", "\n")
            cursor.beginEditBlock()
            cursor.removeSelectedText()
            cursor.insertText(f"~~{text}~~")
            cursor.endEditBlock()
        else:
            cursor.insertText("~~~~")
            cursor.movePosition(cursor.Left, cursor.MoveAnchor, 2)
            self.editor.setTextCursor(cursor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownEditor()
    window.show()
    sys.exit(app.exec_())
