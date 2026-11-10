from flask import Blueprint, request
from common.db import query_one, query_all, execute
from common.response import success, error
from datetime import datetime

# 创建帖子模块蓝图，url前缀统一为 /api/post
post_bp = Blueprint('post', __name__, url_prefix='/api/post')

# 1. 帖子列表
@post_bp.route('/list', methods=['GET'])
def get_list():
    try:
        sql = """
        SELECT p.post_id, p.title, p.like_count, p.create_time, u.nickname
        FROM post p
        LEFT JOIN `user` u ON p.user_id = u.user_id
        WHERE p.status = 0
        ORDER BY p.create_time DESC
        """
        result = query_all(sql)
        return success(result)
    except Exception as e:
        print("帖子列表错误：", e)
        return error(-5, "系统繁忙，请稍后再试")

# 2. 帖子详情
@post_bp.route('/detail', methods=['GET'])
def get_detail():
    try:
        post_id = request.args.get('post_id')
        if not post_id:
            return error(-1, "帖子ID不能为空")

        sql = """
        SELECT p.*, u.nickname, u.level
        FROM post p
        LEFT JOIN `user` u ON p.user_id = u.user_id
        WHERE p.post_id = %s AND p.status = 0
        """
        detail = query_one(sql, (post_id,))
        if not detail:
            return error(-2, "帖子不存在或已删除")
        return success(detail)
    except Exception as e:
        print("帖子详情错误：", e)
        return error(-5, "系统繁忙，请稍后再试")

# 3. 发布帖子
@post_bp.route('/publish', methods=['POST'])
def publish():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        title = data.get('title')
        content = data.get('content')
        plate_id = data.get('plate_id', 1)
        tag_id = data.get('tag_id', 1)

        if not user_id or not title or not content:
            return error(-1, "用户ID、标题、正文不能为空")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_sql = """
        INSERT INTO post (user_id, plate_id, tag_id, title, content, is_essence, hot_value, reply_count, like_count, status, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, 0, 0, 0, 0, 0, %s, %s)
        """
        post_id = execute(insert_sql, (user_id, plate_id, tag_id, title, content, now, now))

        # 发帖+10经验，对应文档经验规则
        exp_sql = "UPDATE `user` SET exp = exp + 10 WHERE user_id = %s"
        execute(exp_sql, (user_id,))

        return success({"post_id": post_id}, "发布成功")
    except Exception as e:
        print("发帖错误：", e)
        return error(-5, "系统繁忙，请稍后再试")
