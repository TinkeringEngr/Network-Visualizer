# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.



import argparse
from impacket.ImpactDecoder import EthDecoder, LinuxSLLDecoder, IP6
from impacket.ImpactPacket import IP
import ipaddress
import json
from multiprocessing import Process
import multiexit
import netifaces
import os
from pcapy import findalldevs, open_live, DLT_EN10MB, DLT_LINUX_SLL, findalldevs
import platform
import pygeoip
import pynng
from requests import get
import sys
import time
import zmq
import zmq.auth


class Sniffer(Process):

    """
    network_sniffer.py: a Pcapy packet sniffer that utilizies Impacket to parse packets and ZMQ (PUB/SUB and Client/Server) to transmit a summmary data dictionary and various commands. The Visualizer (specifically gui_manager.py) parses this data to create a graphical representation.
    
    
    self.sniffer_data["ip"]["data_key"]
    e.g. self.sniffer_data['129.129.0.1']['packet_count']

    data keys:

    packet_count
    tcp_count
    udp_count
    icmp_count
    data_in
    data_out
    new_packet_timestamp
    stream_data
    collect_data_flag
    geoip_info
    """

    def __init__(self, port=None) -> None:

        """Construct Network Sniffer"""

        super(Sniffer, self).__init__()

        
        #Identify directory for any desired assets 
        if getattr(sys, "frozen", False):

                # If the application is run as a bundle, the PyInstaller bootloader
                # extends the sys module by a flag frozen=True and sets the application
                # path into variable _MEIPASS'.
                self.resource_path = sys._MEIPASS

        else:  # otherwise get the directory where the Network Sniffer is executed

            self.resource_path = os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) )



        self.operating_system = platform.system()

        if self.operating_system == "Linux":
            multiexit.register(self.terminate)


        if self.operating_system == "Darwin" and getattr(sys, "frozen", False):

            self.darwin_network_visualizer_dir = os.path.expanduser('~/Library/Application Support/Network-Visualizer')

            with open(os.path.join(self.darwin_network_visualizer_dir, "sniffer_config.json"), "r+") as configuration_file:
                self.config_variables_dict = json.load(configuration_file)

        else:

            with open(os.path.join(self.resource_path, "configuration/sniffer_config.json"), "r+") as configuration_file:
                self.config_variables_dict = json.load(configuration_file)


        if self.config_variables_dict["default_interface"] == None:
                self.active_sniffing = False
                self.pcapy_sniffer = None
                default_interface = None
            
        else:

            default_interface = self.config_variables_dict["default_interface"]
            self.pcapy_sniffer = open_live(default_interface, 3000, 1, 100)
            


        if self.pcapy_sniffer:

            self.active_sniffing = True

            datalink = self.pcapy_sniffer.datalink()

            # # identify correct Impacket Decoder() to use for datalink layer
            if DLT_EN10MB == datalink:
                self.decoder = EthDecoder()

            elif DLT_LINUX_SLL == datalink:
                self.decoder = LinuxSLLDecoder()

            else:
                print(f"Datalink type not supported: {datalink}")
                self.decoder = EthDecoder() # Better than nothing? haha



        if port is None:  

            self.request_port = self.config_variables_dict["default_port"]  # client/server (request/reply)
            self.subscribe_port = self.request_port + 1 # publish/subscribe port

        else:

            self.request_port = port
            self.subscribe_port = port + 1


        self.sniffer_dictionary = {}  # Sniffed data will be stored here!
        self.mac_dict = {}  # store mac address for each interface
        self.populate_mac_dict()
        self.interface_dictionary = self.get_network_interfaces()
        

        self.previous_timestamp = time.time() #initalize timestamp
        self.publish_to_client = True
        self.keep_alive = True
        
        try: #error correction if API call is down? 
            self.sniffer_ip_addresss = get("https://api.ipify.org").content.decode("utf-8") 
        except:
            self.sniffer_ip_addresss = ""


        self.ipv6_database = pygeoip.GeoIP( os.path.join(self.resource_path, "assets/geolocation/maxmind.dat") )  # geolocation database lookup of ip's


        self.ipv4_database = pygeoip.GeoIP( os.path.join(self.resource_path, "assets/geolocation/GeoLiteCity.dat") )  # geolocation database lookup of ip's

        self.sniffer_state = { "active_sniffing": self.active_sniffing,
                               "sniffing_interface": default_interface,
                               "ip_address": self.sniffer_ip_addresss,
                               "interface_dictionary" : self.interface_dictionary,
                               "Operating_System" : self.operating_system 
                             }

        self.setup_client_server_connection()      

        self.start_sniffing()



    def setup_client_server_connection(self) -> None:

        """
        Setup ZMQ network sockets
        """

        try:

            # from zmq.asyncio import Context
            # from zmq.auth.asyncio import AsyncioAuthenticator

            context = zmq.Context()

            # context = Context.instance()

            # auth_location = (
            #     zmq.auth.CURVE_ALLOW_ANY
            # )

            # Configure the authenticator
            # self.auth = AsyncioAuthenticator(context=context)
            # self.auth.configure_curve(domain="*", location=auth_location)
            # self.auth.allow("136.36...")
            # self.auth.start()

            self.publish_socket = context.socket(zmq.PUB)

      
            if self.operating_system == "Darwin" and getattr(sys, "frozen", False): #MacOS and packaged (not terminal executed)
                
                keys = zmq.auth.load_certificate( os.path.join(self.darwin_network_visualizer_dir, "keys/server.key_secret") )

            else:

                keys = zmq.auth.load_certificate( os.path.join(self.resource_path, "configuration/keys/server.key_secret") )

            self.publish_socket.setsockopt(zmq.CURVE_PUBLICKEY, keys[0])
            self.publish_socket.setsockopt(zmq.CURVE_SECRETKEY, keys[1])
            self.publish_socket.setsockopt(zmq.CURVE_SERVER, True)
            self.publish_socket.bind(f"tcp://*:{self.subscribe_port}")


            self.client_socket = pynng.Rep0()
            self.client_socket.listen(f"tcp://*:{self.request_port}")

            # self.client_socket = context.socket(zmq.REP)
            # self.client_socket.setsockopt(zmq.CURVE_PUBLICKEY, keys[0])
            # self.client_socket.setsockopt(zmq.CURVE_SECRETKEY, keys[1])
            # self.client_socket.setsockopt(zmq.CURVE_SERVER, True)
            # self.client_socket.bind(f"tcp://*:{self.request_port}")

        except Exception as e:

            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            sys.exit("Issue with ZMQ server (network_sniffer.py) setup! Try closing any old network_sniffer.py python processes or adding appropriate encryption key.")



    def populate_mac_dict(self) -> None:

        """
        Populates self.mac_dict. Useful for discerning inbound or outbound packets. 
        """

        interfaces = netifaces.interfaces()

        for i in interfaces:

            try:
                interface_dict = netifaces.ifaddresses(i)[netifaces.AF_LINK]
                if interface_dict[0]['addr'] == '00:00:00:00:00:00': #don't bother with loopback
                    continue
                else:
                    self.mac_dict[interface_dict[0]['addr']] = interface_dict[0]['addr']

            except Exception as e:
                pass




    def get_network_interfaces(self) -> dict:

        """
        Populate network interface dictionary using pcapy findalldevs().
        """

        interface_array = findalldevs()
        interface_dictionary = {}

        for interface in interface_array:
            interface_dictionary[interface] = True

        return interface_dictionary


        
    def start_sniffing(self) -> None:

        """Start pcapy packet sniffing loop"""

        while self.keep_alive:

            self.check_for_client_commands()


            if self.active_sniffing == True:

                try:
                    header, packet = self.pcapy_sniffer.next()
                    self.parse_packet(header, packet)

                except Exception as e:
                    pass
                    #print(e) #commonly trying to parse NoneType


                current_timestamp = time.time()
                delta_time = current_timestamp - self.previous_timestamp

                # only send data dictionary after 1 second and client is requesting data
                if delta_time > 1 and self.publish_to_client == True:

                    self.previous_timestamp = current_timestamp
                    self.publish_data_to_clients()



    def parse_packet(self, packet_header: object, packet_data: object) -> None:

        """
        Called on each packet. Parse data and add to self.sniffer_dictionary[IP_Address][data_key]

        """

        timestamp = time.time()

        try:
            ethernet_packet = self.decoder.decode(packet_data) #often packets fail to decode
        except:
            return

        ip_packet = ethernet_packet.child()
        transmision_packet = ip_packet.child()
        payload = transmision_packet.child()

  
        # IPv4
        if type(ethernet_packet.__dict__["_ProtocolLayer__child"]) == type(IP()):  # better way to check for IP4 protocol?
            #print("IPV4!")
            database_lookup = self.ipv4_database

            source_IP_address = ip_packet.get_ip_src()
            destination_IP_address = ip_packet.get_ip_dst()
            transmission_protocol = ip_packet.get_ip_p()
            number_of_bytes_of_data = len(payload.get_bytes())

        # IPv6
        elif type(ethernet_packet.__dict__["_ProtocolLayer__child"]) == type(IP6()):

            database_lookup = self.ipv6_database

            source_IP_address = ip_packet.get_ip_src().as_string()
            destination_IP_address = ip_packet.get_ip_dst().as_string()
            transmission_protocol = transmision_packet.protocol
            number_of_bytes_of_data = len(payload.get_bytes())

        else:
            #print("Protocol other than IPv4 or IPv6")
            return


        if ( ethernet_packet.as_eth_addr(ethernet_packet.get_ether_dhost()) in self.mac_dict):  # packet inbound (recieved)

            ip_index = source_IP_address  # set ip_index for self.sniffer_dictionary

            if ( ip_index in self.sniffer_dictionary ):  # Previous self.sniffer_dictionary entry found

                self.sniffer_dictionary[ip_index]["packet_count"] += 1
                self.sniffer_dictionary[ip_index]["new_packet_boolean"] = True
                self.sniffer_dictionary[ip_index]["new_packet_timestamp"] = timestamp
                self.sniffer_dictionary[ip_index]["data_in"] += number_of_bytes_of_data

            else:  # initalize new self.sniffer_dictionary entry for new inbound packet

                self.sniffer_dictionary[ip_index] = {}

                self.sniffer_dictionary[ip_index]["packet_count"] = 1
                self.sniffer_dictionary[ip_index]["tcp_count"] = 0
                self.sniffer_dictionary[ip_index]["udp_count"] = 0
                self.sniffer_dictionary[ip_index]["icmp_count"] = 0
                self.sniffer_dictionary[ip_index]["data_in"] = number_of_bytes_of_data  # data inbound
                self.sniffer_dictionary[ip_index]["data_out"] = 0  # data outbound
                self.sniffer_dictionary[ip_index]["new_packet_boolean"] = True
                self.sniffer_dictionary[ip_index]["new_packet_timestamp"] = timestamp
                self.sniffer_dictionary[ip_index]["stream_data"] = ""
                self.sniffer_dictionary[ip_index]["collect_data_flag"] = False

                if ipaddress.ip_address(ip_index).is_private or ipaddress.ip_address(ip_index).is_multicast:
                    geoip_info = 'Local'  

                else:
                    geoip_info = database_lookup.record_by_addr(ip_index)                    

                self.sniffer_dictionary[ip_index]["geoip_info"] = geoip_info

            if self.sniffer_dictionary[ip_index]["collect_data_flag"] == True:
                self.sniffer_dictionary[ip_index]["stream_data"] += str(ethernet_packet.get_buffer_as_string())


            # switch to enum-like python3.10? more efficient? 
            if transmission_protocol == 6:  # TCP protocol
                self.sniffer_dictionary[ip_index]["tcp_count"] += 1
                self.sniffer_dictionary[ip_index]["last_packet"] = "TCP"

            elif transmission_protocol == 17:  # UDP packets
                self.sniffer_dictionary[ip_index]["udp_count"] += 1
                self.sniffer_dictionary[ip_index]["last_packet"] = "UDP"

            elif transmission_protocol == 1 or transmission_protocol == 58:  # ICMP Packets
                self.sniffer_dictionary[ip_index]["icmp_count"] += 1
                self.sniffer_dictionary[ip_index]["last_packet"] = "ICMP"

            else:  # some other IP packet
                self.sniffer_dictionary[ip_index]["last_packet"] = "OTHER"



        else:  # packet outbound (sent) ################################################################################

            ip_index = destination_IP_address

            if ( destination_IP_address in self.sniffer_dictionary ):  # Previous self.sniffer_dictionary entry found for outbound destination

                self.sniffer_dictionary[ip_index]["packet_count"] += 1
                self.sniffer_dictionary[ip_index]["new_packet_boolean"] = True
                self.sniffer_dictionary[ip_index]["new_packet_timestamp"] = timestamp
                self.sniffer_dictionary[ip_index]["data_out"] += number_of_bytes_of_data

            else:  # initalize new self.sniffer_dictionary entry for new outbound packet destination

                self.sniffer_dictionary[ip_index] = {}

                self.sniffer_dictionary[ip_index]["packet_count"] = 1
                self.sniffer_dictionary[ip_index]["tcp_count"] = 0
                self.sniffer_dictionary[ip_index]["udp_count"] = 0
                self.sniffer_dictionary[ip_index]["icmp_count"] = 0
                self.sniffer_dictionary[ip_index]["data_in"] = 0  # data inbound
                self.sniffer_dictionary[ip_index]["data_out"] = number_of_bytes_of_data  # data outbound
                self.sniffer_dictionary[ip_index]["new_packet_boolean"] = True
                self.sniffer_dictionary[ip_index]["new_packet_timestamp"] = timestamp
                self.sniffer_dictionary[ip_index]["stream_data"] = ""
                self.sniffer_dictionary[ip_index]["collect_data_flag"] = False

                if ipaddress.ip_address(ip_index).is_private or ipaddress.ip_address(ip_index).is_multicast:
                    geoip_info = 'Local'  

                else:
                    geoip_info = database_lookup.record_by_addr(ip_index)

                self.sniffer_dictionary[ip_index]["geoip_info"] = geoip_info

            if self.sniffer_dictionary[ip_index]["collect_data_flag"] == True:
                self.sniffer_dictionary[ip_index]["stream_data"] += str(ethernet_packet.get_buffer_as_string())


            if transmission_protocol == 6:  # TCP protocol
                self.sniffer_dictionary[ip_index]["tcp_count"] += 1
                self.sniffer_dictionary[ip_index]["last_packet"] = "TCP"

            elif transmission_protocol == 17:  # UDP packets
                self.sniffer_dictionary[ip_index]["udp_count"] += 1
                self.sniffer_dictionary[ip_index]["last_packet"] = "UDP"

            elif transmission_protocol == 1 or transmission_protocol == 58:  # ICMP Packets
                self.sniffer_dictionary[ip_index]["icmp_count"] += 1
                self.sniffer_dictionary[ip_index]["last_packet"] = "ICMP"

            else:
                #print("Protocol other than TCP/UDP/ICMP")  # some other IP packet
                self.sniffer_dictionary[ip_index]["last_packet"] = "OTHER"



    def check_for_client_commands(self) -> None:

        """Using ZMQ Client/Server architecture, check for any commands from client"""

        try:

            msg = self.client_socket.recv(block=False)
            #print(msg)

            if msg == b"reset":

                self.sniffer_dictionary.clear()
                self.client_socket.send(b"received reset")

            elif msg == b"activate":

                self.active_sniffing = True
                self.sniffer_state["active_sniffing"] = self.active_sniffing
                self.client_socket.send(str(self.active_sniffing).encode())

            elif msg == b"deactivate":

                self.active_sniffing = False
                self.sniffer_state["active_sniffing"] = self.active_sniffing
                self.client_socket.send(str(self.active_sniffing).encode())

            elif msg == b'state':
                
                sniffer_state = json.dumps(self.sniffer_state)
                self.client_socket.send(sniffer_state.encode())

            elif msg.startswith(b"collect "):

                client_msg = msg.split(b" ")
                target_ip = client_msg[1].decode('utf-8')
                self.sniffer_dictionary[target_ip]["collect_data_flag"] = True

                self.client_socket.send(f"Collecting on target {target_ip}".encode())

            elif msg.startswith(b"default_port"):

                client_msg = msg.split(b" ")
                port = int(client_msg[1].decode('utf-8'))

                self.config_variables_dict["default_port"] = port

                with open( os.path.join(self.resource_path, "configuration/sniffer_config.json"), "w" ) as configuration_file:
                    json.dump(self.config_variables_dict, configuration_file)

                self.client_socket.send("default port set".encode())
                


            elif msg.startswith(b"interface "):

                client_msg = msg.split(b" ")
                interface = client_msg[1].decode('utf-8')

                try:
                    del self.pcapy_sniffer
                    self.pcapy_sniffer = open_live(interface, 3000, 1, 100)

                    datalink = self.pcapy_sniffer.datalink()
            
                    if DLT_EN10MB == datalink:
                        self.decoder = EthDecoder()

                    elif DLT_LINUX_SLL == datalink:
                        self.decoder = LinuxSLLDecoder()
                    else:
                        raise Exception("Datalink type not supported: " % datalink)

                except:
                        self.client_socket.send("unsupported".encode())
                        return 
                
                self.active_sniffing = True
                self.client_socket.send(f"listening on {interface}".encode())
                self.sniffer_state["sniffing_interface"] = interface
                self.config_variables_dict["default_interface"] = interface

                with open( os.path.join(self.resource_path, "configuration/sniffer_config.json"), "w" ) as configuration_file:
                    json.dump(self.config_variables_dict, configuration_file)

        
        except Exception as e:
            pass



    def publish_data_to_clients(self) -> None:

        """Using ZMQ PUB/SUB architecture to publish self.sniffer_dictionary to any connected clients"""

 
        json_data = json.dumps(self.sniffer_dictionary)

        self.publish_socket.send_string(json_data)



    def terminate(self) -> None:

        """Shutdown pcapy sniffer"""

        self.keep_alive = False
        self.publish_socket.close()
        self.client_socket.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                                    description="Specify port to transmit data. The specified port (client/server) and port + 1 (publish/subscribe) will be used." 
                                    )

    parser.add_argument( "--port", type=int, help="An interger between 1024-49150 not in use")
    args = parser.parse_args()

    sniffer = Sniffer(port=args.port)
