import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse
from time import sleep

BASE_URL = "https://www.mosdac.gov.in/"
LOGIN_URL = "https://www.mosdac.gov.in/user/login"  # adjust if needed
HEADERS = {"User-Agent": "Mozilla/5.0"}
LOGIN_PAYLOAD = {
    "name": "adi1472",
    "pass": "Different@123",
    "form_id": "user_login_form"
}

OUTPUT_FILE = "output.json"
ALLOWED_FILE_EXTS = [".pdf", ".docx", ".xlsx", ".xls", ".csv"]

visited = set()
results = []
session = requests.Session()


def login_to_site():
    try:
        print("🔐 Attempting login...")
        res = session.get(LOGIN_URL, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")

        # Get login form tokens if needed
        token_input = soup.find("input", {"name": "form_build_id"})
        if token_input:
            try:
                LOGIN_PAYLOAD["form_build_id"] = str(token_input["value"])  # type: ignore
            except:
                pass

        login_res = session.post(LOGIN_URL, headers=HEADERS, data=LOGIN_PAYLOAD)
        if "logout" in login_res.text.lower():
            print("✅ Login successful")
        else:
            print("❌ Login failed. Check credentials or login URL.")
    except Exception as e:
        print("❌ Login error:", e)


def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.netloc and parsed.scheme and BASE_URL in url


def extract_links(soup, base_url):
    links = set()
    for a in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a['href'])
        if is_valid_url(full_url):
            links.add(full_url)
    return links


def extract_content(url):
    try:
        res = session.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 40]

        # Filter images with full src
        images = [urljoin(url, img['src']) for img in soup.find_all("img", src=True)]  # type: ignore

        # Look for files by extension
        files = [
            urljoin(url, a['href']) for a in soup.find_all("a", href=True)  # type: ignore
            if any(a['href'].lower().endswith(ext) for ext in ALLOWED_FILE_EXTS)  # type: ignore
        ]

        return {
            "url": url,
            "title": title,
            "headings": headings,
            "description": paragraphs,
            "images": images,
            "files": files
        }
    except Exception as e:
        print(f"⚠️ Error extracting from {url}: {e}")
        return None


def scrape_site(start_url, max_depth=2, delay=1.5):
    global visited, results
    to_visit = {start_url}

    for depth in range(max_depth):
        print(f"\n🌍 Depth {depth + 1} - URLs to visit: {len(to_visit)}")
        current_layer = list(to_visit)
        to_visit = set()

        for url in current_layer:
            if url in visited:
                continue

            visited.add(url)
            print(f"🔎 Visiting: {url}")
            sleep(delay)

            try:
                res = session.get(url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(res.text, "html.parser")

                data = extract_content(url)
                if data:
                    results.append(data)

                new_links = extract_links(soup, url)
                to_visit.update(new_links)
            except Exception as e:
                print(f"❌ Skipping {url}: {e}")
                continue

    return results


if __name__ == "__main__":
    print("🚀 Starting optimized MOSDAC scraper...")
    login_to_site()

    all_data = scrape_site(BASE_URL, max_depth=3)

    out_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraping complete. {len(all_data)} pages saved to {OUTPUT_FILE}")
