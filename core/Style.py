def StylePage(page='index.css'):
    yield "<style>"
    yield open(f"core\\looks\\{page}","r").read()
    yield "</style>"