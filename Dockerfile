FROM python:3.8
WORKDIR /app
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install flask tinydb flask-cors openpyxl
