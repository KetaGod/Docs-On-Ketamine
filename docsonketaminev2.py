import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QAction, QToolBar, QColorDialog,
    QFontDialog, QPushButton, QComboBox, QLabel, QVBoxLayout, QWidget, QMessageBox, QDialog,
    QLineEdit, QFormLayout, QDialogButtonBox
)
from PyQt5.QtGui import (
    QIcon, QTextCursor, QTextCharFormat, QColor, QFont, QDragEnterEvent, QDropEvent, QPixmap
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtCore import Qt, QRegularExpression, QMimeData
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith(('.png', '.jpg', '.gif', '.webm')):
                cursor = self.textCursor()
                cursor.insertHtml(f'<img src="{file_path}" width="200">')
            elif file_path.endswith(('.txt', '.rtf')):
                with open(file_path, "r", encoding="utf-8") as file:
                    self.setText(file.read())
        event.acceptProposedAction()

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keywords = ["def", "class", "import", "from", "return", "if", "else", "elif", "for", "while", "try", "except"]
        self.highlighting_rules += [(f"\\b{k}\\b", keyword_format) for k in keywords]

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            match_iter = expression.globalMatch(text)
            while match_iter.hasNext():
                match = match_iter.next()
                index = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(index, length, format)

class EmailSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Email Settings")

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter your email address")

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout = QFormLayout()
        form_layout.addRow("Email Address:", self.email_input)
        form_layout.addRow("password:", self.password_input)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Help, self
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        button_box.helpRequested.connect(self.show_help)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def validate_and_accept(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Email and password cannot be empty.")
        else:
            self.accept()

    def show_help(self):
        QMessageBox.information(
            self,
            "Help",
            "Enter your email address and password to configure the email settings. \n\n"
            "This information will be used to send emails from the application.",
        )

    def get_credentials(self):
        return self.email_input.text(), self.password_input.text()

class DocsOnKetamine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Docs on Ketamine | Coded by @KetaGod")
        self.setGeometry(100, 100, 1000, 700)

        icon_path = self.resource_path("snoopa.ico")
        self.setWindowIcon(QIcon(icon_path))

        self.text_edit = CustomTextEdit(self)
        self.setCentralWidget(self.text_edit)

        default_font = QFont()
        default_font.setPointSize(12)
        self.text_edit.setFont(default_font)

        self.highlighter = SyntaxHighlighter(self.text_edit.document())

        self.email = ""
        self.password = ""

        self.create_menu()
        self.create_toolbar()
        self.create_theme_toggle()
        self.create_email_provider_dropdown()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        print_action = QAction("Print", self)
        print_action.triggered.connect(self.print_document)
        file_menu.addAction(print_action)

        email_action = QAction("Send Email", self)
        email_action.triggered.connect(self.send_email)
        file_menu.addAction(email_action)

        email_settings_action = QAction("Email Settings", self)
        email_settings_action.triggered.connect(self.open_email_settings)
        file_menu.addAction(email_settings_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def create_toolbar(self):
        toolbar = QToolBar("Toolbar", self)
        self.addToolBar(toolbar)

        bold_action = QAction("Bold", self)
        bold_action.triggered.connect(self.make_bold)
        toolbar.addAction(bold_action)

        italic_action = QAction("Italic", self)
        italic_action.triggered.connect(self.make_italic)
        toolbar.addAction(italic_action)

        underline_action = QAction("Underline", self)
        underline_action.triggered.connect(self.make_underline)
        toolbar.addAction(underline_action)

        color_action = QAction("Text Color", self)
        color_action.triggered.connect(self.change_text_color)
        toolbar.addAction(color_action)

        font_action = QAction("Font", self)
        font_action.triggered.connect(self.change_font)
        toolbar.addAction(font_action)

        image_action = QAction("Insert Image", self)
        image_action.triggered.connect(self.insert_image)
        toolbar.addAction(image_action)

    def create_theme_toggle(self):
        self.theme_button = QPushButton("Toggle Theme", self)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.addToolBarBreak()
        toolbar = QToolBar("Theme", self)
        self.addToolBar(toolbar)
        toolbar.addWidget(self.theme_button)
        self.dark_mode = False
    
    def create_email_provider_dropdown(self):
        self.email_provider_label = QLabel("Email Provider:", self)
        self.email_provider_dropdown = QComboBox(self)
        self.email_provider_dropdown.addItems(["Gmail", "ProtonMail", "Yahoo", "Outlook"])
        self.email_provider_dropdown.setCurrentIndex(0)

        email_layout = QVBoxLayout()
        email_layout.addWidget(self.email_provider_label)
        email_layout.addWidget(self.email_provider_dropdown)

        email_widget = QWidget()
        email_widget.setLayout(email_layout)
        self.addToolBarBreak()
        toolbar = QToolBar("Email", self)
        self.addToolBar(toolbar)
        toolbar.addWidget(email_widget)

    def open_email_settings(self):
        dialog = EmailSettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.email, self.password = dialog.get_credentials()
            QMessageBox.information(self, "Success", "Email settings updated successfully.")

    def get_smtp_server(self):
        provider = self.email_provider_dropdown.currentText()
        if provider == "Gmail":
            return ("smtp.gmail.com", 587)
        elif provider == "ProtonMail":
            return ("smpt.protonmail.com", 587)
        elif provider == "Yahoo":
            return ("smtp.mail.yahoo.com", 587)
        elif provider == "Outlook":
            return ("smtp.office365.com", 587)
        else:
            return None

    def send_email(self):
        if not self.email or not self.password:
            QMessageBox.warning(self, "Error", "Please configure your email settings first.")
            return

        smtp_server, smtp_port = self.get_smtp_server()
        if not smtp_server:
            QMessageBox.warning(self, "Error", "Unsupported email provider. | Please contact @KetaGod to add.")
            return

        msg = MIMEMultipart()
        msg['From'] = 'your_email@example.com'
        msg['To'] = 'recipient@example.com'
        msg['Subject'] = 'Document'
        msg.attach(MIMEText(self.text_edit.toPlainText(), 'plain'))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login('your_email@example.com', 'your_password')
            server.send_message(msg)
            server.quit()
            QMessageBox.information(self, "Success", "Email sent successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to send email: {e}")

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;Rich Text Files (*.rtf)")
        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                self.text_edit.setText(file.read())

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;Rich Text Files (*.rtf)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(self.text_edit.toHtml())

    def print_document(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            self.text_edit.print(printer)

    def make_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        self.text_edit.textCursor().mergeCharFormat(fmt)

    def  make_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(True)
        self.text_edit.textCursor().mergeCharFormat(fmt)

    def make_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(True)
        self.text_edit.textCursor().mergeCharFormat(fmt)

    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self.text_edit.textCursor().mergeCharFormat(fmt)

    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            fmt = QTextCharFormat()
            fmt.setFont(font)
            self.text_edit.textCursor().mergeCharFormat(fmt)

    def insert_image(self):
        file_name, _ =QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.gif *.webm)")
        if file_name:
            cursor = self.text_edit.textCursor()
            cursor.insertHtml(f'<img src="{file_name}" width="200">')

    def toggle_theme(self):
        if self.dark_mode:
            self.setStyleSheet("")
        else:
            self.setStyleSheet("background-color: #333; color: white;")
        self.dark_mode = not self.dark_mode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocsOnKetamine()
    window.show()
    sys.exit(app.exec_())
