#! /usr/bin/env python
# vim: set fenc=utf8 ts=4 sw=4 et :
# -----------/lib/systemd/system/ipupdater.service systemd配置---------------
# [Unit]
# Description=update ip config when system start
# After=network-online.target
# 
# [Service]
# Type=simple
# User=root
# ExecStart=python3 /root/ipupdater.py 
# 
# [Install]
# WantedBy=multi-user.target


import socket
import shutil
import re

NTERFACE_PATH = '/etc/network/interfaces'
HOSTS_PATH = '/etc/hosts'
ISSUE_PATH = '/etc/issue'

def getRealNetInfo():
    # defaultGateWay, defaultInterface = ni.gateways()['default'][ni.AF_INET]
    # addressInfo = ni.ifaddresses(defaultInterface)[ni.AF_INET][0]
    # ip = addressInfo['addr']
    # maskBits = IPv4Network('0.0.0.0/'+addressInfo['netmask']).prefixlen
    # return ip, defaultGateWay, maskBits
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip 

def checkIfIpChanged(ip, defaultGateWay):
    shutil.copy(INTERFACE_PATH, INTERFACE_PATH + '.bak')
    targetFile = open(INTERFACE_PATH, "r")
    configText = targetFile.read()

    addressMatch = re.search(' {8}address (.+)\n',configText)
    if addressMatch is None or len(addressMatch.groups()) == 0:
        print("pve静态IP配置文件%s中未找到IP地址信息，配置文件内容:%s" % (NTERFACE_PATH, configText) )
        return False
    configIp = addressMatch.groups()[0][:-3]

    gatewayMatch = re.search(' {8}gateway (.+)\n',configText)
    if gatewayMatch is None or len(gatewayMatch.groups()) == 0:
        print("pve静态IP配置文件%s中未找到默认路由信息，配置文件内容:%s" % (NTERFACE_PATH, configText) )
        return False
    configGateway = gatewayMatch.groups()[0]
    if defaultGateWay == configGateway and ip == configIp:
        return False
    else:
        return True

def updateInterfaces(ip, gateway, maskBits):
    shutil.copy(INTERFACE_PATH, INTERFACE_PATH + '.bak')
    targetFile = open(INTERFACE_PATH, "r+")
    configText = targetFile.read()
    splitRes = re.split(" {8}address .+\n {8}gateway .+\n", configText)
    prepart = splitRes[0]
    postpart = splitRes[1]
    updateConfig = "        address %s/%s\n        gateway %s\n" % (ip, maskBits, gateway)
    print("interfaces updateConfig: %s" % updateConfig)
    newConifg = prepart + updateConfig+ postpart
    print("interfaces newConifg:%s" % newConifg)

    targetFile.seek(0)
    targetFile.write(newConifg)
    targetFile.truncate()
    targetFile.close()

def updateHosts(ip):
    shutil.copy(HOSTS_PATH, HOSTS_PATH + '.bak')
    targetFile = open(HOSTS_PATH, "r+")
    configText = targetFile.read()
    splitRes = re.split("\n.+ ${pve_host}\n", configText)
    print(splitRes)
    prepart = splitRes[0]
    postpart = splitRes[1]
    updateConfig = "\n%s ${pve_host}\n" % ip
    print("----host updateConfig----\n %s" % updateConfig)
    newConifg = prepart + updateConfig+ postpart
    print("----host newConifg----\n%s" % newConifg)

    targetFile.seek(0)
    targetFile.write(newConifg)
    targetFile.truncate()
    targetFile.close()

def updateIssue(ip):
    shutil.copy(ISSUE_PATH, ISSUE_PATH + '.bak')
    targetFile = open(ISSUE_PATH, "r+")
    configText = targetFile.read()
    splitRes = re.split("  https://.+:8006/\n", configText)
    prepart = splitRes[0]
    postpart = splitRes[1]
    updateConfig = "  https://%s:8006/\n" % ip
    print("----issue updateConfig----\n%s" % updateConfig)
    newConifg = prepart + updateConfig+ postpart
    print("----issue newConifg----\n%s" % newConifg)

    targetFile.seek(0)
    targetFile.write(newConifg)
    targetFile.truncate()
    targetFile.close()


if __name__ == "__main__":
    print('ipupdater start.')
    ip = getRealNetInfo()
    print("ip:%s" % ip)
    updateHosts(ip)
    updateIssue(ip)