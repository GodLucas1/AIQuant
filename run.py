import os
from app import create_app
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )