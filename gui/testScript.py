import subprocess
import sys

def run_script(script_path):
    process = subprocess.Popen(
        ['bash', script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=5
    )

    print("stderr:       ")
    for line in process.stderr:
        print(line, end='')

    # Print stdout and stderr in real-time
    print("stdout:       ")
    for line in process.stdout:
        print(line, end='')
    process.stdout.close()
    process.stderr.close()
    process.wait()

def run2(script_path):
    process = subprocess.run(
        ['bash', script_path],
        capture_output=True
    )

    print("stderr:       ")
    for line in process.stderr:
        print(line, end='')

    print(subprocess.check_output(["bash", script_path]))
    # Print stdout and stderr in real-time
    print("stdout:       ")
    for line in process.stdout:
        print(line, end='')
    process.stdout.close()
    process.stderr.close()
    process.wait()

def git_clone(repo_url):
    process = subprocess.Popen(
        ['git', 'clone', repo_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )

    # Print stdout and stderr in real-time
    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()

    for line in process.stderr:
        sys.stdout.write(line)
        sys.stdout.flush()

    process.stdout.close()
    process.stderr.close()
    process.wait() 

if __name__ == "__main__":
    # script_path = '/home/xmmgr/Documents/installWizard/trexinstaller/gui/testScript.sh'
    # run_script(script_path)
    repo_url = "https://bitbucket.parsons.us/scm/trex/launch.git"
    git_clone(repo_url)