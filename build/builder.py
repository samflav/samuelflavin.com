import os
import shutil

from bs4 import BeautifulSoup
import requests

class Builder:

    src = ""
    target = ""
    base_site = ""

    handlers = {}
    replacements = {}

    def __init__(self, wd, base_site):
        self.base_site = base_site

        self.src = os.path.join(wd, 'src')
        self.target = os.path.join(wd, 'target')

        os.makedirs(self.target, exist_ok=True)

        self.handlers = {
            'partial_html': self.partial_html
        }

    def build(self):
        for key, value in self.handlers.items():
            if os.path.exists(os.path.join(self.src, key)):
                os.chdir(os.path.join(self.src, key))
                value()

        os.chdir(self.src)

        for root, dirs, files in os.walk(self.src):
            rel_path = os.path.relpath(root, self.src)

            if rel_path in self.handlers.keys():
                continue

            os.chdir(os.path.join(root))
            self.default(os.path.join(self.target, rel_path))


    def default(self, target_dir):
        os.makedirs(target_dir, exist_ok=True)
        for file in os.listdir():
            if not os.path.isfile(file):
                continue

            if file.endswith(".html"):
                self.copy_html(file, os.path.join(target_dir, file))
            else:
                shutil.copy2(file, os.path.join(target_dir, file))

    def partial_html(self, target_dir=""):
        for file in os.listdir():
            if os.path.isfile(file):
                with open(file) as f:
                    self.replacements[file] = BeautifulSoup(f.read(), 'html.parser')

    def copy_html(self, source, dest):
        with open(source, 'r', encoding='utf-8') as src, open(dest, 'w', encoding='utf-8') as dst:
            data = BeautifulSoup(src.read(), 'html.parser')
            for replacement in data.findAll("meta", class_="replace"):
                file = replacement["content"]
                replacement.replace_with(self.get_replacement(file))

            for replacement in data.findAll("div", class_="replace"):
                file = replacement.string
                replacement.replace_with(self.get_replacement(file))

            self.clean_links(data)
            dst.writelines(str(data))


    def get_replacement(self, file):
        #TODO(caching)
        if file.startswith("https://"):
            # if file in self.replacements.keys():
            #     soup = self.replacements[file]
            # else:
            #     soup = BeautifulSoup(requests.get(file).text, 'html.parser')
            #     self.replacements[file] = soup
            soup = BeautifulSoup(requests.get(file).text, 'html.parser')
            self.replacements[file] = soup
        else:
            soup = self.replacements[file]

        return soup

    def clean_links(self, soup):
        try:
            base_url = soup.find("base")["href"]

        except:
            base_url = self.base_site


        for link in soup.findAll("a"):
            if link["href"].startswith(base_url):
                link["href"] = link["href"][len(base_url):]

    #TODO(generate cards dynamically)
    #TODO(generate nav links)