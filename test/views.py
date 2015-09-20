# coding:utf-8
import datetime
from sets import Set
import MySQLdb
from MySQLdb.cursors import DictCursor
from django.shortcuts import render
from django.http import HttpResponse
from utils import json_encode


ENV_NAME_DICT = {
    "1": "FAT",
    "2": "LPT",
    "3": "FWS",
    "4": "ComDev",
    "5": "UAT"
}


class QateServerInfo(object):
    """
    统一的服务器信息类
    """
    def __init__(self, env=None, name=None, ip=None, os=None, cpu=None,
                 mem=None, disk=None, role=None, pd=None, desc=None):
        self.env = env
        self.name = name
        self.ip = ip
        self.os = os
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
        self.role = role
        self.pd = pd
        self.desc = desc

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))


class QateEnvInfo(object):
    """
    统一的环境信息
    """
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))


class QatePDInfo(object):
    """
    统一的PD信息
    """
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))


def get_uat_cursor():
    """
    获取uat数据库连接
    """
    uat_conn = MySQLdb.connect(
        host="192.168.1.109",
        port=3306,
        user="test",
        passwd="test",
        db="test",
        cursorclass=DictCursor,
        charset="utf8",
        use_unicode=False
    )
    uat_cursor = uat_conn.cursor()
    return uat_cursor


def get_qate_cursor():
    """
    获取qate数据库连接
    """
    qate_conn = MySQLdb.connect(
        host="192.168.1.109",
        port=3306,
        user="test",
        passwd="test",
        db="test",
        cursorclass=DictCursor,
        charset="utf8",
        use_unicode=False
    )
    qate_cursor = qate_conn.cursor()
    return qate_cursor


def need_filter_server(server_info, filter_env_name, filter_pd_name, key):
    """
    过滤服务器信息
    如果需要过滤，返回true，否则返回false
    """
    # 如果是搜索key，必须ip或者名称等于key
    if key != "":
        if key.lower() == server_info.ip.lower() or key.lower() == server_info.name.lower():
            return False
    else:
        # 如果是按照env和pd进行过滤
        if filter_env_name == "所有环境" and filter_pd_name == "所有PD":
            return False
        elif filter_env_name == "所有环境" and filter_pd_name != "所有PD":
            if filter_pd_name == server_info.pd:
                return False
        elif filter_env_name != "所有环境" and filter_pd_name == "所有PD":
            if filter_env_name == server_info.env:
                return False
        else:
            if filter_pd_name == server_info.pd and filter_env_name == server_info.env:
                return False

    return True


def get_page_server_infos_from_db(filter_env_name, filter_pd_name, key, pageNum, pageSize):
    """
    从数据库表中获取数据，并解析成dict
    """
    # import pdb; pdb.set_trace()
    uat_cursor = get_uat_cursor()

    # 获取uat的所有服务器信息
    sql = """
    select HostName,IPAddress,OSInfo,CPUInfo,MemInfo,DiskTotal,Role,Comments,Pd_id from simplecmdb_server
    order by Pd_id, Role
    """
    uat_cursor.execute(sql)
    uat_results = uat_cursor.fetchall()
    uat_cursor.close()

    all_server_infos = []
    for result in uat_results:
        tmp_server = QateServerInfo()
        tmp_server.env = "UAT"
        tmp_server.name = result["HostName"]
        tmp_server.ip = result["IPAddress"]
        tmp_server.os = result["OSInfo"]

        tmp_server.cpu = result["CPUInfo"]
        tmp_server.mem = result["MemInfo"]
        tmp_server.disk = result["DiskTotal"]

        tmp_server.role = result["Role"]
        tmp_server.pd = result["Pd_id"]
        tmp_server.desc = result["Comments"]
        all_server_infos.append(tmp_server)

    # 获取QATE的所有服务器信息
    qate_cursor = get_qate_cursor()

    # 获取Qate的部门id和名称信息
    sql = """
    select id,name from auth_group
    """
    qate_cursor.execute(sql)
    dept_results = qate_cursor.fetchall()

    pd_dict = {}

    for result in dept_results:
        pd_dict[result["id"]] = result["name"]

    sql = """
    select env_id,name,ip,image,cpu,memory,disk,role,dept_id,comments from vm
    order by dept_id, role
    """
    qate_cursor.execute(sql)
    qate_results = qate_cursor.fetchall()
    qate_cursor.close()

    for result in qate_results:
        tmp_server = QateServerInfo()
        tmp_server.env = ENV_NAME_DICT[str(result["env_id"])]
        tmp_server.name = result["name"]
        tmp_server.ip = result["ip"]
        tmp_server.os = result["image"]

        tmp_server.cpu = result["cpu"]
        tmp_server.mem = result["memory"]
        tmp_server.disk = result["disk"]

        tmp_server.role = result["role"]
        if result["dept_id"] in pd_dict:
            tmp_server.pd = pd_dict[result["dept_id"]]
        else:
            tmp_server.pd = result["dept_id"]
        tmp_server.desc = result["comments"]

        all_server_infos.append(tmp_server)

    page_server_infos = []
    start = pageNum * pageSize
    limit = pageSize

    filter_total = 0
    cpu_total = 0
    mem_total = 0
    disk_total = 0
    for i in range(0, len(all_server_infos)):

        # 检查服务器是否满足过滤规则
        if need_filter_server(all_server_infos[i], filter_env_name, filter_pd_name, key):
            continue

        # 取分页数据
        if filter_total >= start and filter_total < start + limit:
            page_server_infos.append(all_server_infos[i])

        # 总数量+1
        filter_total += 1

        # 计算统计信息，如果无法转化成正数，则忽略
        try:
            cpu_total += int(all_server_infos[i].cpu)
            mem_total += int(all_server_infos[i].mem)
            disk_total += int(all_server_infos[i].disk)
        except Exception:
            pass

    return filter_total, page_server_infos, cpu_total, mem_total, disk_total


