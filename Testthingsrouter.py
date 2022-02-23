from email import message
from typing import Type
from xmlrpc.client import Boolean

class Network:
    def __init__(self):
        self.hosts = []
        
    def Connect_computer_to_network(self, host):
        self.hosts.append(host)

    def Send_ARP_Request(self, IP):
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

    def findHost(self, IP, MAC):
        for host in self.hosts:
            if host.IP == IP and host.MAC == MAC:
                return host
    
    def findHost_From_Mac(self, MAC):
        for host in self.hosts:
            if host.MAC == MAC:
                returnhost = host
                return returnhost

    #def check_Router_For_MAC_IP_Pair(self, IP, MAC, message):
    #    for host in self.hosts:
    #        if host.isRouter:           
    #            if host.cache[IP] == MAC:
    #                dest = self.findHost(IP, MAC, message)
    #                dest.ReceiveMessage(message)

    
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

    def Add_To_Cache(self, IP, MAC):
        self.cache.update({IP: MAC})

    def Request_MAC_Adress(self, IP):
        if IP in self.cache:
            return self.cache[IP]
        return "0"

    def getRouterInfo(self):
        IP = self.network.findRouter(self)
        MAC = self.network.Send_ARP_Request(IP)
        self.Add_To_Cache(IP, MAC)

    def SendMessage(self, destIP, message):
        MAC = ""
        if destIP in self.cache:
            MAC = self.cache[destIP]
        else:
            MAC = self.network.Send_ARP_Request(destIP)
            self.Send_ARP_Reply(destIP)
        dest_host = network.findHost_From_Mac(MAC)
        dest_host.ReceiveMessage(message + self.name)

    def ReceiveMessage(self, message):
        print(f"{self.name} has received message: {message}")

    def Recieve_ARP_Reply(self, IP, MAC):
        self.Add_To_Cache(IP, MAC)
        pass

    def Send_ARP_Reply(self, destIP):
        MAC = ""
        if destIP in self.cache:
            MAC = self.cache[destIP]
        else:
            MAC = self.network.Send_ARP_Request(destIP)
            self.cache.update({destIP: MAC})
        dest_host = network.findHost(destIP, MAC)
        dest_host.Recieve_ARP_Reply(self.IP, self.MAC)

    def Send_Spoofed_ARP_Reply(self, destIP, newIP):
        MAC = ""
        if destIP in self.cache:
            MAC = self.cache[destIP]
        else:
            MAC = self.network.Send_ARP_Request(destIP)
            self.cache.update({destIP: MAC})
        dest_host = network.findHost(destIP, MAC)
        dest_host.Recieve_ARP_Reply(newIP, self.MAC)      

    def __str__(self) -> str:
        return f"{self.name} || {self.IP} || {self.MAC}"

network = Network()
router = Host("Router", "127.00.00", "00-00-00-00-00-00", network, True)
computer1 = Host("Computer1", "127.00.01", "01-01-01-01-01-01", network, False)
computer2 = Host("Computer2", "127.00.02", "02-02-02-02-02-02", network, False)
attacker = Host("Attacker", "127.00.03", "03-03-03-03-03-03", network, False)

computer1.SendMessage(computer2.IP, "hello")
print(computer1.cache)
attacker.Send_Spoofed_ARP_Reply(computer1.IP, '127.00.02')
print(computer1.cache)
computer1.SendMessage(computer2.IP, "hello")

for host in network.hosts:
    print(host.name)
    print(host.cache)
