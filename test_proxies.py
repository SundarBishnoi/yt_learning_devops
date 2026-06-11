import requests
import concurrent.futures

# Read the downloaded proxies
with open("proxies.txt", "r") as f:
    raw_proxies = [line.strip() for line in f if line.strip()]

working_proxies = []

def check_proxy(proxy):
    proxy_dict = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    try:
        # Test connection against a basic IP check endpoint with a strict timeout
        response = requests.get("https://ipify.org", proxies=proxy_dict, timeout=3)
        if response.status_code == 200:
            print(f"[SUCCESS] Active Proxy: {proxy}")
            return proxy
    except Exception:
        pass
    return None

print(f"Testing {len(raw_proxies)} free proxies concurrently...")

# Use multi-threading to check all proxies in a few seconds
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    results = executor.map(check_proxy, raw_proxies)
    for res in results:
        if res:
            working_proxies.append(f"http://{res}")

print(f"\nFound {len(working_proxies)} working proxies!")
print("Add these directly to your run_scraper.py script:")
print(working_proxies[:5])  # Show top 5 working proxies
