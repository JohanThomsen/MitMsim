from email import message
from typing import Type
from xmlrpc.client import Boolean

from sqlalchemy import false

class Network:
    def __init__(self):
        self.hosts = []
        
    def Connect_computer_to_network(self, host):
        self.hosts.append(host)

    def Send_ARP_Request(self, sourceHost, IP):
        print(f"{sourceHost.name} is requesting ARP reply from IP: {IP}")
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

class Host:
    def __init__(self, name, IP, MAC, network: Network, isRouter: Boolean):
        self.name = name
        self.IP = IP
        self.MAC = MAC
        self.cache = {}
        self.network = network
        self.isRouter = isRouter
        self.relay = False
        self.spoofedMACS = []
        self.message_alter = ''
        network.Connect_computer_to_network(self)


    def Add_To_Cache(self, IP, MAC):
        self.cache.update({IP: MAC})

    def Request_MAC_Adress(self, IP):
        if IP in self.cache:
            return self.cache[IP]
        return "0"

    def getRouterInfo(self):
        print()
        IP = self.network.findRouter(self)
        MAC = self.network.Send_ARP_Request(IP)
        self.Add_To_Cache(IP, MAC)

    def SendMessage(self, destIP, message):
        MAC = ""
        if destIP in self.cache:
            MAC = self.cache[destIP]
        else:
            MAC = self.network.Send_ARP_Request(self, destIP)
            self.Send_ARP_Reply(destIP)
        dest_host = network.findHost_From_Mac(MAC)
        dest_host.ReceiveMessage(message + ' from ' + self.name, self.MAC)

    def ReceiveMessage(self, message, MAC):
        if self.relay:
            self.Relay_Message(message, MAC)
        else:
            print(f"{self.name} has received message: {message}")

    def Recieve_ARP_Reply(self, IP, MAC):
        print(f"{self.name} has received ARP reply containing: IP: {IP} MAC: {MAC}")
        self.Add_To_Cache(IP, MAC)

    def Send_ARP_Reply(self, destIP):
        MAC = self.__Get_MAC_and_update_cache(destIP)
        dest_host = network.findHost(destIP, MAC)
        print(f"{self.name} is sending ARP reply to {dest_host.name} containing: IP: {self.IP} MAC: {self.MAC}")
        dest_host.Recieve_ARP_Reply(self.IP, self.MAC)

    def Send_Spoofed_ARP_Reply(self, destIP, newIP):
        MAC = self.__Get_MAC_and_update_cache(destIP)
        self.spoofedMACS.append(MAC)
        dest_host = network.findHost(destIP, MAC)
        print(f"{self.name} is sending spoofed ARP reply to {dest_host.name} containing: IP: {newIP} MAC: {self.MAC}")
        dest_host.Recieve_ARP_Reply(newIP, self.MAC)
    
    def __Get_MAC_and_update_cache(self, destIP):
        MAC = ""
        if destIP in self.cache:
            MAC = self.cache[destIP]
        else:
            MAC = self.network.Send_ARP_Request(self, destIP)
            self.cache.update({destIP: MAC})
        return MAC

    def Start_Relay(self, message_alter = ''):
        print(f"{self.name} relaying with message: {message_alter}")
        self.relay = True
        self.message_alter = message_alter

    def Relay_Message(self, message, MAC):
        if self.spoofedMACS[0] == MAC:
            self.__Send_altered_message(message, self.spoofedMACS[1])
        else:
            self.__Send_altered_message(message, self.spoofedMACS[0])
    
    def __Send_altered_message(self, message, MAC):
        dest_host = network.findHost_From_Mac(MAC)
        print(f'{self.name} relaying and reading message {message}')
        dest_host.ReceiveMessage(message + self.message_alter, MAC)


    def __str__(self) -> str:
        return f"{self.name} || {self.IP} || {self.MAC}"

network = Network()
router = Host("Router", "192.60.20.0", "00-00-00-00-00-00", network, True)
computer1 = Host("Computer1", "192.60.20.1", "01-01-01-01-01-01", network, False)
computer2 = Host("Computer2", "192.60.20.2", "02-02-02-02-02-02", network, False)
attacker = Host("Attacker", "192.60.20.3", "03-03-03-03-03-03", network, False)

print("---------------------------------------------------------------------------------------------")
computer1.SendMessage(router.IP, "hello")
print("---------------------------------------------------------------------------------------------")
computer1.SendMessage(computer2.IP, "hello")
print("---------------------------------------------------------------------------------------------")
attacker.Send_Spoofed_ARP_Reply(computer1.IP, '192.60.20.0')
print("---------------------------------------------------------------------------------------------")
attacker.Send_Spoofed_ARP_Reply(router.IP, '192.60.20.1')
print("---------------------------------------------------------------------------------------------")
attacker.Start_Relay(" Altered by attacker")
print("---------------------------------------------------------------------------------------------")
router.SendMessage(computer1.IP, "hello")
print("---------------------------------------------------------------------------------------------")
computer1.SendMessage(router.IP, "hello")