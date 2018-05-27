# encoding=utf8
# author=spenly
# mail=i@spenly.com

from link_checker import LinkChecker


class SuiChuanChecker(LinkChecker):

    def _get_date(self, doc, link):
        # return format:xxxx-xx-xx
        sdate = "#"
        if link.startswith(self.site + "/doc/"):
            sdate = "-".join(link.split("/doc/")[-1].split("/")[:3])
        return sdate


if __name__ == "__main__":
    sc = SuiChuanChecker("http://www.suichuan.gov.cn")
    sc.run()
