from flask import Flask
from flask_cors import CORS

# 导入各个业务模块的蓝图
from modules.user import user_bp
from modules.post import post_bp

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

# 注册所有业务模块路由
app.register_blueprint(user_bp)
app.register_blueprint(post_bp)

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health():
    return {"code": 0, "msg": "服务运行正常", "data": None}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
