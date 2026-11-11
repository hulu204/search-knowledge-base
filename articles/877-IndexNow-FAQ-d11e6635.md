---
title: 'IndexNow FAQ'
company: IndexNow
tag: 爬虫抓取
date: 2026-01-01
url: https://www.indexnow.org/faq
account: 
origin: harvest2-202607
---
# FAQ

## Setup and Installation

---

How Do I Start Using IndexNow?

To get started with IndexNow, check whether your Content Management System (CMS), hosting provider, or SEO plugin already supports it. Many platforms offer built-in support or compatible add-ons, so you may not need to configure it manually.

If your platform doesn't support IndexNow, you can implement it manually by generating a key file, verifying your website, and submitting URLs using the IndexNow API.

Check your CMS documentation or plugin library first before setting up IndexNow manually.

Which content management systems support IndexNow?

The following CMS' offer native IndexNow integration or support it through SEO plugins or extensions:

* **WordPress**
* **Shopify**
* **Wix**
* **GoDaddy**
* **Duda**
* **XenForo**
* **Milestone**
* **Joomla!**
* **Drupal**
* **Bitrix24**
* **PrestaShop**
* **MODX**
* **Shopware**
* **OpenCart**
* **Typo3**
* **Umbraco**

Other content management systems may support IndexNow natively through third-party plugins or extensions available in their plugin libraries. Check with your CMS or hosting provider for details on how to enable IndexNow for your website.

Which Content Delivery Networks support IndexNow?

Cloudflare offers native IndexNow integration. However, this list is not exhaustive. Please check with your provider for specific instructions on enabling IndexNow for your website.

Why should I use IndexNow instead of relying on search engine crawlers?

Traditional search engines rely on web crawlers to discover content updates, but that process can be slow, taking days or even weeks. IndexNow lets you submit URLs immediately when content is added, updated, or deleted.

This improves your site's indexing speed with supported search engines and helps keep your content current in AI-powered search results. Faster indexing can lead to better visibility and more timely inclusion in search results, which may support improved SEO performance.

When should I notify search engines using IndexNow?

Websites should notify IndexNow whenever content is **added, updated, or removed**, so search engines can reflect the latest version in their index.

Typical cases include:

* **New content:** product pages, videos, travel listings, job postings, blog posts, or event announcements.
* **Updated content:** product descriptions, video titles/metadata, destination guides, company profiles, or policy pages.
* **Price or availability changes:** inventory status, promotions, or expired offers.
* **User-generated content:** new reviews, comments, or forum posts (submitted incrementally to avoid over-notifying, e.g., each review from 1-20, then every 5 up to 100, every 10 up to 1000).
* **Removed content:** deleted products, videos, travel deals, or expired events.

By notifying IndexNow at these points, you help search engines index the correct version of your site faster and more efficiently.

## API Key and Verification

---

How do I generate an IndexNow API key?

When your CMS, hosting provider, or SEO plugin supports IndexNow, you don't need a key file. Submissions are handled automatically.

For manual setup, you'll need to create an API key. This key proves ownership of your domain and authenticates your submissions so search engines know they're coming from an authorized source.

**Steps to generate your API key**

**1. Generate a key string**

* Use a GUID/UUID generator or command-line tool.
* Your key must be **8 to 128 characters** long.
* Allowed characters: lowercase (a to z), uppercase (A to Z), numbers (0 to 9), and hyphens (-).

**2. Create the key file**

* Open a text editor or code editor (e.g., Notepad, TextEdit, VS Code).
* Paste your API key into the file.
* Save the file in UTF-8 encoding with the key as the filename, followed by .txt.
* Example if your key is abcd1234, create a file named abcd1234.txt with the contents abcd1234

**3. Upload the file**

* Place the key file in the root directory of your site, or any publicly accessible folder on the same host (no login required).
* Confirm it's accessible at a public URL, such as: `https://yourdomain.com/{your-key}.txt`
* *Example:* If your domain is yourdomain.com and your key is I-love-IndexNow-3000, the file should be at `https://yourdomain.com/I-love-IndexNow-3000.txt`.
* Alternatively, you may use another public location, e.g. `https://yourdomain.com/keys/well-known.txt`. If you use a non-root location, specify the key file location using the `keyLocation` parameter when submitting URLs.

