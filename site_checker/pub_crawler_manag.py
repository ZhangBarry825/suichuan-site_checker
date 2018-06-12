# encoding=utf8
# author=spenly
# mail=i@spenly.com

import requests
from cpyder import document, select
import re
import time
from models import engine, ChannelInfo, DocumentInfo, Task


class WCM_Suichuan(object):

    def __init__(self, user, pswd):
        self.user = user
        self.pswd = pswd
        self._login_page = "http://218.64.81.28:9000/wcm/app/login.jsp"
        self._login_api = "http://218.64.81.28:9000/wcm/app/login_dowith.jsp"
        self._tree_root_api = "http://218.64.81.28:9000/wcm/app/nav_tree/tree_html_creator.jsp"
        self._channel_list_api = "http://218.64.81.28:9000/wcm/center.do"
        self._column_list_api = "http://218.64.81.28:9000/wcm/app/infoview/infoview_document_list_of_channel.jsp"
        self._info_view_api = "http://218.64.81.28:9000/wcm/center.do?serviceid=wcm61_infoviewdoc&methodname=infoViewFindById&ObjectIds={0}&ObjectId={0}"
        self.session = requests.session()
        # simulate the login action
        self.session.get(self._login_page)
        self.login_status = False
        self.todo_columns = []
        self.task_id = None
        self.visited_channels = {}

    def create_task(self):
        self.task_id = "SuiChuan-mgmt-console-" + time.strftime("%Y%m%d%H%M%S")
        stmt = Task.insert().values({"task_id": self.task_id}).return_defaults()
        engine.execute(stmt)

    def login(self, user="", pswd=""):
        user = user or self.user
        pswd = pswd or self.pswd
        data = {"FromUrl": "", "UserName": user, "PassWord": pswd, "x": "48", "y": "14"}
        rep = self.session.post(self._login_api, data=data)
        # cookies expires almost 1 year
        # so will not check login expires time here
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "==> login cookies")
        print(rep.headers.get("Set-Cookie"))
        if rep.status_code == 200:
            print("==> login successful!")
            self.login_status = True
        else:
            print("==> login failed!")

    def get_info_view(self, object_id, channel_id):
        print(time.strftime("%Y-%m-%d %H:%M:%S"), ">>>", object_id)
        url = self._info_view_api.format(object_id)
        rep = self.session.get(url)
        if rep.status_code != 200 or not rep.text.strip():
            print("get document info view failed")
            return
        if rep.text.startswith("<fault>"):
            doc = document(rep.text, "xml")
            channel_name = "null"
            doc_title = select(doc.xpath("//detail/text()"))
            doc_status = ""
            pub_url = ""
            pub_date = ""
        else:
            doc = document(rep.text)
            channel_name = select(doc.xpath("//div[@class='attribute_row docchannel readonly']/span[2]/text()"))
            doc_title = select(doc.xpath("//div[@class='attribute_row doctitle editable']/span/text()"))
            doc_status = select(doc.xpath("//div[@class='attribute_row docstatus editable']/span[2]/text()"))
            pub_url = select(doc.xpath("//div[@class='attribute_row docpuburl readonly']//text()"))
            pub_date = select(doc.xpath("//div[@class='attribute_row descinfo readonly']/span/span[4]/text()"))
        doc_info = {
            "doc_id": object_id,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "task_id": self.task_id,
            "doc_title": doc_title,
            "pub_url": pub_url,
            "pub_date": pub_date,
            "doc_status": doc_status
        }
        try:
            stmt = DocumentInfo.insert().values(doc_info).return_defaults()
            engine.execute(stmt)
        except Exception as ex:
            print("sql error", ex)
            print(doc_info)

    def _parse_list(self, doc):
        items = doc.xpath("//tbody[@class='grid_body']/tr")
        ids = []
        for item in items:
            article_id = select(item.xpath("./@rowid")).strip()
            ids.append(article_id)
        return ids

    def get_info_list(self, channel_id, rv, list_type):
        cur_page = 0
        page_size = 20
        next_page = True
        ids = []
        while next_page:
            cur_page = cur_page + 1
            print(time.strftime("%Y-%m-%d %H:%M:%S"), "-> -> ", channel_id, cur_page, list_type)
            if list_type == "column":
                post = {
                    'CHANNELID': channel_id,
                    'CHANNELIDS': channel_id,
                    'CHANNELTYPE': '13',
                    'CHNLDOCSELECTFIELDS': 'WCMChnlDoc.DOCKIND,WCMChnlDoc.DOCID,WCMChnlDoc.ChnlId,WCMChnlDoc.DocStatus,WCMChnlDoc.DocChannel,WCMChnlDoc.DocOrderPri,WCMChnlDoc.Modal,WCMChnlDoc.RecId',
                    'DOCUMENTSELECTFIELDS': 'DOCID,DocTitle,DocType,CrUser,CrTime,AttachPic,FLOWOPERATIONMARK',
                    'FIELDSTOHTML': 'DocTitle,DocChannel.Name',
                    'FILTERTYPE': '0',
                    'ISVIRTUAL': '',
                    'PAGESIZE': str(page_size),
                    'RIGHTVALUE': rv,
                    'SITEIDS': '',
                    'SITETYPE': '0',
                    'CURRPAGE': str(cur_page)
                }
                url = self._column_list_api
            elif list_type == "channel":
                post = """<post-data><method type="jQuery">wcm61_viewdocument</method><parameters><CHANNELID><![CDATA[{0}]]></CHANNELID><SITETYPE><![CDATA[0]]></SITETYPE><ISVIRTUAL><![CDATA[]]></ISVIRTUAL><CHANNELTYPE><![CDATA[0]]></CHANNELTYPE><RIGHTVALUE><![CDATA[{1}]]></RIGHTVALUE><FIELDSTOHTML><![CDATA[DocTitle,DocChannel.Name]]></FIELDSTOHTML><CHNLDOCSELECTFIELDS><![CDATA[WCMChnlDoc.DOCKIND,WCMChnlDoc.DOCID,WCMChnlDoc.ChnlId,WCMChnlDoc.DocStatus,WCMChnlDoc.DocChannel,WCMChnlDoc.DocOrderPri,WCMChnlDoc.Modal,WCMChnlDoc.RecId,WCMCHNLDOC.CRTIME,WCMCHNLDOC.INVALIDTIME]]></CHNLDOCSELECTFIELDS><DOCUMENTSELECTFIELDS><![CDATA[DOCID,DocTitle,DocType,CrUser,CrTime,AttachPic,FLOWOPERATIONMARK]]></DOCUMENTSELECTFIELDS><CHANNELIDS><![CDATA[{0}]]></CHANNELIDS><SITEIDS><![CDATA[]]></SITEIDS><FILTERTYPE><![CDATA[0]]></FILTERTYPE><PAGESIZE><![CDATA[{2}]]></PAGESIZE><CURRPAGE><![CDATA[{3}]]></CURRPAGE></parameters></post-data>"""
                post = post.format(channel_id, rv, page_size, cur_page)
                url = self._channel_list_api
            else:
                print("invalid list type.")
                return
            rep = self.session.post(url, post)
            if rep.status_code != 200 and not rep.text.strip():
                return
            if rep.text.startswith("<fault>"):
                print("[ error ]", channel_id, rv)
                print(rep.text)
                return
            doc = document(rep.text)
            tids = self._parse_list(doc)
            if len(tids) < page_size or tids == ids:
                next_page = False
            if tids != ids:
                for did in tids:
                    self.get_info_view(did, channel_id)
            ids = tids

    def get_sub_tree(self, parent_type, parent_id, depth):
        post = {"Type": 0, "ParentType": parent_type, "ParentId": parent_id, "forIndividual": 1}
        rep = self.session.post(self._tree_root_api, data=post)
        if rep.status_code != 200:
            return
        try:
            doc = document(rep.text)
        except Exception as ex:
            print("!!! parent_id", parent_id, depth)
            print(ex)
            return
        # channels_tag = ""
        channels = []
        for channel in doc.xpath("//div"):
            class_pre = select(channel.xpath("./@classpre")).strip()
            rv = select(channel.xpath("./@rv")).strip()
            cid = select(channel.xpath("./@id")).strip()  # x_xxxx
            channel_name = select(channel.xpath("./@title")).strip()
            # channels_tag += channel_name
            column = cid.split("_")
            channel_id = column[1]
            assert len(column) == 2
            print(time.strftime("%Y-%m-%d %H:%M:%S"), "+", depth, channel_id, channel_name)
            chn_info = {
                "column": column,
                "channel_id": channel_id,
                "class_pre": class_pre,
                "channel_name": channel_name,
                "channel_type": class_pre,
                "right_value": rv,
                "parent_id": parent_id,
                "task_id": self.task_id
            }
            channels.append(chn_info.copy())
        for chn in channels:
            column = chn.pop("column")
            channel_id = column[1]
            class_pre = chn.pop("class_pre")
            if class_pre == "channel":
                column.append(depth + 1)
                self.todo_columns.append(column)
                self.get_info_list(channel_id, chn["right_value"], "channel")
            elif class_pre == "channel13":
                self.get_info_list(channel_id, chn["right_value"], "column")
            stmt = ChannelInfo.insert().values(chn).return_defaults()
            engine.execute(stmt)

    def run(self):
        if not self.login_status:
            self.login()
        if self.login_status:
            self.create_task()
        else:
            return
        # init start channel
        start_channel = ["s", "40", 0]
        self.todo_columns.append(start_channel)
        chn_info = {
            "channel_id": "40",
            "channel_name": "suichuan_gov_pub_root",
            "channel_type": "site",
            "parent_id": "0",
            "task_id": self.task_id
        }
        stmt = ChannelInfo.insert().values(chn_info).return_defaults()
        engine.execute(stmt)
        for column in self.todo_columns:
            self.get_sub_tree(*column)
        print("all over!")


if __name__ == "__main__":
    wcm = WCM_Suichuan("sc_adminqiang", "xxzx6326836")
    wcm.run()
    # wcm.login()
    # wcm.get_info_list("102287", "110000110100000000000001111111111000001000011111111101110111110", "channel")
    # wcm.get_info_list("102288", "110000110100000000000001111111111000001000011111111001110111110", "column")
    # wcm.get_info_view("42544", "102287")
