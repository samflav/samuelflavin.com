import os
import shutil
from builder import Builder

if __name__ == "__main__":
    bob = Builder(os.getcwd())

    bob.build()