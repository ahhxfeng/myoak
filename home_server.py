#! /usr/bin/env python
#coding=utf-8

__author__ = "TF00"
__version__ = "1.0.0"

import argparse
import json
import time
from html import escape

from flask import jsonify
# from oak_home import config
from oak_home import config
from oak_home.init_app import create_app
from oak_home.init_db import db
from oak_home.logger import get_logger
from oak_home.models import *

app = create_app("./config.py")
db.init_app(app=app)


def _redis_client():
    import redis

    return redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        decode_responses=True,
    )


def _json_load(value, default=None):
    if value in (None, ""):
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _age_text(age):
    if age is None:
        return "未上报"
    if age < 60:
        return "{} 秒前".format(age)
    if age < 3600:
        return "{} 分钟前".format(age // 60)
    return "{} 小时前".format(age // 3600)


def _machine_from_redis(rig):
    data = _redis_client().hgetall("rig:" + rig.device_id)
    machine = _json_load(data.get("machine"), {}) or {}
    return {
        "device_id": rig.device_id,
        "name": data.get("rig_name") or rig.name,
        "status": rig.status,
        "tag_name": _json_load(data.get("tag_name"), data.get("tag_name") or "default"),
        "last_report_ts": int(data.get("ts") or 0),
        "last_report_age": int(time.time()) - int(data.get("ts") or 0) if data.get("ts") else None,
        "cpu": machine.get("cpu") or _json_load(data.get("cpu"), {}),
        "memory": machine.get("memory") or _json_load(data.get("memory"), {}),
        "gpus": machine.get("gpus") or _json_load(data.get("gpus"), []),
        "machine": machine,
    }


def _machines_for_account(account):
    user = User.query.filter_by(user_name=account, status="normal").first_or_404()
    rigs = Rig.query.filter_by(user_id=user.id).filter(Rig.status != "delete").all()
    return [_machine_from_redis(rig) for rig in rigs]


@app.route("/api/machines/<account>")
def api_machines(account):
    return jsonify({
        "code": 0,
        "message": "success",
        "data": _machines_for_account(account),
    })


@app.route("/machines/<account>")
def machines_page(account):
    machines = _machines_for_account(account)
    rows = []
    for machine in machines:
        cpu = machine.get("cpu") or {}
        memory = machine.get("memory") or {}
        gpus = machine.get("gpus") or []
        memory_total = memory.get("total") or 0
        memory_used = memory.get("used") or 0
        rows.append("""
            <tr>
                <td>{name}<div class="muted">{device}</div></td>
                <td>{tag}</td>
                <td>{cpu_usage}%<div class="muted">{cores} cores</div></td>
                <td>{mem_usage}%<div class="muted">{mem_used} / {mem_total} GB</div></td>
                <td>{gpu_count}<div class="muted">{gpu_names}</div></td>
                <td>{last_seen}</td>
            </tr>
        """.format(
            name=escape(machine.get("name") or "未命名机器"),
            device=escape(machine.get("device_id") or ""),
            tag=escape(str(machine.get("tag_name") or "default")),
            cpu_usage=cpu.get("usage_percent") if cpu.get("usage_percent") is not None else "-",
            cores=cpu.get("core_count") or "-",
            mem_usage=memory.get("usage_percent") if memory.get("usage_percent") is not None else "-",
            mem_used=round(memory_used / 1024 / 1024 / 1024, 2) if memory_used else "-",
            mem_total=round(memory_total / 1024 / 1024 / 1024, 2) if memory_total else "-",
            gpu_count=len(gpus),
            gpu_names=escape(", ".join([gpu.get("name", "GPU") for gpu in gpus]) or "无显卡数据"),
            last_seen=_age_text(machine.get("last_report_age")),
        ))

    body = "\n".join(rows) or '<tr><td colspan="6" class="empty">暂无机器</td></tr>'
    return """
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>我的机器 - {account}</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #1f2937; background: #f6f7f9; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 32px 20px; }}
    h1 {{ margin: 0 0 20px; font-size: 28px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e5e7eb; }}
    th, td {{ padding: 14px 16px; text-align: left; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
    th {{ font-size: 13px; color: #4b5563; background: #f9fafb; }}
    .muted {{ margin-top: 4px; color: #6b7280; font-size: 12px; }}
    .empty {{ text-align: center; color: #6b7280; }}
  </style>
</head>
<body>
  <main>
    <h1>{account} 的机器</h1>
    <table>
      <thead>
        <tr>
          <th>机器</th>
          <th>标签</th>
          <th>CPU</th>
          <th>内存</th>
          <th>显卡</th>
          <th>最后上报</th>
        </tr>
      </thead>
      <tbody>{body}</tbody>
    </table>
  </main>
</body>
</html>
    """.format(account=escape(account), body=body)

# command line to parser start and db operation
def command_line():
    parser = argparse.ArgumentParser(prog="home_server", description="the flask server ")
    Choices = ["runserver", "create_db", "drop_db"]
    parser.add_argument("command", type=str, choices=Choices)
    args = parser.parse_args()

    match args.command:
        case "runserver":
            # runserver 
            app.run(host="0.0.0.0", port=8080, debug=True)
        case "create_db":
            with app.app_context():
                db.create_all()
        case "drop_db":
            with app.app_context():
                db.drop_all()
        case _:
            print("bad command, please choose above{}".format(Choices))
       


if __name__ == "__main__":
    logger = get_logger("main_log", "main.log")
    command_line()
