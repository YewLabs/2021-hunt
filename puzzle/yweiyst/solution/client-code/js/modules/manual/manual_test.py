import random, subprocess, sys
import os.path

SERVER_REPO = "../../../../../../../../ktane-server"
MANUAL_TEST = os.path.join(SERVER_REPO, "manual/test.py")

if len(sys.argv) == 1:
    while True:
        seed = random.randint(0, 1 << 31)
        print(seed)
        subprocess.run(["python3", MANUAL_TEST, str(seed)])
        subprocess.run(["node", "test.js"])

seed = sys.argv[1]
subprocess.run(["python3", MANUAL_TEST, str(seed)])
subprocess.run(["node", "test.js"])
