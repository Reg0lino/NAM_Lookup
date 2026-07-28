DARK_THEME_QSS = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    color: #E0E0E0;
    font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* Drop Zone Frame */
#DropZone {
    background-color: #1E1E1E;
    border: 2px dashed #3A3A3A;
    border-radius: 12px;
}

#DropZone[dragOver="true"] {
    background-color: #252A34;
    border: 2px dashed #007ACC;
}

#DropTitle {
    font-size: 16px;
    font-weight: bold;
    color: #FFFFFF;
}

#DropSubtitle {
    font-size: 12px;
    color: #888888;
}

/* Inputs & ComboBox */
QLineEdit, QComboBox {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 6px 10px;
    color: #FFFFFF;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #007ACC;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #1E1E1E;
    selection-background-color: #007ACC;
    color: #FFFFFF;
}

/* Push Buttons */
QPushButton {
    background-color: #2D2D2D;
    border: 1px solid #3D3D3D;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
    color: #FFFFFF;
}

QPushButton:hover {
    background-color: #383838;
    border-color: #007ACC;
}

QPushButton:pressed {
    background-color: #005999;
}

QPushButton#PrimaryButton {
    background-color: #007ACC;
    border: none;
    font-weight: bold;
}

QPushButton#PrimaryButton:hover {
    background-color: #0098FF;
}

QPushButton#Tone3000Button {
    background-color: #1E2A38;
    border: 1px solid #2B4C7E;
    color: #64B5F6;
}

QPushButton#Tone3000Button:hover {
    background-color: #283E58;
}

QPushButton.HardwareChip {
    background-color: #222222;
    border: 1px solid #3A3A3A;
    border-radius: 16px;
    padding: 6px 14px;
    font-size: 12px;
}

QPushButton.HardwareChip:hover {
    background-color: #2D3748;
    border-color: #4A5568;
    color: #63B3ED;
}

#StatusLabel {
    color: #9E9E9E;
    font-size: 12px;
}

QGroupBox {
    background-color: #1A1A1A;
    border: 1px solid #2C2C2C;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #007ACC;
}

/* Debug Console */
QPlainTextEdit#DebugConsole {
    background-color: #0D0D0D;
    border: 1px solid #262626;
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    color: #A0A0A0;
}
"""
