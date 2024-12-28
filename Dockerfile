FROM python:3.12

LABEL auther="liuzhiyi"

ENV MYPATH=/app

COPY . $MYPATH

WORKDIR $MYPATH

RUN pip install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD python /app/main.py