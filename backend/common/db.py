import pymysql

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "chenqiyi",  # 换成你自己的密码
    "database": "csas_forum",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "init_command": "SET NAMES utf8mb4"
}

def get_db():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def query_one(sql, args=None):
    """查询单条记录"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(sql, args)
        return cursor.fetchone()
    finally:
        db.close()

def query_all(sql, args=None):
    """查询多条记录"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(sql, args)
        return cursor.fetchall()
    finally:
        db.close()

def execute(sql, args=None):
    """执行增删改操作，支持事务"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(sql, args)
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
