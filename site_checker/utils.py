# encoding=utf8
# author=spenly
# mail=i@spenly.com

from cpyder import select, document, HttpWorker
import requests
from urllib.parse import urljoin


def apply_rules(doc, rules):
    res = doc
    for item in rules:
        if item["type"] == "xp":
            res = select(res.xpath(item["value"]))
        elif item["type"] == "py":
            res = eval(item["value"])(res)
    return res


invalid_url_heads = ["mailto:", "javascript:"]


def url_padding(link, plink):
    for item in invalid_url_heads:
        if link.startswith(item):
            return ""
    if "." not in plink.split("/")[-1] and not plink.endswith("/"):
        plink = plink + "/"
    link = urljoin(plink, link)
    if link.endswith("/"):
        link = link[:-1]
    link = link.split("#")[0]
    return link


file_exts = ["doc", "docx", "xls", "xlsx", "ppt", "pptx", "pdf", "jpg", "jpeg", "png", "xml", "rar"]


def is_file(url):
    url = url.lower()
    for ext in file_exts:
        if url.endswith("." + ext):
            return True
    return False


headers = {
    "user-agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko)" +
        "Chrome/66.0.3359.139 Safari/537.36",
    "accept": "*/*"
}


def parse_url(url):
    status_code = -1
    doc = None
    error = "NA"
    try:
        if is_file(url):
            rep = requests.head(url)
            status_code = rep.status_code
            return doc, status_code, error
        else:
            rep = requests.get(url, timeout=10, headers=headers)
        status_code = rep.status_code
        if "Content-Type" in rep.headers and rep.headers["Content-Type"].lower().startswith("text"):
            try:
                str_doc = rep.content.decode("utf8")
            except Exception:
                str_doc = rep.content.decode("gb2312", errors="ignore")
            str_doc = str_doc.replace("<A>", "<a>").replace("<A/>", "<a/>")
            doc = document(str_doc)
    except Exception as ex:
        error = str(ex).replace(",", " ").replace("\"", "'")
        print(error)
    return doc, status_code, error
