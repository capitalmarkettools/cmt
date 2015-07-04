#!/bin/bash
echo "cron_batch.sh start"
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/lib/python2.7/dist-packages/django/bin:/home/cmt/cmt:/home/cmt:$PATH
export PYTHONPATH=/home/cmt/cmt:/usr/local/lib/QuantLib-SWIG-1.1/Python/QuantLib:/home/cmt:$PYTHONPATH
export USER=cmt
export MAIL=/var/mail/cmt
export PWD=/home/cmt
export DJANGO_SETTINGS_MODULE=settings
python /home/cmt/cmt/misc/batch.py > /tmp/cmt_batch.out
echo "cron_batch.sh end"