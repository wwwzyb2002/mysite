# coding:utf-8
from django.http import HttpResponse
from uat.utils import json_encode, send_mail, send_http_exception


def apply(request):
    """
    申请机器的请求处理函数
    """
    # 获取请求的参数
    request.POST.get('user').encode("utf-8")

    # 插入到数据库中

    # 发送邮件
    subject = "你好"
    text_content = "Hello"
    from_email = "uatinfo@ctrip.com"
    to = ["OPS_Qate@Ctrip.com"]
    send_mail(subject, text_content, from_email, to)

    # 回复成功消息
    response = json_encode({
        "result": True
    })

    return HttpResponse(response, content_type="application/json")


def getunresolvedapply(request):
    """
    获取所有未处理的申请
    """
    # 从数据库中读取所有未处理的申请
    response = json_encode({
        "result": True
    })

    return HttpResponse(response, content_type="application/json")


def getresolvedapply(request):
    """
    获取所有已处理的申请
    """
    # 从数据库中读取所有处理过的申请
    response = json_encode({
        "result": True
    })

    return HttpResponse(response, content_type="application/json")


def audit(request):
    """
    审核申请机器的请求
    """
    # 
    response = json_encode({
        "result": True
    })

    return HttpResponse(response, content_type="application/json")


def getallservers(request):
    """
    获取所有创建好的机器
    """
    response = json_encode({
        "result": True
    })

    return HttpResponse(response, content_type="application/json")
