from bs4 import BeautifulSoup

def parse_detail(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    return {"title": soup.title.string.strip() if soup.title else "Unknown"}