How do I verify ownership of my website for IndexNow?

After generating your key file, upload it to one of these locations:

* The **root directory** of your website (preferred).
* Or, if root access isn't possible, a **publicly accessible folder** on your hosting provider (no login required).

Then, open the file's URL in a browser:  
**https://yourdomain.com/{your-key}.txt**

If the file loads and displays only your key, your site is verified. Search engines use this file to confirm domain ownership before accepting IndexNow submissions. If verification fails, review the **Troubleshooting** section below for common fixes.

How do I update or rotate my IndexNow API key?

You can rotate your IndexNow API key without disrupting service by following these steps:

**Generate a new key** using the same method you used originally (manual or tool-based).

* **Replace the old key file** in the root directory with the new {key}.txt file.
* **Begin submitting URLs using the new key.** This automatically prompts search engines to verify the new key during the next submission.

Search engines will automatically re-verify ownership when the updated key is detected during URL submission.

## URL Submission

---

How Do I Submit a URL Using IndexNow?

You can notify search engines instantly when you add, update, or delete content by submitting a URL to the IndexNow API.

**1. Format the request URL:**

You may submit your request to only one of the following participating endpoints.  
Each endpoint sends your submission directly to its respective search engine, and your submission will be shared across all IndexNow-enabled search engines:

* **IndexNow global endpoint:** `https://api.indexnow.org/indexnow?url={your-added-or-updated-or-deleted-url}&key={your-key}`
* **Amazon:** `https://indexnow.amazonbot.amazon/indexnow?url={your-url}&key={your-key}`
* **Bing:** `https://www.bing.com/indexnow?url={your-url}&key={your-key}`
* **Naver:** `https://searchadvisor.naver.com/indexnow?url={your-url}&key={your-key}`
* **Seznam.cz:** `https://search.seznam.cz/indexnow?url={your-url}&key={your-key}`
* **Yandex:** `https://yandex.com/indexnow?url={your-url}&key={your-key}`
* **Yep:** `https://indexnow.yep.com/indexnow?url={your-url}&key={your-key}`

**2.** Replace `{your-url}` with the full URL of the page you've added, updated or deleted and `{your-key}` with your verified IndexNow API key.

**3.** Submit the request using a browser, script, or HTTP client.

**4. Confirm the submission was successful:**

* If you receive an **HTTP 200** response, your submission was accepted and processed.
* **Note:** For your **first request**, you may receive an **HTTP 202** response. This means the URL was received, and the search engine will verify your key before indexing the content. Once verification is complete, subsequent successful submissions will typically return HTTP 200.

How do I submit multiple URLs at once using IndexNow?

IndexNow supports bulk submission of up to 10,000 URLs per POST request. This is useful when you have several updated, added, or deleted pages to notify search engines about in a single batch.

**Use this JSON format in your POST request:**

```
POST /indexnow HTTP/1.1
Host: <searchengine>
Content-Type: application/json; charset=utf-8

{
  "host": "www.example.com",
  "key": "fa8c0a469da44e9b8f6a769f291829f5",
  "urlList": [
    "https://www.example.com/url1",
    "https://www.example.com/folder/url2",
    "https://www.example.com/url3"
  ]
}
```

**Submit your POST request to:**  
`https://api.indexnow.org/indexnow`

**Things to keep in mind when submitting multiple URLs:**

* Submit no more than 10,000 URLs per request.
* Use UTF-8 encoding and set the proper Content-Type header.

What is the maximum payload size for a POST request in IndexNow?

IndexNow allows you to submit up to **10,000 URLs per POST request** in a single JSON payload. Submitting more than this may cause the request to fail or return an HTTP 422 (Unprocessable Entity) response.

To ensure successful processing, always keep your batch submissions below the 10,000-URL limit.

How do I format IndexNow notification URLs?

You can submit to any participating search engine using the following URL structure:

**`https://<searchengine>/indexnow?url={your-url}&key={your-key}`**

