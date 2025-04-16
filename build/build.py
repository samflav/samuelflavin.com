import os
from builder import Builder

BASE_SITE = "https://samuelflavin.com"

if __name__ == "__main__":
    bob = Builder(os.getcwd(), BASE_SITE)

    bob.build()