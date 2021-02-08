def sanitize(text):
    """Remove all newlines and >1 spaces in a line of text"""
    return " ".join(text.replace("\xa0", " ").replace("&nbsp", "").split())