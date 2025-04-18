import os
import shutil
import copy

from bs4 import BeautifulSoup
import requests

class Builder:

    base_site = ""

    build_order = []

    handlers = {}
    replacements = {}

    def __init__(self, wd, base_site, build_order):
        self.base_site = base_site

        self.src = os.path.join(wd, 'src')
        self.target = os.path.join(wd, 'target')

        self.build_order = build_order

        os.makedirs(self.target, exist_ok=True)

        self.handlers = {
            './src/partial_html': self.partial_html
        }


    def build(self):
        for row in self.build_order:
            build_target = Builder.parse_build_order(row)
            if not build_target["enabled"]:
                continue

            if build_target["source_dir"] in self.handlers.keys():
                self.handlers[build_target["source_dir"]](build_target["source_dir"], build_target["target_dir"], build_target["follow_dirs"])
            else:
                self.default(build_target["source_dir"], build_target["target_dir"], build_target["follow_dirs"])


    def default(self, src_dir, target_dir, follow_dirs):
        if follow_dirs:
            for root, dirs, files in os.walk(src_dir):
                rel_path = os.path.relpath(root, src_dir)
                for directory in dirs:
                    os.makedirs(os.path.join(target_dir, directory), exist_ok=True)

                for file in files:
                    if file.endswith(".html"):
                        self.copy_html(os.path.join(root, file), os.path.join(target_dir, str(rel_path), file))
                    else:
                        shutil.copy2(str(os.path.join(root, file)), str(os.path.join(target_dir, str(rel_path), file)))
        else:
            os.makedirs(os.path.join(target_dir), exist_ok=True)
            for file in os.listdir(src_dir):
                if not os.path.isfile(os.path.join(src_dir, file)):
                    continue

                if file.endswith(".html"):
                    self.copy_html(os.path.join(src_dir, file), os.path.join(target_dir, file))
                else:
                    shutil.copy2(os.path.join(src_dir, file), os.path.join(target_dir, file))


    def partial_html(self, src_dir, target_dir="", follow_dirs=False):
        for file in os.listdir(src_dir):
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
        if file.startswith("https://"):
            if file in self.replacements.keys():
                soup = self.replacements[file]
            else:
                soup = BeautifulSoup(requests.get(file).text, 'html.parser')
                self.replacements[file] = soup
        else:
            soup = self.replacements[file]

        return copy.copy(soup)


    def clean_links(self, soup):
        try:
            base_url = soup.find("base")["href"]

        except:
            base_url = self.base_site


        for link in soup.findAll("a"):
            if link["href"].startswith(base_url):
                link["href"] = link["href"][len(base_url):]


    @staticmethod
    def parse_build_order(row):
        return {
            "source_dir": row[0],
            "target_dir": row[1],
            "follow_dirs": row[2],
            "enabled": row[3]
        }

    #TODO(generate cards dynamically)
    #TODO(generate nav links)