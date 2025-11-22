def update_window_title(self, category=None):
    """Update window title to 'ScratchBoard - Category'"""
    title = "Scratch Board"
    if category:
        title += f" : {category}"
    self.setWindowTitle(title)
