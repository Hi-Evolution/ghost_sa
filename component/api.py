# -*- coding: utf-8 -*
# author: unknowwhite@outlook.com
# wechat: Ben_Xiaobai
import sys
sys.path.append("./")
sys.setrecursionlimit(10000000)

from flask import request,jsonify,Response,redirect
import traceback
import time
import urllib.parse
import base64
import json
import pprint
import os
from component.db_func import insert_event,get_long_url_from_short,insert_shortcut_history,check_long_url,insert_shortcut,show_shortcut,count_shortcut,show_check
from component.db_op import *
from geoip.geo import get_addr,get_asn
import gzip
from component.api_tools import insert_device,encode_urlutm,insert_user
from configs.export import write_to_log
from component.shorturl import get_suoim_short_url
from configs import admin




def insert_data(project,data_decode,User_Agent,Host,Connection,Pragma,Cache_Control,Accept,Accept_Encoding,Accept_Language,ip,ip_city,ip_asn,url,referrer,remark,ua_platform,ua_browser,ua_version,ua_language,ip_is_good,ip_asn_is_good,created_at=None,updated_at=None):
  start_time = time.time()
  jsondump = json.dumps(data_decode,ensure_ascii=False)
  if '_track_id' in data_decode:
    track_id = data_decode['_track_id']
  else:
    track_id = 0
  distinct_id = data_decode['distinct_id']
  if 'event' in data_decode:
    event = data_decode['event']
  else:
    event = None
  if remark :
    remark = remark
  else:
    remark = ''
  type_1 = data_decode['type'] if 'type' in data_decode else None
  # lib = data_decode['lib']['$lib'] if '$lib' in data_decode['lib'] else None
  lib = None
  if 'lib' in data_decode:
    if '$lib' in data_decode['lib']:
      lib = data_decode['lib']['$lib']
  elif 'properties' in data_decode:
    if '$lib' in data_decode['properties']:
      lib = data_decode['properties']['$lib']
  try:
    count = insert_event(table=project,alljson=jsondump,track_id=track_id,distinct_id=distinct_id,lib=lib,event=event,type_1=type_1,User_Agent=User_Agent,Host=Host,Connection=Connection,Pragma=Pragma,Cache_Control=Cache_Control,Accept=Accept,Accept_Encoding=Accept_Encoding,Accept_Language=Accept_Language,ip=ip,ip_city=ip_city,ip_asn=ip_asn,url=url,referrer=referrer,remark=remark,ua_platform=ua_platform,ua_browser=ua_browser,ua_version=ua_version,ua_language=ua_language,created_at=created_at)
    print('插入行数：'+str(count))
    insert_device(project=project,data_decode=data_decode,user_agent=User_Agent,accept_language=Accept_Language,ip=ip,ip_city=ip_city,ip_is_good=ip_is_good,ip_asn=ip_asn,ip_asn_is_good=ip_asn_is_good,ua_platform=ua_platform,ua_browser=ua_browser,ua_version=ua_version,ua_language=ua_language,created_at=created_at)
  except Exception:
    error = traceback.format_exc()
    write_to_log(filename='api',defname='insert_date',result=error)
  # if type_1 == 'profile_set' or type_1 == 'track_signup' or type_1 =='profile_set_once' or event == '$SignUp':
  if type_1 == 'profile_set' or type_1 == 'track_signup' or type_1 =='profile_set_once':
    try:
      insert_user(project=project,data_decode=data_decode,created_at=created_at)
    except Exception:
      error = traceback.format_exc()
      write_to_log(filename='api',defname='insert_date',result=error)
  print (time.time()-start_time)

