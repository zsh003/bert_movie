@echo off
echo 正在初始化数据库...
cd backend
python scripts/init_db.py

echo 正在启动后端服务器...
start python -m uvicorn main:app --reload

echo 正在启动前端开发服务器...
cd ../frontend
npm install
npm run dev

echo 系统启动完成！
echo 后端API地址：http://localhost:8000
echo 前端页面地址：http://localhost:5173
echo 默认管理员账号：admin
echo 默认管理员密码：admin123 