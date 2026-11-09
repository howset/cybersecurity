import argparse
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from pathlib import Path
from urllib.parse import urlsplit, unquote, urldefrag


# https://www.scrapingbee.com/blog/download-image-python/
def dl_imgs(img_urls, args, parser):
    """download image urls to the defined directory."""
    directory = Path(args.p)  # create path
    directory.mkdir(parents=True, exist_ok=True)
    for img_url in img_urls:
        filename = unquote(Path(urlsplit(img_url).path).name) or "image"  # Uh confused :(
        output_path = directory / filename  # join
        number = 1
        while output_path.exists():  # check duplicates
            output_path = directory / f"{Path(filename).stem}_{number}{Path(filename).suffix}"
            number += 1
        try:
            with requests.get(
                img_url,
                timeout=15,
                headers={"User-Agent": "spider/1.0 (learning project)"},
                stream=True,
            ) as response:
                response.raise_for_status()
                # print(response.headers.get("Content-Type"))
                with output_path.open("wb") as f:  # write bytes
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print(f"Downloaded: {output_path}")
        except requests.RequestException as error:
            print(f"Could not download {img_url}: {error}")


def get_links(page, args) -> list[str]:
    """Extract same-host links from the page."""
    soup = bs(page, "html.parser")
    links = []
    start_host = urlsplit(args.url).netloc.lower()  # get host by net location
    for tag in soup.find_all("a", href=True):
        link_url, _ = urldefrag(urljoin(args.url, tag["href"]))  # remove fragment
        if urlsplit(link_url).netloc.lower() == start_host:  # exclude other host
            links.append(link_url)
    # for entry in links:
    #     print(entry)
    return links

def get_imageurl(page, args) -> list[str]:
    """extract image urls from html that matches file extensions filter"""
    filter = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
    # filter = (".svg")
    soup = bs(page, "html.parser")  # py’s builtin html parser
    img_urls = []
    for img in soup.find_all("img", src=True):  # refuse <img alt="No source">
        src = img["src"].lower().split("?", 1)[0]  # splits at first ? & keeps whats before it
        if src.endswith(filter):
            # img_url = urljoin(args.url, img["src"])  # read urljoin(base, link)
            # print(args.url)
            # print(img_url)
            img_urls.append(urljoin(args.url, img["src"]))
    # for entry in img_urls:
    #     print(entry)
    return img_urls


def fetch_page(args, parser) -> str:
    """fetch and return the html"""
    try:
        response = requests.get(
            args.url,
            timeout=15,
            headers={"User-Agent": "spider/1.0 (learning project)"},
            # headers={
            #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            #     "Accept-Language": "en-US,en;q=0.9"
            # }
            # headers = {
            #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
            #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            #     "Accept-Language": "en-US,en;q=0.9"
            # }
        )
        response.raise_for_status()
    except requests.RequestException as error:
        parser.error(f"could not fetch URL: {error}")
    # print(response.text)
    return response.text


def recurse(url, depth, max_depth, args, parser, visited):
    if url in visited:
        return
    visited.add(url)
    # print(url)
    args.url = url
    page = fetch_page(args, parser)
    images = get_imageurl(page, args)
    dl_imgs(images, args, parser)
    if depth >= max_depth:
        return
    linklist = get_links(page, args)
    for next_url in linklist:
        recurse(next_url, depth + 1, max_depth, args, parser, visited)


def spider_dl():
    parser = argparse.ArgumentParser(
        prog="./spider",
        description="Download images from a page.",
        epilog="Short usage: ./spider [-r] [-l N] [-p DIR] URL",
    )
    parser.add_argument(
        "-r",
        action="store_true",
        help="crawl linked pages",
    )
    parser.add_argument(
        "-l",
        type=int,
        default=5,
        help="max depth (requires -r)",
    )
    parser.add_argument(
        "-p",
        default="./data/",
        help="output dir",
    )
    parser.add_argument("url", help="page URL")
    args = parser.parse_args()
    if args.l < 0:
        parser.error("-l must be >= 0")
    if args.l != 5 and not args.r:
        parser.error("-l requires -r")
    # page = fetch_page(args, parser)
    # img_urls = get_imageurl(page, args)
    # dl_imgs(img_urls, args, parser)

    if args.r:
        max_depth = args.l
    else:
        max_depth = 0
    recurse(args.url, 0, max_depth, args, parser, set())  # set() -> store unique vals
    # print("args:", args)


if __name__ == "__main__":
    spider_dl()
