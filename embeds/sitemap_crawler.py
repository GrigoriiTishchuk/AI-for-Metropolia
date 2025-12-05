from usp.tree import sitemap_tree_for_homepage
from urllib.robotparser import RobotFileParser

# Helper to load and parse robots.txt to avoid disallowed URLs
def get_robots_parser(base_url: str):
    rp = RobotFileParser()
    rp.set_url(base_url.rstrip("/") + "/robots.txt")
    rp.read()
    return rp
"""
    Crawl site using Ultimate Sitemap Parser.
    - Automatically finds all sitemaps
    - Automatically parses nested sitemaps
    - Extracts all URLs
    - Filters by robots.txt rules
"""
def crawl_via_sitemaps(base_url: str) -> list[str]:
    print(f"Crawling sitemaps for: {base_url}")
    rp = get_robots_parser(base_url)
    tree = sitemap_tree_for_homepage(base_url)
    if not tree:
        print("No sitemap detected!")
        return []
    print("Sitemaps discovered:")
    for sm in tree.sub_sitemaps:
        print("  -", sm.url)
    # extract all URLs in all nested sitemaps
    urls = []
    for page in tree.all_pages():
        urls.append(page.url)
    urls = list(set(urls))  # remove duplicates by using set
    print(f"Found total URLs in sitemap(s): {len(urls)}")
    # filter by robots.txt rules
    allowed_urls = [u for u in urls if rp.can_fetch("*", u)]
    print(f"Allowed URLs after robots.txt: {len(allowed_urls)}")
    return allowed_urls
