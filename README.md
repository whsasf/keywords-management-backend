# keywords-management-backend

1. 克隆到本地
```
git clone https://github.com/whsasf/keywords-management-backend.git
```
2. 安装依赖, 确保python >=3.6
```
pip3 install -r requirements.txt
```
3. 确保mongodb 已经启动(port:27017)
4. 本地启动：
```
uvicorn main:app --reload --port 3000  --host 0.0.0.0
```