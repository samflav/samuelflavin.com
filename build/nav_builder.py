from bs4 import BeautifulSoup
import copy
import os


class NavBuilder:
    commands = {}
    base_nav = None
    nav_stack = []
    nav = None
    has_changes = False

    def __init__(self, clean_nav):
        self.commands = {
            "literal-both": self.literal_both,
            "literal-desktop": self.literal_desktop,
            "literal-mobile": self.literal_mobile
            #TODO(more hehe)
        }

        self.base_nav = clean_nav
        self.nav = clean_nav


    def rebase(self, source_dir):
        self.nav_stack = []
        self.has_changes = False
        self.nav = self.base_nav
        #XXX: sketch idk how this would interact with file names TODO(make path split method)
        # self.nav_stack.append((os.path.normpath(source_dir).split(os.sep)[-1], self.base_nav))

    def handle_nav(self, navlinks_file):
        self.has_changes = True

        bot_dir, nav_soup = self.find_current_nav(os.path.split(navlinks_file)[0])

        with open(navlinks_file, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break

                if line.startswith("$.>"):
                    command = line[3:]

                    self.nav = self.commands[command.strip()](f, copy.copy(nav_soup))

        self.nav_stack.append((bot_dir, self.nav))

    def find_current_nav(self, src_dir, assign=False):
        if not self.has_changes:
            return None, None

        # XXX: again, but this time in reverse. This assumes a file name TODO()
        path = os.path.normpath(src_dir).split(os.sep)
        bot_dir = path[-1]

        #NOT TODO(N^2 is for the coolest of coolios)
        found = False
        for directory in reversed(path):
            if found:
                break

            for idx, item in reversed(list(enumerate(self.nav_stack))):
                if item[0] == directory:
                    nav_soup = item[1]
                    found = True
                    self.nav_stack = self.nav_stack[:idx]
                    break
        else:
            nav_soup = self.base_nav

        self.nav = nav_soup if not assign else self.nav
        return bot_dir, nav_soup


    #TODO(error handling low importance)
    @staticmethod
    def literal_desktop(file_handle, nav_soup):
        soup = NavBuilder.get_soup_from_literal(file_handle)

        nav_soup.find(id="desktop-nav-entrypoint").insert_before(soup)
        return nav_soup

    @staticmethod
    def literal_mobile(file_handle, nav_soup):
        soup = NavBuilder.get_soup_from_literal(file_handle)

        nav_soup.find(id="mobile-nav-entrypoint").insert_before(soup)
        return nav_soup

    @staticmethod
    def literal_both(file_handle, nav_soup):
        soup = NavBuilder.get_soup_from_literal(file_handle)

        nav_soup.find(id="desktop-nav-entrypoint").insert_before(copy.copy(soup))
        nav_soup.find(id="mobile-nav-entrypoint").insert_before(soup)
        return nav_soup


    @staticmethod
    def get_soup_from_literal(file_handle):
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

        return BeautifulSoup(html, 'html.parser')