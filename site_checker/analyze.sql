-- replace all your task id to real task id


create table link_title_count (select url, title, count(*) as ct from links group by url, title);
create table link_title_map (select url, title, ct from link_title_count where title <> '' group by url having ct = max(ct));

update links, link_title_map
set links.title = link_title_map.title
where links.url = link_title_map.url;

update links, link_title_map
set links.ptitle = link_title_map.title
where links.purl = link_title_map.url;

-- update data by task_id
update links, (
select status_code, error, sdate, url, task_id from links where task_id = "xxxxxxxxxx" and status_code <> 0) as t1
set links.status_code = t1.status_code,
links.error = t1.error,
links.sdate = t1.sdate
where links.url = t1.url and links.task_id = t1.task_id;

-- get faileds links by task_id
select * from links where task_id = "xxxxxxxxxx" and status_code <> 200

-- get latest update time of each column by task id
select purl, ptitle, max(sdate) from links where task_id = "xxxxxxxxxx" GROUP BY purl

