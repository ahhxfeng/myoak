# coding-utf-8

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin

from db import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(64), nullable=False,
                       server_default="normal")  # normal, delete
    telephone = db.Column(db.String(64), unique=True, server_default="")
    wallet = db.relationship("Wallet", backref="wallets")
    rig = db.relationship("Rig", backref="rigs")

    @property
    def password():
        raise AttributeError("password is not a readable arrtribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Rig(db.Model):
    __tablename__ = "rigs"
    MAX_RIG_NAME = 64
    MAX_NOTES = 4096

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    device_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(MAX_RIG_NAME), nullable=False, server_default='')
    notes = db.Column(db.String(MAX_NOTES), nullable=False, server_default='')
    status = db.Column(db.String(32), nullable=False, server_default='new') # new, normal, delete
    failures = db.Column(db.String(1024), nullable=False, server_default='{}') # disconnect: 900, gpu_failure: 1, gpu_temp: 1
    power_status = db.Column(db.String(1024), nullable=True, server_default='{"mb_state": "on", "mb_time": 0}') # mb_time: timestamp, mb_state: on/off/reboot
    last_file = db.Column(db.String(128), nullable=False, server_default='0000000000.gz')

    # need to know more ?
    __table_args__ = (
        db.Index('i_user_status', user_id, status),
    )


class RigGroup(db.Model):
    __tablename__ = "rig_groups"
    MAX_GROUP_NAME = 64
    MAX_NOTES = 4096
    MAX_CONFIG = 4096

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(MAX_GROUP_NAME), nullable=False, server_default='')
    notes = db.Column(db.String(MAX_NOTES), nullable=False, server_default='')
    status = db.Column(db.String(32), nullable=False, server_default='normal') # normal, delete

    # config是json, 包含type, main_pool, main_protocol, spare_pool, spare_protocol
    config = db.Column(db.String(MAX_CONFIG), nullable=False, server_default='{}')


class RigFailures(db.Model):
    __tablename__ = "rig_failures"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    error_time = db.Column(db.DateTime, nullable=False)  # 对齐到小时
    system_error = db.Column(db.Integer, nullable=False, server_default='0')
    python_error = db.Column(db.Integer, nullable=False, server_default='0')
    normal_claymore_error = db.Column(db.Integer, nullable=False, server_default='0')
    zec_claymore_error = db.Column(db.Integer, nullable=False, server_default='0')
    bminer_error = db.Column(db.Integer, nullable=False, server_default='0')
    

    __table_args__ = (
        db.UniqueConstraint(device_id, error_time, name='u_device_time'),
    )


class Wallet(db.Model):
    __tablename__ = "wallets"
    MAX_WALLET_NAME = 64
    MAX_WALLET_ADDRESS = 128

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullalbe=False)
    wallet_name = db.Column(db.String(MAX_WALLET_NAME), nullable=False, server_default='')
    wallet_address = db.Column(db.String(MAX_WALLET_ADDRESS), nullable=False)
    wallet_type = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(32), nullable=False, server_default='normal') # normal, delete


class GroupWallet(db.Model):
    __tablename__ = 'oak_group_wallet'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey("oak_rig_group.id"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("oak_wallet.id"), nullable=False)

    # 反链
    rig_group = db.relationship("RigGroup", backref=db.backref("group_wallet"))
    wallet = db.relationship("Wallet", backref=db.backref("group_wallet"))


class DigProfit(db.Model):
    __tablename__ = 'dig_profit'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wallet_type = db.Column(db.String(64), unique=True, nullable=False)
    profit_rmb = db.Column(db.Float, nullable=False)  # 每Mh/s一天的收益
    dollar_rate = db.Column(db.Float, nullable=False)  # $1 = ? CNY
  
class RigGroupStatsHourly(db.Model):
    """
    rig_group统计信息的小时级上卷-与wallet无关的部分
    """
    __tablename__ = 'oak_rig_group_stats_hourly'
    
    # 键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_time = db.Column(db.DateTime, nullable=False)  # 对齐到小时
    rig_group_id = db.Column(db.Integer, db.ForeignKey("oak_rig_group.id"), nullable=False)
    
    # 值
    sample_count = db.Column(db.Integer, nullable=False, default=0)
    rig_count_recent = db.Column(db.Integer, nullable=False, default=0)
    rig_count_average = db.Column(db.Integer, nullable=False, default=0)
    rig_failure_count_recent = db.Column(db.Integer, nullable=False, default=0)
    rig_failure_count_average = db.Column(db.Integer, nullable=False, default=0)
    max_temperature_recent = db.Column(db.Integer, nullable=False, default=0)
    max_temperature_average = db.Column(db.Integer, nullable=False, default=0)
    rig_online_count_recent = db.Column(db.Integer, nullable=False, default=0)
    rig_online_count_average = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        db.UniqueConstraint(log_time, rig_group_id, name='i_group_time'),
    )

    def clear(self, rig_group_id, log_time):
        self.log_time = log_time
        self.rig_group_id = rig_group_id
        self.sample_count = 0
        self.rig_count_recent = 0
        self.rig_count_average = 0
        self.rig_failure_count_recent = 0
        self.rig_failure_count_average = 0
        self.max_temperature_recent = 0
        self.max_temperature_average = 0
        self.rig_online_count_recent = 0
        self.rig_online_count_average = 0

class RigGroupWalletStatsHourly(db.Model):
    """
    rig_group统计信息的小时级上卷-与wallet有关的部分
    """
    __tablename__ = 'oak_rig_group_wallet_stats_hourly'
    
    # 键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_time = db.Column(db.DateTime, nullable=False)  # 对齐到小时
    rig_group_id = db.Column(db.Integer, db.ForeignKey("oak_rig_group.id"), nullable=False)
    wallet_type = db.Column(db.String(64), nullable=False)

    # 值
    sample_count = db.Column(db.Integer, nullable=False, default=0)
    sum_hashrate_recent = db.Column(db.Integer, nullable=False, default=0)
    sum_hashrate_average = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        db.UniqueConstraint(log_time, rig_group_id, wallet_type, name='i_group_time_wallet'),
    )

    def clear(self, rig_group_id, log_time, wallet_type):
        self.log_time = log_time
        self.rig_group_id = rig_group_id
        self.wallet_type = wallet_type
        self.sample_count = 0
        self.sum_hashrate_recent = 0
        self.sum_hashrate_average = 0




