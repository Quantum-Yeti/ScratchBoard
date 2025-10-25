from datetime import datetime

import feedparser
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser, QScrollArea
from PySide6.QtCore import Qt, QTimer
from utils.resource_path import resource_path


class NewsFeedView(QWidget):
    def __init__(self, feed_url="https://news.ycombinator.com/rss" + "https://hackernoon.com/feed"):
        super().__init__()
        self.feed_url = feed_url

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.title_label = QLabel("📰 Latest News")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("NewsTitle")
        layout.addWidget(self.title_label)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setObjectName("NewsContent")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.browser)
        layout.addWidget(scroll)

        self.load_news()
        self.load_stylesheet()

        # Refresh every 15 minutes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_news)
        self.timer.start(900000)

    def load_stylesheet(self):
        """Load dark QSS styling for the news feed."""
        try:
            with open(resource_path("ui/themes/news_feed.qss"), "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Failed to load news_feed.qss:", e)

    def load_news(self):
        """Fetch and display combined Hacker News and Y Combinator RSS feeds."""
        feed_urls = [
            "https://news.ycombinator.com/rss",  # Hacker News
            "https://www.ycombinator.com/feed"   # Y Combinator News
        ]

        combined_entries = []

        # Parse each feed and add entries
        for url in feed_urls:
            feed = feedparser.parse(url)
            combined_entries.extend(feed.entries)

        # Sort entries by published date (newest first)
        def get_date(entry):
            return datetime(*entry.published_parsed[:6]) if 'published_parsed' in entry else datetime.min

        combined_entries.sort(key=get_date, reverse=True)

        # Build HTML
        html = "<ul style='padding-left: 0;'>"
        for entry in combined_entries[:40]:  # Limit to 40 items
            summary = getattr(entry, "summary", "")[:100]
            html += f"""
                <li style='margin-bottom:10px; list-style: none;'>
                    <a href="{entry.link}" style="color:#4FC3F7; font-weight:bold; text-decoration:none;">{entry.title}</a><br>
                    <span style="color:#aaa; font-size:12px;">{summary}...</span>
                </li>
            """
        html += "</ul>"

        # Set HTML to QTextBrowser
        self.browser.setHtml(html)


