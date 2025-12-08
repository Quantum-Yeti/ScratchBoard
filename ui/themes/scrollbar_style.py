vertical_scrollbar_style = """
    QScrollBar:vertical {
        background: #1F1F1F;
        width: 12px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #3E8CA3;
        min-height: 20px;
        border-radius: 4px;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        background: none;
        height: 0px;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: #1F1F1F;
    }
"""