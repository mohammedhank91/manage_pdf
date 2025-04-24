from PyQt6.QtWidgets import QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

def add_developer_credit(self):
    """Add developer credit to the application"""
    credit_layout = QHBoxLayout()
    
    credit_label = QLabel("© Developed by: <a href='https://github.com/mohammedhank91'>mohammedhank91</a>")
    credit_label.setStyleSheet("color: #757575; font-size: 8pt;")
    credit_label.setOpenExternalLinks(True)
    credit_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    
    credit_layout.addStretch()
    credit_layout.addWidget(credit_label)
    
    self.main_layout.addLayout(credit_layout)
    