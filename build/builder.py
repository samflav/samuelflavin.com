import os
import shutil
from bs4 import BeautifulSoup

class Builder:

    src = ""
    target = ""

    handlers = {}
    replacements = {}

    def __init__(self, wd):
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
                new_val = self.replacements[replacement["content"]]
                replacement.replace_with(new_val)

            for replacement in data.findAll("div", class_="replace"):
                new_val = self.replacements[replacement.string]
                replacement.replace_with(new_val)

            dst.writelines(data.prettify())
            # for line in src.readlines():
            #     if "class=\"replace\"" in line:
            #         start = line.find('>') + 1
            #         end = line.rfind('<')
            #
            #         if start != -1 and end != -1:
            #             dst.write(self.replacements[line[start:end]])
            #     else:
            #         dst.write(line)