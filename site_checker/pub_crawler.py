# encoding=utf8
# author=spenly
# mail=i@spenly.com

from link_checker import LinkChecker
from utils import url_padding, select
import re

DATE_PATTERN = re.compile(".*?/t(\d{8})_.*?")


class PubChecker(LinkChecker):

    def _get_date(self, doc, link):
        # return format:xxxx-xx-xx
        sdate = "#"
        res = DATE_PATTERN.match(link)
        if res and len(res.groups()) > 0:
            sdate = res.groups()[0]
            sdate = "-".join([sdate[:4], sdate[4:6], sdate[6:8]])
        return sdate

    def _get_extra_links(self, doc, plink):
        links = doc.xpath('//script[contains(text(), "gkfs(")]')
        for l in links:
            content = select(l.xpath(".//text()")).replace("gkfs(", "").replace(")", "")
            items = content.split(",")
            items = [item.replace('"', "") for item in items]
            if len(items) == 3:
                link = {}
                _, url_shown, title = items
                url = url_padding(url_shown, plink["url"])
                if not url:
                    continue
                link["url"] = url
                link["url_shown"] = url_shown
                link["title"] = title
                link["purl"] = plink["url"]
                link["ptitle"] = plink["title"]
                self.links.append(link.copy())


if __name__ == "__main__":
    ja = PubChecker("http://pub.jian.gov.cn/jxsc/")
    ja.run()
