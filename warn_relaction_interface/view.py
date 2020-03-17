from django.http import HttpResponse
from . import settings
from .core.warn_realation import warn_relation
from .core import systen_unit as su
import threading
import os
import re
import json
import logging

logger = logging.getLogger('log')


def start(req):
    return HttpResponse(json.dumps({
        "code": 200,
        "msg": "interface alive",
        "body": {
            "isalive": 1
        }
    }))


def warn_realtion(req):
    work_id = su.get_unique_str()
    if req.method == "POST" and req.POST.get("data","") !="":
        try:
            down_un = su.download_unit()

            req_para=json.loads(str(req.POST.get("data", "")))
            warn_data_url = str(req_para["warn_data_url"])
            if su.isURL(warn_data_url):
                min_support = str(req_para['min_support'])
                f1 = re.match(r"[0]\.\d+", min_support)
                if f1 != None and (f1.group() == min_support):
                    min_support = float(min_support)

                min_confidence = str(req_para['min_confidence'])
                f2 = re.match(r"[0]\.\d+", min_confidence)
                if f2 != None and (f2.group() == min_confidence):
                    min_confidence = float(min_confidence)
                time_window = str(req_para['time_window'])
                f3 = re.match(r"\d+", time_window)
                if f3 != None and (f3.group() == time_window):
                    time_window = int(time_window)
                save_url = os.path.join(settings.MEDIA_ROOT, work_id + "." + str(warn_data_url).split(".")[-1])
                wr = warn_relation(min_support, min_confidence, time_window)

                down_thread = threading.Thread(target=down_un.download_file, args=(warn_data_url, save_url, work_id))
                core_thread = threading.Thread(target=wr.file_deal, args=(save_url, work_id))
                down_thread.start()
                down_thread.join()
                if down_un.get_result():
                    logger.info("[" + work_id + "]:请求成功，任务开始启动")
                    core_thread.start()
                    return HttpResponse(json.dumps({
                        "code": 200,
                        "msg": "Check successed.",
                        "body": {
                            "ret": "4000",
                            "pre_time": str(
                                down_un.get_len() / 4000 + down_un.get_len() / 300000 + down_un.get_len() / 25000),
                            "work_id": work_id
                        }
                    }))
                else:
                    logger.error("[" + work_id + "]:没有告警文件下载url，或者告警文件url不合法，下载地址为" + str(warn_data_url))
                    return HttpResponse(json.dumps({
                        "code": 201,
                        "msg": "warn file download address error",
                        "body": {
                            "ret": "4003"
                        }
                    }))
            else:
                logger.error("[" + work_id + "]:告警文件下载失败，或者告警文件不符合要求，下载地址为" + str(warn_data_url))
                return HttpResponse(json.dumps({
                    "code": 201,
                    "msg": "warn data download failed",
                    "body": {
                        "ret": "4001"
                    }
                }))
        except Exception as e:
            logger.error("[" + work_id + "]:" + str(e))
            return HttpResponse(json.dumps({
                "code": 500,
                "msg": "unknown exception",
                "body": {
                    "ret": "4002"
                }
            }))
    else:
        return HttpResponse(json.dumps({
            "code": 201,
            "msg": "wrong request type",
            "body": {
                "ret": "4004"
            }
        }))


def get_resu_process(req):
    if req.method == "POST" and req.POST.get("data","") !="":
        req_para=json.loads(str(req.POST.get("data","")))
        work_id = str(req_para["work_id"])
        resu_file_url = os.path.join(settings.DWON_RESU_URL, work_id + ".csv")
        process_file_url = os.path.join(settings.PROCESS_URL, "process_" + work_id)
        if os.path.exists(resu_file_url):
            return HttpResponse(json.dumps({
                "code": 200,
                "msg": "task complete",
                "body":{
                    "ret": "5000",
                    "process": "100%"
                }
            }))
        else:
            if os.path.exists(process_file_url):
                with open(process_file_url, 'r') as process:
                    lines = process.readlines()
                if len(lines) >= 2:
                    current_process = str(lines[-1]).split("：")[-1].strip()
                    if current_process == "100%":
                        current_process = "98.7%"
                    return HttpResponse(json.dumps({
                        "code": 200,
                        "msg": "task in progress",
                        "body":{
                            "ret": "5000",
                            "process": current_process
                        }
                    }))
                else:
                    return HttpResponse(json.dumps({
                        "code": 200,
                        "msg": "task in progress",
                        "body": {
                            "ret": "5000",
                            "process": "0%"
                        }

                    }))

            else:
                return HttpResponse(json.dumps({
                    "code": 201,
                    "msg": "work err,please upload file again to start task",
                    "body": {
                        "ret": "5001",
                        "process": "0%"
                    }
                }))
    else:
        return HttpResponse(json.dumps({
            "code": 201,
            "msg": "wrong request type",
            "body": {
                "ret": "5002",
                "process": "0%"
            }
        }))
