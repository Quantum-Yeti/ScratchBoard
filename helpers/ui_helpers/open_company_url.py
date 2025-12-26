# Get company website
import webbrowser

from utils.resource_path import resource_path


def get_company_homepage():
        try:
            with open(resource_path("resources/user_site.txt"), "r") as f:
                url = f.read().strip()
                return url
        except Exception as e:
            print("Failed to load website.")
            return None

def open_company_homepage():
    url = get_company_homepage()
    if url:
        webbrowser.open(url, new=1)