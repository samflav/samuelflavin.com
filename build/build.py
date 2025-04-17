import os
import paramiko

from builder import Builder
from hidden import KEY_PATH

BASE_SITE = "https://samuelflavin.com"
DEPLOY = True

#local dir / remote dir / follow dirs / enabled / other site
DEPLOY_ORDER = [
    ("./target/", "/var/www/home/", False, True, None),
    ("./target/pt/", "/var/www/pt/", True, True, None)
]


def sftp_files(src, target, sftp):
    for item in os.listdir(src):
        file = os.path.join(src, item)
        if os.path.isfile(file):
            sftp.put(file, os.path.join(target, item))

def sftp_walk(src, target, sftp):
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        for directory in dirs:
            try:
                sftp.mkdir(os.path.join(target, directory))
            except IOError:
                pass

        for file in files:
            sftp.put(os.path.join(root, file), os.path.join(target, str(rel_path), file).replace("\\","/"))



def deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    site = BASE_SITE[8:] if BASE_SITE.startswith("https://") else BASE_SITE

    ssh.connect(hostname=site, username="delta", port=22, key_filename=KEY_PATH)
    sftp = ssh.open_sftp()

    for target in DEPLOY_ORDER:
        if target[4] is not None or not target[3] :
            #TODO(enable other sites)
            continue

        if target[2]:
            sftp_walk(target[0], target[1], sftp)
        else:
            sftp_files(target[0], target[1], sftp)


if __name__ == "__main__":
    base_dir = os.getcwd()
    bob = Builder(base_dir, BASE_SITE)

    bob.build()

    os.chdir(base_dir)

    if DEPLOY:
        deploy()
