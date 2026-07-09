QUOTE_WRAPPERS = "\"“”"


def normalize_quote_text(text):
    if text is None:
        return ""

    return text.strip().strip(QUOTE_WRAPPERS).strip()


def has_curly_quote_wrapping(text):
    return text.startswith("“") and text.endswith("”")
