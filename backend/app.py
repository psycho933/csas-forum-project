from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 中文正常显示
CORS(app)  # 加上这一行，开启跨域支持
# ========== 数据库配置（对应CSCI-8公共基础库）==========
def get_db():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='chenqiyi',  # 你的MySQL密码
        database='csas_forum',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        init_command='SET NAMES utf8mb4'
    )
    return conn

# ========== 统一返回格式（对应CSCI-8统一报文规范）==========
def success(data=None, msg="操作成功"):
    return jsonify({"code": 0, "msg": msg, "data": data})

def error(code=-1, msg="操作失败"):
    return jsonify({"code": code, "msg": msg, "data": None})

# ==================== CSCI-3 用户账号管理包 ====================

# 1. 用户注册接口
@app.route('/api/user/register', methods=['POST'])
def user_register():
    """对应文档CSCI-3：用户注册功能"""
    try:
        data = request.get_json()
        account = data.get('account')
        password = data.get('password')
        nickname = data.get('nickname', account)

        # 参数校验
        if not account or not password:
            return error(-1, "账号和密码不能为空")

        db = get_db()
        cursor = db.cursor()

        # 校验账号唯一性
        check_sql = "SELECT user_id FROM `user` WHERE account = %s"
        cursor.execute(check_sql, account)
        if cursor.fetchone():
            db.close()
            return error(-2, "账号已存在")

        # 密码加盐哈希后存储
        password_hash = generate_password_hash(password)
        now = datetime.now()

        # 插入用户数据
        insert_sql = """
        INSERT INTO `user` (account, password_hash, nickname, exp, level, role, status, create_time)
        VALUES (%s, %s, %s, 0, 1, 0, 0, %s)
        """
        cursor.execute(insert_sql, (account, password_hash, nickname, now))
        db.commit()
        db.close()

        return success({"user_id": cursor.lastrowid}, "注册成功")
    except Exception as e:
        print("注册错误：", e)
        return error(-5, "系统繁忙，请稍后再试")

# 2. 用户登录接口
@app.route('/api/user/login', methods=['POST'])
def user_login():
    """对应文档CSCI-3：用户登录功能"""
    try:
        data = request.get_json()
        account = data.get('account')
        password = data.get('password')

        if not account or not password:
            return error(-1, "账号和密码不能为空")

        db = get_db()
        cursor = db.cursor()

        # 查询账号
        sql = "SELECT * FROM `user` WHERE account = %s"
        cursor.execute(sql, account)
        user = cursor.fetchone()
        db.close()

        if not user:
            return error(-2, "账号不存在")
        if user['status'] == 1:
            return error(-4, "账号已被封禁")
        # 校验密码哈希
        if not check_password_hash(user['password_hash'], password):
            return error(-3, "密码错误")

        # 返回用户信息（后续可扩展token）
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

# ==================== CSCI-1 帖子业务管理包 ====================

# 3. 帖子列表接口（原有功能保留）
@app.route('/api/post/list', methods=['GET'])
def get_post_list():
    try:
        db = get_db()
        cursor = db.cursor()
        sql = """
        SELECT p.post_id, p.title, p.like_count, p.create_time, u.nickname
        FROM post p
        LEFT JOIN `user` u ON p.user_id = u.user_id
        WHERE p.status = 0
        ORDER BY p.create_time DESC
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        db.close()
        return success(result)
    except Exception as e:
        print("帖子列表错误：", e)
        return error(-5, "系统繁忙，请稍后再试")

# 4. 帖子发布接口
@app.route('/api/post/publish', methods=['POST'])
def post_publish():
    """对应文档CSCI-1-1：帖子发布子模块"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        title = data.get('title')
        content = data.get('content')
        plate_id = data.get('plate_id', 1)
        tag_id = data.get('tag_id', 1)

        # 参数校验
        if not user_id or not title or not content:
            return error(-1, "用户ID、标题、正文不能为空")

        db = get_db()
        cursor = db.cursor()
        now = datetime.now()

        # 插入帖子
        insert_sql = """
        INSERT INTO post (user_id, plate_id, tag_id, title, content, is_essence, hot_value, reply_count, like_count, status, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, 0, 0, 0, 0, 0, %s, %s)
        """
        cursor.execute(insert_sql, (user_id, plate_id, tag_id, title, content, now, now))
        db.commit()
        post_id = cursor.lastrowid

        # 发帖+10经验（对应文档经验规则）
        update_exp_sql = "UPDATE `user` SET exp = exp + 10 WHERE user_id = %s"
        cursor.execute(update_exp_sql, user_id)
        db.commit()
        db.close()

        return success({"post_id": post_id}, "发布成功")
    except Exception as e:
        print("发帖错误：", e)
        return error(-5, "系统繁忙，请稍后再试")

# 5. 帖子详情接口
@app.route('/api/post/detail', methods=['GET'])
def get_post_detail():
    """对应文档CSCI-1：帖子详情查询"""
    try:
        post_id = request.args.get('post_id')
        if not post_id:
            return error(-1, "帖子ID不能为空")

        db = get_db()
        cursor = db.cursor()
        sql = """
        SELECT p.*, u.nickname, u.level
        FROM post p
        LEFT JOIN `user` u ON p.user_id = u.user_id
        WHERE p.post_id = %s AND p.status = 0
        """
        cursor.execute(sql, post_id)
        detail = cursor.fetchone()
        db.close()

        if not detail:
            return error(-2, "帖子不存在或已删除")
        return success(detail)
    except Exception as e:
        print("帖子详情错误：", e)
        return error(-5, "系统繁忙，请稍后再试")

# ========== 启动服务 ==========
if __name__ == '__main__':
    app.run(debug=True, port=5000)
