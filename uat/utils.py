# coding:utf-8
import traceback
from json import JSONEncoder, JSONDecoder, dumps
from django.http import HttpResponse


class Encoder(JSONEncoder):
    '''
    重载JSONEncoder，让其可以解析class
    '''
    def default(self, obj):
        return obj.__dict__


def json_encode(obj):
    '''
    针对json库不方便的问题，进行的重写
    '''
    return Encoder().encode(obj)


def json_decode(json):
    '''
    封装JSON的decode方法
    @param json String json格式数据
    @return Dict 返回字典
    '''
    return JSONDecoder().decode(json)


def json_dumps(d):
    '''
    将Dict对象转为JSON String
    '''
    return dumps(d, ensure_ascii=False)


def send_mail(subject, text_content, from_email, to):
    """
    发送邮件
    """
    pass


def send_http_exception(func):
    """
    捕获所有异常，将异常以http形式回复
    """
    def warp(*args, **kwargs):
        """
        warp
        """
        try:
            return func(*args, **kwargs)
        except Exception:
            bt = traceback.format_exc()
            response = json_encode({
                "exception": bt
            })
            return HttpResponse(response, content_type="application/json", status=500)

    return warp
