import json
from typing import List, Dict 
import markdown as md
from bs4 import BeautifulSoup
import re
import io
import requests
import pdfplumber

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


async def download_extract_text_from_pdf(links:str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/pdf",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",  # Avoid compression issues
        "Referer": "https://google.com"
    }
    all_content=""
    for link in links:
        try:
            resp = requests.get(link, headers=headers, timeout=(10,60))
            resp.raise_for_status()
        except Exception as e:
            print(f"{link}={e}")
        # 2) open with pdfplumber from a BytesIO buffer
        if ".pdf" in link:
            with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
                # join page texts with double newlines
                text = "\n\n".join(
                    page.extract_text() or "" for page in pdf.pages
                ).strip()
        else:
            continue
        all_content+=link+"\n"+text+"\n"
    return all_content



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