For example, if you are submitting to IndexNow, the URL would be:

**`https://api.indexnow.org/indexnow?url=https%3A%2F%2Fwww.example.com%2Fpage1&key=50283fcd8c764cfd9bd79a8b4002f647`**

**How to correctly format your IndexNow submission URL:**

* Replace the key parameter with your actual IndexNow API key
* Be sure to **URL-encode** the submitted page URL (e.g., %3A for : and %2F for /)

How do I encode URLs correctly for IndexNow?

IndexNow requires URLs to be encoded following [RFC-3986](https://datatracker.ietf.org/doc/html/rfc3986) standards. This ensures special characters are safely transmitted via the API.

**Common URL encoding examples:**

* `:` becomes `%3A`
* `/` becomes `%2F`
* `?` becomes `%3F`
* `=` becomes `%3D`
* `&` becomes `%26`

**Why it matters to correctly encode your IndexNow URLs:**

Correct encoding ensures that IndexNow URLs are parsed and processed properly by search engines. Failing to encode URLs may result in errors or skipped submissions.

What happens after I submit a URL using IndexNow?

After you submit a URL using IndexNow, the search engine evaluates whether it should crawl the URL based on its crawl quota, scheduling logic, and quality signals. If the page passes internal checks, it will be crawled to fetch the most recent content.

**Submitting a URL does not guarantee immediate indexing.** However, IndexNow increases the likelihood that important changes are discovered and crawled faster, helping search engines surface your content more quickly.

Does submitting URLs via IndexNow count against my crawl quota?

**Yes. Every URL submitted through IndexNow counts toward your site's crawl quota.**

However, by using IndexNow, you're signaling to search engines that these URLs are important and should be prioritized. This typically results in faster crawling of submitted URLs compared to pages that haven't been submitted.

Can I submit the same URL multiple times a day?

Avoid submitting the same URL many times a day unless there are meaningful content changes. For frequently updated pages, it is best practice to wait at least 5 minutes between updates before resubmitting.

For high-frequency updates, focus on using IndexNow only for substantial changes that affect content or structure. Submitting unnecessary updates may lead to wasted crawl quota without improving visibility.

How do I handle submissions for frequently changing content?

If your content updates often, focus IndexNow submissions on meaningful changes such as updates to page content, pricing, or availability. Avoid submitting every small layout or cosmetic change.

To handle frequent updates effectively:

* **Automate submissions** using scripts that detect real content changes.
* **Wait at least 5 minutes** before resubmitting the same URL.
* **Monitor indexing behavior** to balance content freshness with crawl efficiency.

Can I submit redirected or deleted URLs using IndexNow?

Yes. You should submit redirected URLs and pages that return HTTP 404 or HTTP 410 status codes.

**Submitting redirected or deleted URLs using IndexNow allows search engines to:**

* Update their indexes when a page is redirected using 301, 302, or meta refresh.
* Remove outdated or broken links when a page is deleted and returns a 404 or 410.
* Maintain accurate and current search results for users.

IndexNow supports submitting URLs for content that has been deleted, moved, or redirected. Including these updates helps ensure that search engines reflect the most accurate structure of your site and improve crawl efficiency.

Can I submit all my site's URLs using IndexNow?

IndexNow is intended for notifying search engines about **recently added, updated, or deleted** URLs. It is not designed for submitting every URL on your site at once.

If your entire site has been recently updated, such as after a migration or redesign, it is acceptable to submit all URLs using IndexNow. For ongoing discovery and long-term indexing, use an XML sitemap.

**To improve indexing coverage and freshness, use the following approach:**

* Use **IndexNow** to submit high priority or frequently changing pages.
* Use **sitemaps** to give search engines a complete inventory of all URLs on your website.

This combination ensures both fast content discovery and comprehensive visibility in search results.

Should I use IndexNow and sitemaps together?

Yes. Using both IndexNow and sitemaps improves content visibility and ensures broader search engine coverage.

**IndexNow improves search visibility by providing:**

* Instant notification when content is added, updated, or deleted.
* Faster discovery of important changes.
* Real-time updates for frequently changing content.

**Sitemaps enhance search coverage by providing:**

* A complete inventory of all URLs on your site.
* Discovery of pages that change infrequently or are deeper in the site structure.
* Long-term crawl support for comprehensive indexing.

Combining IndexNow and sitemaps ensures your content is both rapidly surfaced and thoroughly discovered by traditional and AI-powered search engines.

Should I submit URLs that changed before I started using IndexNow?

**No.** IndexNow is designed to notify search engines about recent additions, updates, or deletions. It is not intended for retroactive submission of older changes.

To help search engines discover previously updated pages, follow this approach:

* Use IndexNow to submit URLs that changed after IndexNow was set up.
* Use sitemaps with accurate `lastmod` values to surface content updated before implementation.
* This combination ensures both recent and historical changes are visible to search engines.

Should I use IndexNow for a small website?

**Yes.** IndexNow is beneficial even for small websites with only a few pages. It allows you to instantly notify search engines about updates, increasing the likelihood of faster crawling and indexing.

**Using IndexNow on a small site can help you:**

* Achieve faster visibility for new or updated content.
* Improve crawl efficiency by targeting changed pages.
* Control how quickly your updates appear in search results.

## Automation and Scripting

---

What are the best practices for automating IndexNow submissions?

Automation helps ensure timely URL notifications without overwhelming search engines or exceeding rate limits. The key is to detect real changes and submit only what matters.

**To automate IndexNow effectively:**

* **Use backend scripts or CMS hooks** to trigger submissions when content is added, updated, or deleted.
* **Detect and filter for meaningful updates** (e.g., price, availability, content) instead of cosmetic or layout-only changes.
* Implement debouncing logic to prevent rapid re-submissions (e.g., wait 5+ minutes between submissions for the same URL).
* **Log each submission** and monitor HTTP response codes for issues.
* **Integrate IndexNow into publishing workflows or deployment pipelines** so submissions happen automatically and reliably.

How can I automate IndexNow submissions using a script?

You can automate IndexNow submissions by creating a script that detects dynamic content changes and submits updated URLs directly to the IndexNow API. This ensures search engines are notified in real time when key content changes.  
Below is a Python example that simulates checking a content database for recently modified URLs and automatically submits them to IndexNow.

Replace the simulated content\_db dictionary with a live integration that queries your CMS, publishing platform, or backend database to detect recently updated content.

```
import requests
import time

# Configuration
API_KEY = "your-api-key"
HOST = "example.org"
KEY_LOCATION = "https://{HOST}/{API_KEY}.txt"
INDEXNOW_API_URL = "https://api.indexnow.org/indexnow"

# Simulated content database (timestamps = now - random offsets)
content_db = {
    "/product?id=101": int(time.time()) - 100,  # modified ~100s ago
    "/news?id=202": int(time.time()) - 4000,   # modified ~1h+
    "/blog?id=303": int(time.time()) - 200     # modified ~200s ago
}

def detect_dynamic_changes():
    current_time = int(time.time())
    changed_urls = []
    for url, last_modified in content_db.items():
        if current_time - last_modified < 3600:  # last hour
            changed_urls.append(f"https://{HOST}{url}")
    return changed_urls

def submit_urls(url_list):
    payload = {
        "host": HOST,
        "key": API_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": url_list
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    response = requests.post(INDEXNOW_API_URL, json=payload, headers=headers)

    if response.status_code in (200, 202):
        print("â URLs submitted successfully:", url_list)
    elif response.status_code == 429:
        print("â ï¸ Rate limited. Try again later.")
    else:
        print("â Failed:", response.status_code, response.text)

if __name__ == "__main__":
    changed_urls = detect_dynamic_changes()
    if changed_urls:
        submit_urls(changed_urls)
    else:
        print("No dynamic content changes detected.")
```

What HTTP response codes should I expect from IndexNow?

When submitting URLs, you may receive the following HTTP response codes:

* **200 OK:** The URL was received successfully.
* **202 Accepted:** Submission accepted but not yet processed.
* **400 Bad Request:** Your URL or API key may be incorrectly formatted.
* **422 Unprocessable Entity:** The server understood the request but couldn't process it.
* **429 Too Many Requests:** You've hit the rate limit. Try again later.

**Log your HTTP responses to monitor submission success and identify issues.** This helps catch problems early, especially with rate limits or formatting errors.

What logging should I set up for IndexNow submissions?

Setting up proper logging helps you monitor URL submissions and troubleshoot errors in your IndexNow integration.

**Important fields to include in your IndexNow logging system:**

* Timestamp of submission
* Full submitted URL
* HTTP response code (e.g., 200, 400, 429)
* Retry attempts or failures
* Submission method (GET or POST)
* API key used (optional if managing multiple keys)

**Why logging is important for IndexNow:**

* Helps detect submission patterns and recurring errors.
* Makes it easier to catch and fix failed submissions.
* Confirms whether URLs are accepted and indexed correctly.

How do I monitor and test IndexNow submissions?

Monitoring and testing your IndexNow implementation ensures your URLs are being submitted correctly and received by search engines.

**To monitor and test IndexNow submissions effectively:**

* Use tools like curl or wget to test URL submissions and view HTTP response codes.
* Check for successful responses (HTTP 200) or errors (e.g., 400, 429).
* Log all submissions along with timestamps and server responses.
* Review indexing reports or tools provided by search engines to track crawl behavior.

## Advanced Use Cases

---

How do I use IndexNow with multiple subdomains?

Each subdomain is treated as a separate host, which means you must create and manage individual key files for each one.

**For sites with subdomains such as:**

* blog.example.com
* shop.example.com
* support.example.com

**You should do the following for each subdomain:**

* Host its own {key}.txt file in the root directory of the subdomain.
* Submit URLs using that subdomain's unique API key.

This ensures each subdomain is independently verified and properly indexed across search engines.

How do I use IndexNow for multilingual websites?

If your website serves content in multiple languages, submit the URLs for each language version separately using IndexNow.

For example:

* `https://example.com/en/product`
* `https://example.com/fr/product`
* `https://example.com/de/product`

**How to optimize multilingual submissions for IndexNow:**

* Submit a separate URL for each language version
* Ensure each version uses canonical and hreflang tags when applicable
* URL-encode all submitted links to meet RFC-3986 standards

Using IndexNow this way helps search engines discover and crawl localized content faster.

## Troubleshooting IndexNow Issues

---

Why isn't my IndexNow key file verifying?

If your IndexNow key file is uploaded but not verifying, it usually means the file isn't named, placed, or accessible correctly.

* **File name:** The file must be named exactly as your API key, followed by .txt (for example, if your key is I-love-IndexNow-3000, name the file I-love-IndexNow-3000.txt).
* **File location:** It should be in the **root directory** of your domain (not a subfolder, unless your host requires otherwise)

Common issues to check:

* **File contents:** The text inside must exactly match your API key
* **File accessibility:** It must be reachable at **https://yourdomain.com/{your-key}.txt** without login, firewall, or IP restrictions

**How to test**

Open the file's URL in a browser. If it displays only your key as plain text, search engines can verify your site. If the file is missing, mismatched, or blocked, IndexNow submissions will not be accepted.

Why didn't my URL get indexed after submitting it to IndexNow?

Submitting a URL with IndexNow alerts search engines that content has changed, but it doesn't guarantee indexing. Reasons your URL may not be indexed include:

* Crawl quota limits for your domain.
* Low-quality, thin, or duplicate content.
* Technical issues like 404 errors, robots.txt blocks, or noindex tags.
* Indexing delays due to crawl scheduling.
* The search engine may choose not to index a URL based on its algorithms.

**Make sure** your content is high quality, internally linked, and accessible to crawlers.

Why is my IndexNow URL indexed on one search engine but not another?

Submitting a URL through IndexNow alerts all participating search engines that content has changed, but each engine makes its own decision about whether to index it.

**Reasons your URL may be indexed on one engine but not another include:**

* Differences in how each search engine evaluates content quality.
* Varying crawl budgets or URL prioritization strategies.
* Unique indexing algorithms and ranking systems.
* Timing or crawl scheduling differences between engines.

Search engines use their own criteria to determine what content appears in their results. To check if a URL is indexed, use each engine's site inspection or reporting tools.

What are the rate limits for IndexNow?

IndexNow does not publicly disclose exact rate limits, as each participating search engine sets its own daily submission thresholds per site.

**If you receive an HTTP 429 (Too Many Requests) response, take the following steps:**

* Pause submissions and retry after the time specified in the Retry-After header.
* Reduce the frequency or batch size of your submissions.
* Log submission activity to monitor for rate-limit errors.

**To avoid hitting rate limits, follow these best practices:**

* Submit only when content has changed. Do not resubmit unchanged URLs.
* Monitor HTTP response codes and adjust submission patterns accordingly.

What should I do if I get a 400 Bad Request error from IndexNow?

An HTTP 400 Bad Request error means the IndexNow submission failed because the request was not properly formatted or was missing required information.

**Common reasons for IndexNow returns a 400 error:**

* The IndexNow API key is missing or incorrect.
* The submitted URL is not properly URL-encoded.
* The request structure does not follow IndexNow format.
* Parameters like url or key are misspelled or missing.

**How to fix a 400 error when using IndexNow:**

* **Verify your IndexNow API key** — Make sure the key in your submission matches the one hosted in your key file.
* **Check that the submitted URL is properly encoded** — Use RFC-3986-compliant encoding for characters like :, /, and &.
* **Review the structure of your IndexNow request** — Whether submitting via GET or POST, confirm the format meets IndexNow protocol guidelines.
* **Correct typos or formatting issues** — Look for extra characters, such as trailing commas or misplaced brackets.
* **Use logging to monitor IndexNow submissions** — Track errors and response codes to identify and correct recurring issues.

By addressing these issues, you can ensure your IndexNow submissions are accepted and processed correctly by participating search engines.

What should I do if I get a 422 Unprocessable Entity error from IndexNow?

An HTTP 422 Unprocessable Entity error means the server understood your IndexNow submission but could not process it due to one or more issues.

**Common reasons why IndexNow returns a 422 error:**

* The submitted URL does not match your verified domain.
* The IndexNow key file is missing or inaccessible.
* The same URL is being submitted repeatedly without meaningful changes.

**How to resolve a 422 error in IndexNow:**

* **Verify the key file location and accessibility** — Make sure the key file is correctly hosted in the root directory and publicly accessible at **https://yourdomain.com/{your-key}.txt**.
* **Confirm the domain matches your key** — Only submit URLs under the domain that matches your verified IndexNow key.
* **Submit only recently changed content** — Avoid submitting unchanged URLs. IndexNow is designed for new, updated, or deleted content.
* **Monitor and log your submissions** — Use logging to track repeated errors, avoid duplicate submissions, and confirm successful delivery.

Fixing these issues helps ensure your IndexNow requests are accepted and processed by participating search engines.

What should I do if I get a 429 Too Many Requests error from IndexNow?

A 429 error means you have **exceeded your site's submission rate limit** by submitting too many URLs to IndexNow in a short time.

**How to resolve an IndexNow 429 error:**

* **Check the Retry-After header** to know how long to wait before resubmitting.
* **Reduce submission frequency** by avoiding unnecessary or duplicate submissions.
* **Wait at least 10 minutes** before resubmitting the same URL, unless it has changed significantly.
* **Log your requests and monitor response codes** to avoid hitting rate limits again.

Each search engine sets its own limits for IndexNow. Slowing down and spacing out submissions improves delivery success.

What are common mistakes to avoid when implementing IndexNow?

These are common implementation issues that may prevent IndexNow from working correctly:

* Hosting the key file outside the domain root.
* Using the wrong file name (must match your key exactly and end in .txt).
* Forgetting to URL-encode special characters in submission URLs.
* Submitting unchanged URLs repeatedly.
* Using an unverified or mismatched key.
* Submitting before the key file is publicly accessible.

Make sure the key file is correctly placed, publicly available, and submission requests are properly formatted.

---

[Terms and Conditions](terms)