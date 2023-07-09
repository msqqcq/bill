from tinydb import TinyDB, Query
from flask import Flask
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def holle():
    return datetime.now().strftime("%Y%m%d")


@app.route('/test')
def test():
    # 创建或打开数据库文件
    db = TinyDB("/app/db/db.json")

    # 创建表格
    users = db.table("users")

    # 插入数据
    users.insert({"name": "Alice", "age": 25})
    users.insert({"name": "Bob", "age": 30})

    # 关闭数据库（可选）
    db.close()
    return "OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6060)
