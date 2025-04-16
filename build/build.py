import os
import paramiko

from builder import Builder

BASE_SITE = "https://samuelflavin.com"
DEPLOY = True

#local dir / remote dir / follow dirs / enabled / other site

DEPLOY_ORDER = [
    ("./target/", "/var/www/home/", False, True, None)
]


def sftp_files(src, target, sftp):
    for item in os.listdir(src):
        if os.path.isfile(item):
            sftp.put(os.path.join(src, item), os.path.join(target, item))

def sftp_walk(src, target, sftp):
    for root, dirs, files in os.walk(src):
        for dir in dirs:
            try:
                sftp.mkdir(os.path.join(target, dir))
            except IOError:
                pass

def deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(hostname=BASE_SITE, username="delta", port=22)
    sftp = ssh.open_sftp()

    for target in DEPLOY_ORDER:
        if target[4] is not None or not target[3] :
            #TODO(enable other sites)
            continue

        if target[2]:
            sftp_files(target[0], target[1], sftp)


def

if __name__ == "__main__":
    bob = Builder(os.getcwd(), BASE_SITE)

    bob.build()

    if DEPLOY:
        deploy()
