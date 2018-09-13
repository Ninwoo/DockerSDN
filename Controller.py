import random
import subprocess
import logging
import time


class Controller:
    def __init__(self, controller_ip, controller_port):
        self.controller_ip = controller_ip;
        self.controller_port = controller_port
        self.dockerid_to_port = {}
        #logging.basicConfig(filename="Controller.log", level=logging.DEBUG)


    def createDocker(self, number):
        '''创建Docker容器'''
        logging.info("Start to generate containers!")
        for i in range(number):
            cmd = 'docker run -d -i --name Router%d --net=none --privileged alpine sh' % i
            (status, output) = subprocess.getstatusoutput(cmd)
            if 1 == status:
                # do something to fix the error
                logging.error("Failed to generate containers!")
                return False
            else:
                self.dockerid_to_port.setdefault(output, {})
        logging.info("Finished generating containers!")
        return True


    def generateIp(self):
        pass


    def generateRandomMac(self):
        '''生成随机的MAC地址'''
        tmp = '00:00:00:{0}:{1}:{2}'

        return tmp.format(''.join(random.sample('0123456789abcdef', 2)),
                ''.join(random.sample('0123456789abcdef', 2)),
                ''.join(random.sample('0123456789abcdef', 2)))


    def removeDocker(self):
        '''删除Docker容器'''
        logging.info("Start to delete containers!")
        for dockerid in self.dockerid_to_port.keys():
            # 不安全的强制删除
            cmd = 'docker rm -f %s' % dockerid
            (status, output) = subprocess.getstatusoutput(cmd)
            if 1 == status:
                logging.error("Failed to delete containers!  %s" % output)
                exit(1)
            # del(self.dockerid_to_port[dockerid])
        logging.info("Finished generating containers!")
        return True


    def createVirtualNetworkBridge(self):
        '''创建ovs虚拟网桥'''
        subprocess.getoutput("ovs-vsctl del-br vnbr")
        logging.info("Start to create Network Bridge!")
        cmdList = ["ovs-vsctl add-br vnbr", "ovs-vsctl set bridge vnbr protocols=OpenFlow13"]
        for cmd in cmdList:
            (status, output) = subprocess.getstatusoutput(cmd)
            if 1 == status:
                logging.error("Failed to create Virtual Network! error: %s " % output)
                exit(1)
        logging.info("Finished creating Network Bridge!")
        return True


    def configContainersNetwork(self):
        '''为已经创建的Docker容器添加网卡，并绑定在ovs端口上'''
        i = 0
        ipList = ['10.0.1.2', '10.0.1.3', '10.0.2.1']
        for containerid in self.dockerid_to_port.keys():
            time.sleep(1)
            mac = self.generateRandomMac()
            cmd = 'ovs-docker add-port vnbr eth0 %s --ipaddress="%s"  --macaddress="%s"' % \
                  (containerid, ipList[i], mac)
            (status, output) = subprocess.getstatusoutput(cmd)
            if 1 == status:
                logging.error("Failed to configContainerNetwork: %s " % output)
                exit(1)
            self.dockerid_to_port[containerid] = mac
            i = i + 1

        print("config finished!")


if "__main__" == __name__:
    c = Controller('127.0.0.1', 1234)

    c.createDocker(3)

    # time.sleep(30)

    # c.removeDocker()

    c.createVirtualNetworkBridge()

    #print(c.generateRandomMac())

    c.configContainersNetwork()

    print(c.dockerid_to_port)