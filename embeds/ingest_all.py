import time
from sitemap_crawler import crawl_via_sitemaps
import db_store  

SLEEP_BETWEEN_URLS = 0.1

def ingest_site(base_url: str):
    print(f"[INGEST] Starting sitemap-based ingestion for: {base_url}")
    urls = crawl_via_sitemaps(base_url)
    print(f"[INGEST] URLs found: {len(urls)}")
    total_urls = 0
    for url in urls:
        try:
            print(f"[PROCESS] {url}")
            db_store.store_chunks(url)
            total_urls += 1
        except Exception as e:
            print(f"[ERROR] Failed to process {url}: {e}")
        time.sleep(SLEEP_BETWEEN_URLS)
    print(f"[DONE] Processed {total_urls} URLs from {base_url}")

if __name__ == "__main__":
    #ingest_site("https://www.metropolia.fi")
    ingest_site("https://opinto-opas.metropolia.fi")
    # Close DB connection
    db_store.cur.close()
    db_store.conn.close()
