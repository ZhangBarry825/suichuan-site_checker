# encoding=utf8
# author=spenly
# mail=i@spenly.com

from link_checker import LinkChecker
from utils import *

class ZWFWChecker(LinkChecker):

    def _get_date(self, doc, link):
        # return format:xxxx-xx-xx
        sdate = "#"
        if "detail" in link.lower():
            sdate = select(doc.xpath("//label[contains(text(),'发布日期')]/text()"))
            sdate = sdate.split("：")[-1]
        return sdate

if __name__ == "__main__":
    zwgk = ZWFWChecker("http://jasc.jxzwfww.gov.cn/jazwfw/")
    zwgk.run()