def get_all_env_infos():
    """
    获取所有环境信息
    """
    qate_cursor = get_qate_cursor()

    # 获取qate的所有环境信息
    sql = """
    select distinct env_id from vm
    """
    qate_cursor.execute(sql)
    qate_results = qate_cursor.fetchall()
    qate_cursor.close()

    env_infos = []
    env_infos.append(QatePDInfo("所有环境", "所有环境"))
    for result in qate_results:
        tmp_info = QateEnvInfo()
        tmp_info.id = ENV_NAME_DICT[str(result["env_id"])]
        tmp_info.name = ENV_NAME_DICT[str(result["env_id"])]
        env_infos.append(tmp_info)

    # 加上UAT
    env_infos.append(QateEnvInfo("UAT", "UAT"))
    return env_infos


def get_all_pd_infos():
    """
    获取所有PD信息
    """
    # 获取uat的所有PD信息
    uat_cursor = get_uat_cursor()
    sql = """
    select distinct Pd_id from simplecmdb_server
    """
    uat_cursor.execute(sql)
    uat_results = uat_cursor.fetchall()
    uat_cursor.close()

    names_set = Set()
    for result in uat_results:
        names_set.add(result["Pd_id"])

    # 获取qate的所有PD信息
    qate_cursor = get_qate_cursor()
    sql = """
    select distinct name from auth_group
    """
    qate_cursor.execute(sql)
    qate_results = qate_cursor.fetchall()
    qate_cursor.close()

    for result in qate_results:
        names_set.add(result["name"])

    pd_infos = []
    for name in names_set:
        tmp_info = QatePDInfo()
        tmp_info.id = str(name)
        tmp_info.name = str(name)
        pd_infos.append(tmp_info)

    sorted_pd_infos = sort_by_gbk(pd_infos)

    # 增加所有PD选项到list头部
    sorted_pd_infos.insert(0, QatePDInfo("所有PD", "所有PD"))
    return sorted_pd_infos


def sort_by_gbk(pd_infos):
    """
    将pd信息按照gbk编码排序
    """
    def getKey1(pd_info):
        return pd_info.name.decode("utf-8").encode("GBK")

    # 先按照部门排序，部门内部再按照角色排序
    return sorted(pd_infos, key=getKey1)


def update_server_info(info):
    """
    更新pd信息
    """
    # 如果是UAT的环境，需要去uat表修改
    if info.env == "UAT":
        uat_cursor = get_uat_cursor()
        sql = """
        update simplecmdb_server set Pd_id='%s',Role='%s',Comments='%s'
        where IPAddress='%s'
        """ % (info.pd, info.role, info.desc, info.ip)
        print sql
        uat_cursor.execute(sql)
        uat_cursor.execute("commit")
        uat_cursor.close()
    # 非UAT环境去Qate表里面修改
    else:
        qate_cursor = get_qate_cursor()
        sql = """
        update vm set role='%s',comments='%s'
        where ip='%s' and name='%s'
        """ % (info.role, info.desc, info.ip, info.name)
        print sql
        qate_cursor.execute(sql)
        qate_cursor.execute("commit")
        qate_cursor.close()


def getpageserverinfos(request):
    env = request.POST.get('env').encode("utf-8")
    pd = request.POST.get('pd').encode("utf-8")
    key = request.POST.get('key').encode("utf-8")
    pageNum = int(request.POST.get('page')) - 1
    pageSize = int(request.POST.get('rows'))

    total, page_server_infos, cpu_total, mem_total, disk_total = get_page_server_infos_from_db(env, pd, key, pageNum, pageSize)
    response = json_encode({
        "total": total,
        "rows": page_server_infos,
        "cpu_total": cpu_total,
        "mem_total": mem_total,
        "disk_total": disk_total
    })

    return HttpResponse(response, content_type="application/json")


def getenvnames(request):
    all_env_infos = get_all_env_infos()
    response = json_encode(all_env_infos)
    return HttpResponse(response, content_type="application/json")


def getpdnames(request):
    all_pd_infos = get_all_pd_infos()
    response = json_encode(all_pd_infos)
    return HttpResponse(response, content_type="application/json")


def updateserver(request):
    server = QateServerInfo()
    server.ip = request.POST.get('ip').encode("utf-8")
    server.name = request.POST.get('name').encode("utf-8")
    server.env = request.POST.get('env').encode("utf-8")
    server.pd = request.POST.get('pd').encode("utf-8")
    server.role = request.POST.get('role').encode("utf-8")
    server.desc = request.POST.get('desc').encode("utf-8")

    update_server_info(server)

    response = json_encode({
        "result": "ok"
    })
    return HttpResponse(response, content_type="application/json")


def index(request):
    return render(request, "index.html", {'time': datetime.datetime.now()})
