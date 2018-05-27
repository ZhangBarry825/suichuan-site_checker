# encoding=utf8
# author=spenly
# mail=i@spenly.com

from utils import *
import sys
import re
import time
from models import Task, engine, Links


class LinkChecker(object):

    def __init__(self, site):
        self.site = site
        self.links = [
            {"url": site, "url_shown": "", "title": "site", "purl": "", "ptitle": ""}
        ]
        self.url_visited = []
        self.task_id = None

    def _get_date(self, doc, link):
        # return format:xxxx-xx-xx
        return "#"

    def _get_links(self, doc, plink):
        links = doc.xpath("//a")
        for l in links:
            link = {}
            url_shown = select(l.xpath("./@href")).strip()
            title = select(l.xpath("./@title")).strip()
            if not title:
                title = select(l.xpath("./text()")).strip()
            if not title:
                title = select(l.xpath(".//text()")).strip()
            title = title.replace(";", "").replace(",", " ").replace("\n", "").replace("\t", "")
            url = url_padding(url_shown, plink["url"])
            if not url:
                continue
            link["url"] = url
            link["url_shown"] = url_shown
            link["title"] = title
            link["purl"] = plink["url"]
            link["ptitle"] = plink["title"]
            self.links.append(link.copy())

    def _get_extra_links(self, doc, plink):
        pass


    def create_task(self):
        self.task_id = self.site + "-" + time.strftime("%Y%m%d%H%M%S")
        stmt = Task.insert().values({"task_id": self.task_id}).return_defaults()
        engine.execute(stmt)

    def run(self):
        self.create_task()
        wf = open("error.log", "w+")
        for link in self.links:
            url = link["url"]
            rst = link.copy()
            rst["task_id"] = self.task_id
            if url not in self.url_visited:
                print(url)
                if link["title"]:
                    self.url_visited.append(url)
                doc, status_code, error = parse_url(url)
                if doc is not None and url.startswith(self.site):
                    self._get_links(doc, link)
                    self._get_extra_links(doc, link)
                sdate = self._get_date(doc, url)
                rst["status_code"] = str(status_code)
                rst["error"] = error
                rst["sdate"] = sdate
            else:
                rst["status_code"] = "0"
                rst["error"] = "duplicate"
                rst["sdate"] = "#"
            try:
                stmt = Links.insert().values(rst).return_defaults()
                engine.execute(stmt)
            except Exception as ex:
                wf.write(str(rst))
                wf.write(str(ex))
        # finally
        self.task_id = None
        wf.close()


if __name__ == "__main__":
    lc = LinkChecker("http://www.suichuan.gov.cn")
    lc.run()
