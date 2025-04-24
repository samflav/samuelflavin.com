from bs4 import BeautifulSoup
import copy

class NavBuilder:
    commands = {}
    base_nav = None
    nav = None


    def __init__(self, clean_nav):
        self.commands = {
            "literal-both": self.literal_both,
            "literal-desktop": self.literal_desktop,
            "literal-mobile": self.literal_mobile
            #TODO(more hehe, list dir, etc)
        }

        self.base_nav = clean_nav
        self.nav = clean_nav


    def get_changes_from_file(self, file):
        changes = []
        with open(file, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break

                if line.startswith("$.>"):
                    command = line[3:]

                    changes.extend(self.commands[command.strip()](f))

        return changes


    def apply_changes(self, changes):
        #naive approach for now, write all changes every time TODO(cache changes and only write if necessary, more 2 come)
        self.nav = copy.copy(self.base_nav)

        for change in changes:
            if change[1] == "both" or change[1] == "desktop":
                self.nav.find(id="desktop-nav-entrypoint").insert_before(BeautifulSoup(change[0], 'html.parser'))

            if change[1] == "both" or change[1] == "mobile":
                self.nav.find(id="mobile-nav-entrypoint").insert_before(BeautifulSoup(change[0], 'html.parser'))




    #TODO(error handling low importance)
    @staticmethod
    def literal_desktop(file_handle):
        return [[NavBuilder.get_html_from_literal(file_handle), "desktop"]]


    @staticmethod
    def literal_mobile(file_handle):
        return[[NavBuilder.get_html_from_literal(file_handle), "mobile"]]

    @staticmethod
    def literal_both(file_handle):
        return [[NavBuilder.get_html_from_literal(file_handle), "both"]]

    @staticmethod
    def get_html_from_literal(file_handle):
        html = ""
        while True:
            pos = file_handle.tell()
            line = file_handle.readline()
            if line.startswith("$.>"):
                file_handle.seek(pos)
                break
            elif not line:
                break
            else:
                html += line

        return html