# coding:utf-8
from json import JSONEncoder, JSONDecoder, dumps


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
