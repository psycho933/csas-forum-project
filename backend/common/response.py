from flask import jsonify

def success(data=None, msg="操作成功"):
    """统一成功返回"""
    return jsonify({
        "code": 0,
        "msg": msg,
        "data": data
    })

def error(code=-1, msg="操作失败", data=None):
    """统一失败返回"""
    return jsonify({
        "code": code,
        "msg": msg,
        "data": data
    })
