import os
import shutil
import copy

from bs4 import BeautifulSoup
import requests

from nav_builder import NavBuilder

class Builder:

    base_site = ""

    build_order = []

    handlers = {}
    replacements = {}

    nav_builder = None

    def __init__(self, wd, base_site, build_order):
        self.base_site = base_site

        self.src = os.path.join(wd, 'src')
        self.target = os.path.join(wd, 'target')

        self.build_order = build_order

        #preload nav (It's a surprise tool that will help us later)
        self.nav_builder = NavBuilder(BeautifulSoup(requests.get("https://assets.samuelflavin.com/html_part/nav.html").text, 'html.parser'))

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
                self.default(build_target["source_dir"], build_target["target_dir"], build_target["follow_dirs"], [])

    #TODO(recursion would be gooder for the nav)
    #Nav changes like [[html of change, target (mobile or desktop or both)], ["<li>...</li>", "mobile"]]
    def default(self, src_dir, target_dir, follow_dirs, nav_changes):
        os.makedirs(os.path.join(target_dir), exist_ok=True)
        self.handle_files(src_dir, target_dir, os.listdir(src_dir), nav_changes)
        curr_cng_idx = len(nav_changes)

        if follow_dirs:
            for directory in os.listdir(src_dir):
                if os.path.isdir(os.path.join(src_dir, directory)):
                    nav_changes = nav_changes[:curr_cng_idx]
                    self.default(os.path.join(src_dir, directory), os.path.join(target_dir, directory), follow_dirs, nav_changes)




    def handle_files(self, src_dir, target_dir, files, nav_changes):
        if ".navlinks" in files:
            nav_changes.extend(self.nav_builder.get_changes_from_file(os.path.join(src_dir, ".navlinks")))
            files.remove(".navlinks")

        self.nav_builder.apply_changes(nav_changes)

        for file in files:
            if not os.path.isfile(os.path.join(src_dir, file)):
                continue

            if file.endswith(".html"):
                self.copy_html(os.path.join(src_dir, file), os.path.join(target_dir, file))
            else:
                shutil.copy2(str(os.path.join(src_dir, file)), str(os.path.join(target_dir, file)))


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
        #update replacements with current nav
        self.replacements["https://assets.samuelflavin.com/html_part/nav.html"] = self.nav_builder.nav

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