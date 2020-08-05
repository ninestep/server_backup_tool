FROM python:3-alpine

WORKDIR /program
COPY program /program
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
    && apk update \
    && apk add tzdata \
    && apk add mysql-client \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apk add supervisor \
    && pip install --upgrade setuptools -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT ["python", "main.py"]