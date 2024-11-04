from urllib.parse import urlparse
from collections import defaultdict

def gen_text(template:str, **kwargs):
    if not template:
        return ' '.join(str(v) for v in kwargs.values()).strip()
    default_dict = defaultdict(str, **kwargs)
    return template.format_map(default_dict)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc)

def process_text(text):
    cleaned_text = text.strip("[]")

    parts = cleaned_text.split("', '")
    if len(parts) == 0:
        return cleaned_text,""
    last_part = parts[-1]
    url_candidate = last_part.strip("'")
    if is_valid_url(url_candidate):
        url = url_candidate
    return " ".join(parts[:-1]),url

