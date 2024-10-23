def update_link(link: str, name: str = "link"):
    with open(f"Database/utils/{name}.txt", "w") as txt:
        txt.write(link)

def get_link(name: str = "link"):
    with open(f"Database/utils/{name}.txt", "r") as txt:
        return str(txt.read())