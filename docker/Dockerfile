FROM python:3-alpine

WORKDIR /program
COPY python.ini /etc/supervisor/
COPY requirements.txt /program/requirements.txt
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
    && apk update \
    && apk add tzdata \
    && apk add mysql-client \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apk add supervisor \
    && pip install --upgrade setuptools -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && echo_supervisord_conf > /etc/supervisord.conf \
    && sed -i '$a \[include]' /etc/supervisord.conf && sed -i '$a \files = /etc/supervisor/*.ini' /etc/supervisord.conf
#ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]