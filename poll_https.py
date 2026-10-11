#!/usr/bin/env python3
import subprocess, sys, time, json

GH = "/Users/leo/.workbuddy/binaries/gh/bin/gh"
REPO = "leo-bone/HowToGoGlobalBetter"
MAX_RETRIES = 6
WAIT = 180  # seconds between retries

def attempt():
    payload = '{"cname":"howtogoglobalbetter.uichain.org","https_enforced":true}'
    p = subprocess.run(
        ["/bin/echo", payload, "|", GH, "api", "-X", "PUT",
         f"repos/{REPO}/pages", "--input", "-"],
        capture_output=True, text=True, shell=False
    )
    # echo piped via shell is awkward; redo with shell True for the pipe
    return p

# Use shell for the pipe
def do_put():
    cmd = (
        'echo \'{"cname":"howtogoglobalbetter.uichain.org","https_enforced":true}\''
        f' | {GH} api -X PUT repos/{REPO}/pages --input -'
    )
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

print(f"[{time.strftime('%H:%M:%S')}] Starting HTTPS-enforce polling for {REPO}", flush=True)
for i in range(1, MAX_RETRIES + 1):
    rc, out, err = do_put()
    print(f"[{time.strftime('%H:%M:%S')}] Attempt {i}/{MAX_RETRIES} -> rc={rc}", flush=True)
    print(f"    STDOUT: {out.strip()}", flush=True)
    if err.strip():
        print(f"    STDERR: {err.strip()}", flush=True)
    # Success detection
    if '"https_enforced": true' in out or '"https_enforced":true' in out:
        print("SUCCESS: https_enforced is true", flush=True)
        sys.exit(0)
    if i < MAX_RETRIES:
        # Wait only if certificate not ready
        if "certificate does not exist" in (out + err).lower() or rc == 1:
            print(f"[{time.strftime('%H:%M:%S')}] Certificate not ready. Sleeping {WAIT}s...", flush=True)
            time.sleep(WAIT)
        else:
            # unexpected error
            print("UNEXPECTED_ERROR", flush=True)
            sys.exit(2)
print("MAX_RETRIES_REACHED", flush=True)
sys.exit(3)
