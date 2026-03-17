import subprocess


def main():
    subprocess.run(["poetry", "publish", "--build"], check=True)
