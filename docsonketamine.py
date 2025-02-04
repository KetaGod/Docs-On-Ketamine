import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog, QAction, QVBoxLayout, QWidget, QToolBar, QColorDialog, QFontDialog, QMessageBox, QLabel, QPushButton
from PyQt5.QtGui import QIcon, QTextCursor, QTextCharFormat, QColor, QFont, QPixmap
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

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

class DocsOnKetamine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Docs on Ketamine | Coded by @KetaGod")
        self.setGeometry(100, 100, 1000, 700)

        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.highlighter = SyntaxHighlighter(self.text_edit.document())

        self.create_menu()
        self.create_toolbar()
        self.create_theme_toggle()

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

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;Rich Text Files (*.rtf)")
        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                self.text_edit.setText(file.read())

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;Rich Text Files (*.rtf)")
        if file_name:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(self.text_edit.toPlainText())

    def print_document(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            self.text_edit.print(printer)

    def make_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        self.text_edit.textCursor().mergeCharFormat(fmt)

    def make_italic(self):
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
        file_name, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.bmp *.gif *.webm)")
        if file_name:
            cursor = self.text_edit.textCursor()
            cursor.insertHtml(f'<img src="{file_name}" width="200">')

### FILL THIS PART WITH YOUR OWN EMAIL/INFORMATION ###
    def send_email(self):
        msg = MIMEMultipart()
        msg['From'] = 'your_email@example.com'
        msg['To'] = 'recipient@example.com'
        msg['Subject'] = 'Document'
        msg.attach(MIMEText(self.text_edit.toPlainText(), 'plain'))
        server = smtplib.SMTP('smtp.example.com', 587) ### CAN CHANGE THIS TO WHAT YOUR PROVIDER IS (i.e. ProtonMail, Yahoo, Gmail, etc) ###
        server.starttls()
        server.login('your_email@example.com', 'your_password')
        server.send_message(msg)
        server.quit()

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
