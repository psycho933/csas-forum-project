from flask import Blueprint, request
from common.db import query_one, execute
from common.response import success, error
from common.security import encrypt_password, verify_password
from datetime import datetime

# 创建用户模块蓝图，url前缀统一为 /api/user
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# 1. 用户注册
@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        account = data.get('account')
        password = data.get('password')
        nickname = data.get('nickname', account)

        if not account or not password:
            return error(-1, "账号和密码不能为空")

        # 校验账号唯一性
        check_sql = "SELECT user_id FROM `user` WHERE account = %s"
        if query_one(check_sql, (account,)):
            return error(-2, "账号已存在")

        # 加密密码
        password_hash = encrypt_password(password)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 插入用户
        insert_sql = """
        INSERT INTO `user` (account, password_hash, nickname, exp, `level`, role, status, create_time)
        VALUES (%s, %s, %s, 0, 1, 0, 0, %s)
        """
        user_id = execute(insert_sql, (account, password_hash, nickname, now))
        return success({"user_id": user_id}, "注册成功")
    except Exception as e:
        print("注册错误：", e)
        return error(-5, "系统繁忙，请稍后再试")

# 2. 用户登录
@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        account = data.get('account')
        password = data.get('password')

        if not account or not password:
            return error(-1, "账号和密码不能为空")

        sql = "SELECT * FROM `user` WHERE account = %s"
        user = query_one(sql, (account,))

        if not user:
            return error(-2, "账号不存在")
        if user['status'] == 1:
            return error(-4, "账号已被封禁")
        if not verify_password(user['password_hash'], password):
            return error(-3, "密码错误")

        user_info = {
            "user_id": user['user_id'],
            "nickname": user['nickname'],
            "role": user['role'],
            "level": user['level']
        }
        return success(user_info, "登录成功")
    except Exception as e:
        print("登录错误：", e)
        return error(-5, "系统繁忙，请稍后再试")
