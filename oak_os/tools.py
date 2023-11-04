# coding = utf-8

# coding: utf-8
import subprocess
import logging

warn_logger = logging.getLogger("miner-warn")
info_logger = logging.getLogger("miner-info")


def read_account(path):
    """
    @return None 如果没有设置账号
    """
    try:
        with open(path, 'r') as f:
            account = ''
            rig_name = ''
            for line in f.readlines():
                line = line.strip()
                # 略过空行和注释行
                if line == '':
                    continue
                if line[0] == '#':
                    continue
                if account == '':
                    account = line[:21]
                elif rig_name == '':
                    rig_name = line[:21]
            # 空文本情况返回None
            if account == '':
                account = None
            return account, rig_name
    except Exception as e:
        warn_logger.exception(e)
        info_logger.exception(e)
        return None, None

def read_tag(path):
    try:
        with open(path, 'r') as f:
            tag_name = ''
            for line in f.readlines():
                line = line.strip()
                #略过空行和注释行
                if line == '':
                    continue
                if line[0] == '#':
                    continue
                if tag_name == '':
                    tag_name = line[:21]
            if tag_name == '':
                tag_name = 'default'
            return tag_name
    except Exception as e:
        warn_logger.exception(e)
        info_logger.exception(e)
        return 'default'

def system(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    return stdout, p.returncode
if __name__ == '__main__':
    x, y = read_account('account.txt')
    print (x, y)
