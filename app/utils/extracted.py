import json
from typing import List, Dict 
import markdown as md
from bs4 import BeautifulSoup
import re
import io
import requests
import pdfplumber
import logging
async def extract_pages_to_json(docs: List[object]) -> json:
    """
    From a list of FirecrawlDocument-like objects, writes a JSON list where each entry has:
      - text: cleaned, tag-free, link-free
      - file_links: [.pdf/.docx/etc URLs]
      - image_links: [all image URLs from <img>]
    """
    # Define which extensions count as “files”
    doc_exts = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')
    url_strip = re.compile(r'https?://\S+')
    # print(str(docs)[:100])
    output: List[Dict[str, object]] = []
    for doc in docs:
        # 1) Get HTML source
        if getattr(doc, "rawHtml", None):
            html = doc.rawHtml
        elif getattr(doc, "html", None):
            html = doc.html
        else:
            md_src = getattr(doc, "markdown", "") or ""
            html = md.markdown(md_src)

        soup = BeautifulSoup(html, "html.parser")

        # 2) Find and classify all <a href> links
        file_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(doc_exts):
                file_links.append(href)

        # 3) Find all <img> src URLs
        image_links = [img["src"] for img in soup.find_all("img", src=True)]

        # 4) Extract clean text
        text = soup.get_text(separator="\n")
        text = url_strip.sub("", text)           # remove any leftover URLs
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        output.append({
            "text": text,
            "file_links": file_links,
            "image_links": image_links
        })

    # # 5) Write JSON
    # with open(output_path, "w", encoding="utf-8") as f:
    #     json.dump(output, f, ensure_ascii=False, indent=2)
    return output





async def unique_pdf(links:List[str],available:List[str])->List[str]:
    checked=[]
    for link in links:
        if link not in available:
            checked.append(link)
    return checked





# async def download_extract_text_from_pdf(links:str):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#         "Accept": "application/pdf",
#         "Accept-Language": "en-US,en;q=0.9",
#         "Accept-Encoding": "identity",  # Avoid compression issues
#         "Referer": "https://google.com"
#     }
#     all_content=""
#     for link in links:
#         try:
#             resp = requests.get(link, headers=headers, timeout=(10,60))
#             resp.raise_for_status()
#         except Exception as e:
#             print(f"{link}={e}")
#         # 2) open with pdfplumber from a BytesIO buffer
#         if ".pdf" in link:
#             with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
#                 # join page texts with double newlines
#                 text = "\n\n".join(
#                     page.extract_text() or "" for page in pdf.pages
#                 ).strip()
#         else:
#             continue
#         all_content+=link+"\n"+text+"\n"
#     return all_content






async def download_extract_text_from_pdf(links: List[str]) -> str:
    """
    Download each PDF, skip failures, extract only “real” text pages,
    strip out (cid:…) junk, and drop pages whose text is <50% letters.
    Returns one big string of all cleaned text.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/pdf",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
        "Referer": "https://google.com"
    }

    cleaned_pages = []

    for url in links:
        if not url.lower().endswith(".pdf"):
            logging.warning(f"Skipping non‑PDF link: {url}")
            continue

        try:
            resp = requests.get(url, headers=headers, timeout=(10, 60))
            resp.raise_for_status()
        except Exception as e:
            logging.warning(f"{url} download failed: {e}")
            continue

        if "pdf" not in resp.headers.get("Content-Type", "").lower():
            logging.warning(f"Not a PDF MIME‑type: {url}")
            continue

        try:
            with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
                for page in pdf.pages:
                    raw = page.extract_text() or ""
                    if not raw.strip():
                        continue

                    # 1) remove (cid:###)
                    no_cid = re.sub(r"\(cid:\d+\)", "", raw)
                    # 2) drop non‑printable
                    printable = "".join(ch for ch in no_cid if ch.isprintable())
                    # 3) compute letter ratio
                    total = len(printable)
                    letters = sum(ch.isalpha() for ch in printable)
                    if total == 0 or letters/total < 0.5:
                        # too much gibberish—skip this page
                        continue

                    # page is “real text”
                    cleaned_pages.append(printable.strip())

        except Exception as e:
            logging.warning(f"Failed to parse PDF {url}: {e}")
            continue

    # join all kept pages
    return "\n\n".join(cleaned_pages)





async def all_content_formatting(extracted:json) -> str:
    '''
        It will accept the extracted information from wesite and format everythink
    '''
    all_text:str=""
    used_pdf=[]
    for field in extracted:
        all_text+=field['text']
        new_links= await unique_pdf(field['file_links'],used_pdf)
        used_pdf.extend(new_links)
        content_from_pdf= await download_extract_text_from_pdf(new_links)
        all_text+="\n"+content_from_pdf+"\n"
    return all_text



