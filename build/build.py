import sys
import os

from builder import Builder
from deploy import deploy
from hidden import KEY_PATH

BASE_SITE = "https://samuelflavin.com"
BUILD = sys.argv[1] == 'True'
DEPLOY = sys.argv[2] == 'True'

#source dir / target dir / follow dirs / enabled
BUILD_ORDER = [
    ("./src/partial_html", "", False, True),
    ("./src/", "./target/", False, True),
    ("./src/pt/", "./target/pt/", True, True),
    ("./src/zynnamon/", "./target/zynnamon/", True, True)
]

#local dir / remote dir / follow dirs / enabled / other site
DEPLOY_ORDER = [
    ("./src/partial_html", "/var/www/assets/html_part/", True, True, None),
    ("./target/", "/var/www/home/", False, True, None),
    ("./target/pt/", "/var/www/pt/", True, True, None),
    ("./target/zynnamon/", "/var/www/cinnamon", True, True, None)
]

if __name__ == "__main__":
    base_dir = os.getcwd()

    if BUILD:
        bob = Builder(base_dir, BASE_SITE, BUILD_ORDER)
        bob.build()

    os.chdir(base_dir)

    if DEPLOY:
        deploy(BASE_SITE, KEY_PATH, DEPLOY_ORDER)
