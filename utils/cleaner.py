from bs4 import BeautifulSoup


def extract_clean_text(raw_content):
    if not raw_content:
        return ""

    try:
        soup = BeautifulSoup(raw_content, "html.parser")
        text = soup.get_text(separator="\n")
        return text.strip()
    except:
        return raw_content