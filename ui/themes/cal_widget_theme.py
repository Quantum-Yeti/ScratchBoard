cal_style = """
    QWidget {
        background-color: #2E2E2E;
    }
    QLabel {
        color: #9ACEEB;
        background-color: none;
    }
    QLabel#time_label {
        font-family: Segoe UI, Consolas, monospace;
        font-size: 20px;
        font-weight: bold;
    }
    QLabel#date_label {
        font-family: Segoe UI, Consolas, monospace;
        font-size: 12px;
    }
    QProgressBar {
        height: 10px;
        border-radius: 5px;
        background: transparent;
    }
    QProgressBar::chunk {
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #9C27B0, stop:1 #7B1FA2
        );
        border-radius: 5px;
    }
"""