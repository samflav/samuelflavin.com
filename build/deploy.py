import os
import paramiko

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
                sftp.mkdir(os.path.join(target, directory).replace("\\","/"))
            except IOError:
                pass

        for file in files:
            sftp.put(os.path.join(root, file), os.path.join(target, str(rel_path), file).replace("\\","/"))


def deploy(base_site, key_path, deploy_order):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    site = base_site[8:] if base_site.startswith("https://") else base_site

    ssh.connect(hostname=site, username="delta", port=22, key_filename=key_path)
    sftp = ssh.open_sftp()

    for row in deploy_order:
        deploy_target = parse_build_order(row)
        if deploy_target["other_site"] is not None or not deploy_target["enabled"] :
            #TODO(enable other sites)
            continue

        if deploy_target["follow_dirs"]:
            sftp_walk(deploy_target["local_dir"], deploy_target["remote_dir"], sftp)
        else:
            sftp_files(deploy_target["local_dir"], deploy_target["remote_dir"], sftp)


def parse_build_order(row):
    return {
        "local_dir": row[0],
        "remote_dir": row[1],
        "follow_dirs": row[2],
        "enabled": row[3],
        "other_site": row[4]
    }