def get_data():
  remark = request.args.get('remark') if 'remark' in request.args else 'normal'
  project = request.args.get('project')
  User_Agent = request.headers.get('User-Agent') #Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36
  Host = request.headers.get('Host') #: 10.16.5.241:5000
  Connection = request.headers.get('Connection')#: keep-alive
  Pragma = request.headers.get('Pragma')#: no-cache
  Cache_Control = request.headers.get('Cache-Control')#: no-cache
  Accept = request.headers.get('Accept')#: image/webp,image/apng,image/*,*/*;q=0.8
  Accept_Encoding = request.headers.get('Accept-Encoding')#: gzip, deflate
  Accept_Language = request.headers.get('Accept-Language')#: zh-CN,zh;q=0.9
  ua_platform = request.user_agent.platform #客户端操作系统
  ua_browser = request.user_agent.browser #客户端的浏览器
  ua_version = request.user_agent.version #客户端浏览器的版本
  ua_language = request.user_agent.language #客户端浏览器的语言
  ext = request.args.get('ext')
  url = request.url
  if request.headers.get('X-Forwarded-For') is None:
    ip = request.remote_addr#服务器直接暴露
  else:
    ip = request.headers.get('X-Forwarded-For') #获取SLB真实地址
  ip_city,ip_is_good = get_addr(ip)
  ip_asn,ip_asn_is_good = get_asn(ip)
  if ip_is_good ==0:
    ip_city = '{}'
  if ip_asn_is_good ==0:
    ip_asn = '{}'
  referrer = request.referrer
  if request.method == 'POST':
    # print(request.form.get())
    if 'data_list' in request.form:
      data_list = request.form.get('data_list')
      data_decodes = json.loads(gzip.decompress(base64.b64decode(urllib.parse.unquote(data_list).encode('utf-8'))))
      for data_decode in data_decodes:
        insert_data(project=project,data_decode=data_decode,User_Agent=User_Agent,Host=Host,Connection=Connection,Pragma=Pragma,Cache_Control=Cache_Control,Accept=Accept,Accept_Encoding=Accept_Encoding,Accept_Language=Accept_Language,ip=ip,ip_city=ip_city,ip_asn=ip_asn,url=url,referrer=referrer,remark=remark,ua_platform=ua_platform,ua_browser=ua_browser,ua_version=ua_version,ua_language=ua_language,ip_is_good=ip_is_good,ip_asn_is_good=ip_asn_is_good)
    elif 'data' in request.form:
      # print(request.cookies)
      data = request.form.get('data')
      data_decode = json.loads(gzip.decompress(base64.b64decode(urllib.parse.unquote(data).encode('utf-8'))))
      insert_data(project=project,data_decode=data_decode,User_Agent=User_Agent,Host=Host,Connection=Connection,Pragma=Pragma,Cache_Control=Cache_Control,Accept=Accept,Accept_Encoding=Accept_Encoding,Accept_Language=Accept_Language,ip=ip,ip_city=ip_city,ip_asn=ip_asn,url=url,referrer=referrer,remark=remark,ua_platform=ua_platform,ua_browser=ua_browser,ua_version=ua_version,ua_language=ua_language,ip_is_good=ip_is_good,ip_asn_is_good=ip_asn_is_good)
    else:
      write_to_log(filename='api',defname='get_datas',result=str(request.form))
      # print(request.form)
  elif request.method == 'GET':
    # try:
    if 'data' in request.args:
      data = request.args.get('data')
      data_decode = json.loads(base64.b64decode(urllib.parse.unquote(data).encode('utf-8')))
      insert_data(project=project,data_decode=data_decode,User_Agent=User_Agent,Host=Host,Connection=Connection,Pragma=Pragma,Cache_Control=Cache_Control,Accept=Accept,Accept_Encoding=Accept_Encoding,Accept_Language=Accept_Language,ip=ip,ip_city=ip_city,ip_asn=ip_asn,url=url,referrer=referrer,remark=remark,ua_platform=ua_platform,ua_browser=ua_browser,ua_version=ua_version,ua_language=ua_language,ip_is_good=ip_is_good,ip_asn_is_good=ip_asn_is_good)
    else:
      write_to_log(filename='api',defname='get_datas',result=url)
  else:
    write_to_log(filename='api',defname='get_datas',result=str(request.method)+url)
  bitimage1 = os.path.join('image','43byte.gif')
  with open(bitimage1, 'rb') as f:
        returnimage = f.read()
  return Response(returnimage, mimetype="image/gif")

def get_datas():
  try:
    return get_data()
  except Exception:
    error = traceback.format_exc()
    write_to_log(filename='api',defname='get_datas',result=error)

def get_long(short_url):
  time1 = int(time.time())
  long_url,status = get_long_url_from_short(short_url=short_url)
  User_Agent = request.headers.get('User-Agent') 
  Accept_Language = request.headers.get('Accept-Language')#: zh-CN,zh;q=0.9
  ua_platform = request.user_agent.platform #客户端操作系统
  ua_browser = request.user_agent.browser #客户端的浏览器
  ua_version = request.user_agent.version #客户端浏览器的版本
  ua_language = request.user_agent.language #客户端浏览器的语言
  url = request.url
  if request.headers.get('X-Forwarded-For') is None:
    ip = request.remote_addr#服务器直接暴露
  else:
    ip = request.headers.get('X-Forwarded-For') #获取SLB真实地址
  time2 = timenow = int(time.time()) - time1
  insert_shortcut_history(short_url=short_url,result=status,cost_time=time2,ip=ip,user_agent=User_Agent,accept_language=Accept_Language,ua_platform=ua_platform,ua_browser=ua_browser,ua_version=ua_version,ua_language=ua_language)
  print(short_url,long_url,status)
  if status == 'success':
    return redirect(long_url)
  elif status == 'expired':
    return '您查询的地址已过期'
  elif status == 'fail':
    return '您查询的解析不存在'

