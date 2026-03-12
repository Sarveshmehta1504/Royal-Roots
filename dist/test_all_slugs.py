import requests

def test():
    base = "http://localhost:8000"
    res = requests.get(f"{base}/api/blogs")
    if not res.ok:
        print("Failed to fetch blog list")
        return
    blogs = res.json()
    print(f"Testing {len(blogs)} blogs...")
    for b in blogs:
        slug = b['slug']
        curl_cmd = f"curl -s -o /dev/null -w '%{{http_code}}' {base}/api/blogs/{slug}"
        import subprocess
        status = subprocess.check_output(curl_cmd, shell=True).decode().strip()
        print(f"Slug: {slug:50} Status: {status}")
        if status != '200':
            print(f"ERROR: slug {slug} failed")

test()
