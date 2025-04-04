FROM python:3.9-slim

RUN pip install requests

COPY auto_merge.py /auto_merge.py
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]