def shortit():
  if 'org_url' in request.form:
    org_url = request.form.get('org_url')
    expired_at = int(time.mktime(time.strptime(request.form.get('expired_at','2038-01-19'), "%Y-%m-%d")))
    project = request.form.get('project',None)
    src = request.form.get('src','suoim')
    submitter = request.form.get('submitter',None)
    utm_source = request.form.get('utm_source',None)
    utm_medium = request.form.get('utm_medium',None)
    utm_campaign = request.form.get('utm_campaign',None)
    utm_content = request.form.get('utm_content',None)
    utm_term = request.form.get('utm_term',None)
    url_addon = encode_urlutm(utm_source=utm_source,utm_medium=utm_medium,utm_campaign=utm_campaign,utm_content=utm_content,utm_term=utm_term)
    if '?' in org_url:
      longurl = org_url+'&'+url_addon
    else:
      longurl = org_url+'?'+url_addon
    urllist,urlstatus = check_long_url(long_url=longurl)
    if urlstatus == 'exist':
      returnjson = {'result':urlstatus,'urllist':urllist}
      return jsonify(returnjson)
    else:
      check_short_status = 'success'
      while check_short_status == 'success':
        if src =='suoim':
          src_short_url,status = get_suoim_short_url(long_url=longurl)
        else:
          return jsonify({'result':'error','urllist':'src:'+src+'不存在'})
        if status == 'ok':
          check_short_result,check_short_status = get_long_url_from_short(src_short_url)
          if check_short_status == 'success':
            continue
          break
      short_url = src_short_url.split('/')[-1]
      insert_count = insert_shortcut(project=project,short_url=short_url,long_url=longurl,expired_at=expired_at,src=src,src_short_url=src_short_url,submitter=submitter,utm_source=utm_source,utm_medium=utm_medium,utm_campaign=utm_campaign,utm_content=utm_content,utm_term=utm_term)
      print('已插入短连接解析地址'+str(insert_count))
      urllist,urlstatus = check_long_url(long_url=longurl)
      returnjson = {'result':'created_success','urllist':urllist}
      return jsonify(returnjson)
  else:
    returnjson = {'result':'error','error':'参数不全'}
    return jsonify(returnjson)

