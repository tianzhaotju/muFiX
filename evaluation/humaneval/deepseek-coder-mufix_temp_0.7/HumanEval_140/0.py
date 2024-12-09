def fix_spaces(text):
    text = text.replace('  ', '-')
    text = text.replace(' ', '_')
    if text[0] == '_':
        text = text[1:]
    return text