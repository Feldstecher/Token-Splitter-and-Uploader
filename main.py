import os
import json
import shutil
import paramiko

def remove_subdirs():
    for d in os.listdir('.'):
        if os.path.isdir(d):
            try:
                shutil.rmtree(d)
                print(f"Directory '{d}' removed successfully.")
            except OSError as e:
                print(f"Error removing directory '{d}': {e}")
    print("Subdirectories removed.")

def create_subdirs():
    with open('servers.json', 'r') as servers:
        server_list = json.load(servers)
    for server in server_list:
        os.mkdir(server)
    print("Subdirectories created.")

def split_into_subdirs():
    subdirectories = [d for d in os.listdir() if os.path.isdir(d)]

    with open('total_tokens.txt', 'r') as source:
        source_content = source.readlines()

    lines_per_file = len(source_content) // len(subdirectories)
    remaining_lines = len(source_content) % len(subdirectories)

    for directory in subdirectories:
        tokens_file = os.path.join(directory, "tokens.txt")
        with open(tokens_file, 'w') as target:
            for _ in range(lines_per_file):
                target.write(source_content.pop(0))
            if remaining_lines > 0:
                target.write(source_content.pop(0))
                remaining_lines -= 1

    print("Tokens split into subdirectories.")


def upload_to_servers():
    subdirectories = [d for d in os.listdir() if os.path.isdir(d)]

    with open('servers.json', 'r') as servers_file:
        server_list = json.load(servers_file)

    for name, server in server_list.items():
        for directory in subdirectories:
            if directory == name:
                tokens_file = os.path.join(directory, "tokens.txt")
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print(f"Trying to upload to {server['ip']} ({name})")
                try:
                    ssh.connect(server['ip'], port=22, username=server['username'], password=server['password'], allow_agent=False, look_for_keys=False)
                    sftp = ssh.open_sftp()
                    sftp.put(tokens_file, f"{server['path_to_executable_folder']}tokens.txt")
                except Exception as e:
                    print(f"Error uploading tokens to {server['ip']}: {e}")
                finally:
                    sftp.close()
                    ssh.close()
                    print(f"Tokens uploaded to {server['ip']} ({name})")           

if __name__ == "__main__":
    remove_subdirs()
    create_subdirs()
    split_into_subdirs()
    upload_to_servers()
