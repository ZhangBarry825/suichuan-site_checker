# encoding=utf8
# author=spenly
# mail=i@spenly.com
import datetime
from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime, create_engine

engine = create_engine("mysql://root:admin@localhost/site_checker", encoding='utf8')
metadata = MetaData()

Task = Table('task', metadata,
             Column('task_id', String(128), index=True),
             Column('start_time', DateTime, nullable=False, default=datetime.datetime.utcnow),
             Column('end_time', DateTime),
             )
# task_id, url,url_shown,title,purl,ptitle,status_code,error,sdate
Links = Table("links", metadata,
              Column("task_id", String(128), index=True),
              Column("url", String(256), index=True),
              Column("url_shown", String(512)),
              Column("title", String(512)),
              Column("purl", String(256), index=True),
              Column("ptitle", String(512)),
              Column("status_code", Integer),
              Column("error", String(512)),
              Column("sdate", String(16)),
              )
# task_id, url,url_shown,title,purl,ptitle,status_code,error,sdate
FailedLinks = Table("failed_links", metadata,
                    Column("task_id", String(128), index=True),
                    Column("url", String(256), index=True),
                    Column("url_shown", String(512)),
                    Column("title", String(512)),
                    Column("purl", String(256), index=True),
                    Column("ptitle", String(512)),
                    Column("status_code", Integer),
                    Column("error", String(512)),
                    Column("sdate", String(16)),
                    )
# task_id, purl, ptitle, sdate
ColumnsUpdates = Table("columns_updates", metadata,
                       Column("task_id", String(128), primary_key=True),
                       Column("purl", String(512), primary_key=True),
                       Column("ptitle", String(512)),
                       Column("sdate", String(16)),
                       )

# create for the first time
# or ignore if existed
metadata.bind = engine
metadata.create_all()
