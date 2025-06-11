import subprocess

args = "for i in {1..10}; do python3 print.py; done;"

print(subprocess.run(args, capture_output=True, text=True, shell=True))