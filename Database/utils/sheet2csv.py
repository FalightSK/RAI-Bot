import re

def convert_google_sheet_url(url):
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'
    new_url = re.sub(pattern, replacement, url)

    return new_url

if __name__ == '__main__':
    print(convert_google_sheet_url("https://docs.google.com/spreadsheets/d/10rkm7hEIX8-zPhP0oITTGZExY03COKdBNN96pRFQiPE/edit?usp=sharing"))