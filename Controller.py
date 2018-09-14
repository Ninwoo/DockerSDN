import random
import subprocess
import logging
import time


class Controller:
    def __init__(self, controller_ip, controller_port):
        self.controller_ip = controller_ip;
        self.controller_port = controller_port
        self.containerid_to_interfaceid = {}
        self.containerid_to_port = {}
        self.portid = 1
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
                self.containerid_to_interfaceid.setdefault(output, {})
                self.containerid_to_port.setdefault(output, {})

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
        for dockerid in self.containerid_to_interfaceid.keys():
            # 不安全的强制删除
            cmd = 'docker rm -f %s' % dockerid
            (status, output) = subprocess.getstatusoutput(cmd)
            if 1 == status:
                logging.error("Failed to delete containers!  %s" % output)
                exit(1)
            # del(self.containerid_to_interfaceid[dockerid])
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


    def setPortId(self):
        '''根据Interface Id自定义端口号Id'''
        for containerid in self.containerid_to_interfaceid.keys():
            cmd = "ovs-vsctl set interface %s ofport_request=%d" \
                    % (self.containerid_to_interfaceid[containerid], self.portid)
            (status, output) = subprocess.getstatusoutput(cmd)
            if 1 == status:
                logging.error("Failed to set Port Id! error: %s " % output)
                exit(1)
            self.containerid_to_port[containerid] = self.portid
            self.portid = self.portid + 1

        logging.info("Finished set Interfaces' Port Id!")


    def configContainersNetwork(self):
        '''为已经创建的Docker容器添加网卡，并绑定在ovs端口上'''
        i = 0
        ipList = ['10.0.1.2', '10.0.1.3', '10.0.2.1']
        for containerid in self.containerid_to_interfaceid.keys():
            time.sleep(1)
            mac = self.generateRandomMac()
            cmd = 'ovs-docker add-port vnbr eth0 %s --ipaddress="%s"/24' % (containerid, ipList[i])
            (status, output) = subprocess.getstatusoutput(cmd)
            if 1 == status:
                logging.error("Failed to configContainerNetwork: %s " % output)
                exit(1)

            if '' == output:
                logging.error("Please replace the fixed script 'ovs-docker'")
                exit(1)

            self.containerid_to_interfaceid[containerid] = output
            i = i + 1
        self.setPortId()

        print("config finished!")

    def connectController(self):
        '''配置ovs-vsctl连接到controller'''
        cmd = "ovs-vsctl set-controller vnbr tcp:%s:%d" \
                % (self.controller_ip, self.controller_port)
        subprocess.getstatusoutput(cmd)


    def main(self):
        c.createDocker(3)
        c.createVirtualNetworkBridge()
        c.configContainersNetwork()



if "__main__" == __name__:
    c = Controller('127.0.0.1', 6633)
    c.main()
    print(c.containerid_to_interfaceid, c.containerid_to_port)