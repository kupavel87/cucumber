import json

from celery import Celery
from flask import current_app

from webapp.celery.utils import check_voucher, get_voucher
from webapp.db import db
from webapp.purchase.models import Process_Purchase

celery = Celery(__name__, config_source='webapp.config')


@celery.task
def Check_Voucher(process_id):
    process = Process_Purchase.query.filter_by(id=process_id).first()
    if process:
        status_code = check_voucher(fn=process.fn, fd=process.fd, fp=process.fp, fdate=process.fdate, fsum=process.fsum)
        print("Check voucher id={}, status code={}".format(process.id, status_code))
        if status_code == 204:
            process.attempt = 1
            Get_Voucher_Detail.apply_async([process_id], countdown=10)
        else:
            process.attempt = process.max_attempt
        db.session.commit()


@celery.task
def Get_Voucher_Detail(process_id):
    process = Process_Purchase.query.filter_by(id=process_id).first()
    if process.attempt < process.max_attempts:
        answer = get_voucher(fn=process.fn, fd=process.fd, fp=process.fp)
        print("Voucher id={}, get detail={}, attempt={}".format(process.id, bool(answer), process.attempt))
        if answer:
            print(process.link)
            with open(process.link, 'w', encoding='utf-8') as f:
                json.dump(answer, f)
            process.attempt = -1
        else:
            process.attempt += 1
            Get_Voucher_Detail.apply_async([process_id], countdown=10)
        db.session.commit()