def show_short_cut_list():
  page = int(request.args.get('page')) if 'page' in request.args else 1
  length = int(request.args.get('length')) if 'length' in request.args else 50
  sort  = '`shortcut`.created_at'
  if 'sort' in request.args:
    sort_org = request.args.get('sort')
    sort = '`shortcut`.'+sort_org
    if sort_org == 'visit_times':
      sort = 'visit_times'
  way = request.args.get('way') if 'way' in request.args else 'desc'
  add_on_parames = []
  if 'create_date_start' in request.args:
    add_on_parames.append('`shortcut`.created_at>={crstart}'.format(crstart=request.args.get('create_date_start')))
  if 'create_date_end' in request.args:
    add_on_parames.append('`shortcut`.created_at<={crend}'.format(crend=request.args.get('create_date_end')))
  if 'expired_date_start' in request.args:
    add_on_parames.append('`shortcut`.expired_at>={epstart}'.format(epstart=request.args.get('expired_date_start')))
  if 'expired_date_end' in request.args:
    add_on_parames.append('`shortcut`.expired_at<={epend}'.format(epend=request.args.get('expired_date_end')))
  if 'short_url' in request.args:
    add_on_parames.append('`shortcut`.short_url=\'{short_url}\''.format(short_url=request.args.get('short_url')))
  if 'long_url' in request.args:
    add_on_parames.append('`shortcut`.long_url like \'{long_url}%\''.format(long_url=request.args.get('long_url')))
  if 'utm_source' in request.args:
    add_on_parames.append('`shortcut`.utm_source like \'%{utm_source}%\''.format(utm_source=request.args.get('utm_source')))
  if 'utm_medium' in request.args:
    add_on_parames.append('`shortcut`.utm_medium like \'%{utm_medium}%\''.format(utm_medium=request.args.get('utm_medium')))
  if 'utm_campaign' in request.args:
    add_on_parames.append('`shortcut`.utm_campaign like \'%{utm_campaign}%\''.format(utm_campaign=request.args.get('utm_campaign')))
  if 'utm_content' in request.args:
    add_on_parames.append('`shortcut`.utm_content like \'%{utm_content}%\''.format(utm_content=request.args.get('utm_content')))
  if 'utm_term' in request.args:
    add_on_parames.append('`shortcut`.utm_term like \'%{utm_term}%\''.format(utm_term=request.args.get('utm_term')))
  if 'project' in request.args:
    add_on_parames.append('`shortcut`.project=\'{project}\''.format(project=request.args.get('project')))
  if 'submitter' in request.args:
    add_on_parames.append('`shortcut`.submitter=\'{submitter}\''.format(submitter=request.args.get('submitter')))
  if 'src' in request.args:
    add_on_parames.append('`shortcut`.src=\'{src}\''.format(src=request.args.get('src')))
  if 'src_short_url' in request.args:
    add_on_parames.append('`shortcut`.src_short_url=\'{src_short_url}\''.format(src_short_url=request.args.get('src_short_url')))
  if 'everywhere' in request.args:
    add_on_parames.append('concat(`shortcut`.project,`shortcut`.short_url,`shortcut`.long_url,`shortcut`.src,`shortcut`.src_short_url,`shortcut`.submitter,`shortcut`.utm_source,`shortcut`.utm_medium,`shortcut`.utm_campaign,`shortcut`.utm_content,`shortcut`.utm_term) like \'%{everywhere}%\''.format(everywhere=request.args.get('everywhere')))
  add_on_params=''
  if add_on_parames:
    add_on_params = " where " + " and ".join(add_on_parames)
  total_count = count_shortcut(filters=add_on_params)
  if total_count[0][0] > 0:
    result,count = show_shortcut(page=page,length=length,filters=add_on_params,sort=sort,way=way)
    if count >0:
      result_name = ['project','short_url','long_url','expired_at_str','created_at_str','src','src_short_url','submitter','utm_source','utm_medium','utm_campaign','utm_content','utm_term','created_at','expired_at','visit_times']
      return_data = []
      for item in result:
        zipped = dict(zip(result_name,item))
        return_data.append(zipped)
      returnjson = {'result':'success','sort':sort,'way':way,'count':count,'total_count':total_count[0][0],'page':page,'length':length,'data':return_data}
      return jsonify(returnjson)
    returnjson = {'result':'fail','error':'参数不正确'}
    return jsonify(returnjson)
  returnjson = {'result':'fail','error':'未找到对应的短链'}
  return jsonify(returnjson)

def ghost_check():
  start_time = time.time()
  password = request.form.get('password')
  project = request.form.get('project',None)
  if password == admin.admin_password and project:#只有正确的密码才能触发动作
    remark = request.form.get('remark',None)
    event = request.form.get('event',None)
    date = request.form.get('date',time.strftime("%Y-%m-%d", time.localtime()))
    hour = int(request.form.get('hour',time.strftime("%H", time.localtime())))
    order = request.form.get('order','desc')
    distinct_id = request.form.get('distinct_id',None)
    start = int(request.form.get('start','0'))
    limit = int(request.form.get('limit','10'))
    add_on_where = ''
    if distinct_id:
      add_on_where = add_on_where+' and distinct_id = \''+distinct_id+'\''
    if event:
      add_on_where = add_on_where+' and event = \''+event+'\''
    if remark:
      add_on_where = add_on_where+' and remark = \''+remark+'\''
    try:
      results,results_count= show_check(project=project,date=date,hour=hour,order=order,start=start,limit=limit,add_on_where=add_on_where)
      pending_result = []
      for item in results:
        row = {'distinct_id':item[0],'event':item[1],'type':item[2],'all_json':json.loads(item[3]),'host':item[4],'user_agent':item[5],'ip':item[6],'url':item[7],'remark':item[8],'created_at':item[9],}
        pending_result.append(row)
      time_cost = time.time() - start_time
      returnjson = {'result':'success','order':order,'results_count':results_count,'timecost':time_cost,'data':pending_result}
      return jsonify(returnjson)
    except Exception:
      error = traceback.format_exc()
      write_to_log(filename='api',defname='ghost_check',result=error)