from email import message
from typing import Type
from xmlrpc.client import Boolean

class Network:
    def __init__(self):
        self.hosts = []
        
    def Connect_computer_to_network(self, host):
        self.hosts.append(host)

    def Search_network_for_MAC_from_IP(self, IP):
        for host in self.hosts:
            if host.IP == IP:
                return host.MAC
            if IP in host.cache:
                return host.cache[IP]

    def findRouter(self, inHost):
        for host in self.hosts:
            if host.isRouter:
                host.Add_To_Cache(inHost.IP, inHost.MAC)
                return host.IP

    def findHost(self, IP, MAC, message):
        for host in self.hosts:
            if host.IP == IP and host.MAC == MAC:
                host.ReceiveMessage(message)

    def check_Router_For_MAC_IP_Pair(self, IP, MAC, message):
        for host in self.hosts:
            if host.isRouter:           
                if host.cache[IP] == MAC:
                    self.findHost(IP, MAC, message)

    
class Host:
    def __init__(self, name, IP, MAC, network: Network, isRouter: Boolean):
        self.name = name
        self.IP = IP
        self.MAC = MAC
        self.cache = {}
        self.network = network
        self.isRouter = isRouter
        network.Connect_computer_to_network(self)
        if isRouter == False:
            self.getRouterInfo()

    def Add_To_Cache(self, MAC, IP):
        self.cache.update({MAC: IP})

    def Request_MAC_Adress(self, IP):
        if IP in self.cache:
            return self.cache[IP]
        return "0"

    def getRouterInfo(self):
        IP = self.network.findRouter(self)
        MAC = self.network.Search_network_for_MAC_from_IP(IP)
        self.Add_To_Cache(IP, MAC)

    def SendMessage(self, destIP, message):
        MAC = ""
        if destIP in self.cache:
            MAC = self.cache[destIP]
        else:
            MAC = self.network.Search_network_for_MAC_from_IP(destIP)
        network.check_Router_For_MAC_IP_Pair(destIP, MAC, message + self.name)

    def ReceiveMessage(self, message):
        print(f"{self.name} has received message: {message}")

    def __str__(self) -> str:
        return f"{self.name} || {self.IP} || {self.MAC}"

network = Network()
router = Host("Router", "127.00.00", "00-00-00-00-00-00", network, True)
computer1 = Host("Computer1", "127.00.01", "01-01-01-01-01-01", network, False)
computer2 = Host("Computer2", "127.00.02", "02-02-02-02-02-02", network, False)
attacker = Host("Attacker", "127.00.03", "03-03-03-03-03-03", network, False)

print(router.cache)

for host in network.hosts:
    print(host.cache)

computer1.SendMessage(computer2.IP, "Hello")
