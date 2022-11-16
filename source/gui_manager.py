# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.


import atexit
import datetime
import gc
from importlib import reload 
import json
from math import floor, sin, cos
from multiprocessing import Process, Pipe
import pygeoip
import pyperclip
#from pyperclip import copy
from pyproj import Proj
import pynng
import os
from random import random, randint, randrange
from skimage.color import rgb2lab, lab2rgb #TODO: implement this
import sys
import time
import threading


from typing import Callable
import zmq 
import zmq.auth #TODO: authorize connections



from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import sp, dp, Metrics
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.dropdown import DropDown
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.scatter import Scatter
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.utils import get_hex_from_color



###################################################################
# Dynamic Reloading of Network Visualizer Code - reload code without having to restart the program. Saves time not having to restart the program while developing.
# There is an issue with exception handling since upgrading to python3. I use visual studio to catch exception that are silenced when running directly from terminal.



# try:
#     import network_sniffer
#     reload(network_sniffer)

#     from network_sniffer import *

# except Exception as e:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     print(exc_type, fname, exc_tb.tb_lineno)
#     print("Code broken in database_config.py")



# try:
#     import utilities.database_config

#     reload(utilities.database_config)
#     from utilities.database_config import *

# except Exception as e:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     print(exc_type, fname, exc_tb.tb_lineno)
#     print("Code broken in utilities/database_config.py")



# try:
#     import utilities.iconfonts

#     reload(utilities.iconfonts)
#     from utilities.iconfonts import *

# except Exception as e:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     print(exc_type, fname, exc_tb.tb_lineno)
#     print("Code broke in utilities/icofonts.py")


# try:
#     import utilities.utils

#     reload(utilities.utils)
#     from utilities.utils import *

# except Exception as e:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     print(exc_type, fname, exc_tb.tb_lineno)
#     print("Code broke in utilities/utils.py")


# try:
#     import widgets.city_widget

#     reload(widgets.city_widget)
#     from widgets.city_widget import City_Widget

# except Exception as e:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     print(exc_type, fname, exc_tb.tb_lineno)
#     print("Code broke in widgets/city_widget.py")


# try:
#     import widgets.computer_widget

#     reload(widgets.computer_widget)
#     from widgets.computer_widget import My_Computer

# except Exception as e:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     print(exc_type, fname, exc_tb.tb_lineno)
#     print("Code broken in widgets/computer_widget.py")


# try:
#     import widgets.country_widget

#     reload(widgets.country_widget)
#     from widgets.country_widget import Country_Widget

# except Exception as e:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     print(exc_type, fname, exc_tb.tb_lineno)
#     print("Code broke in widgets/country_widget.py")



# try:
#     import widgets.ip_widget

#     reload(widgets.ip_widget)
#     from widgets.ip_widget import IP_Widget

# except Exception as e:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     print(exc_type, fname, exc_tb.tb_lineno)
#     print("Code broke in widgets/ip_widget.py")



# try:
#     import widgets.settings_panel

#     reload(widgets.settings_panel)
#     from widgets.settings_panel import Settings_Panel

# except Exception as e:
#     exc_type, exc_obj, exc_tb = sys.exc_info()
#     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#     print(exc_type, fname, exc_tb.tb_lineno)
#     print("Code broke in widgets/settings_panel.py")

########################################################################


from network_sniffer import *
from widgets.settings_panel import Settings_Panel
from widgets.ip_widget import IP_Widget
from widgets.country_widget import Country_Widget
from widgets.computer_widget import My_Computer
from widgets.city_widget import City_Widget
from utilities.utils import *
from utilities.iconfonts import *
from utilities.database_config import *
from utilities.whois_lookup_process import ip_whois_lookup_process



class GUI_Manager(ScreenManager):

    """
    GUI_Manager runs the show. This class stores program state, update loops, data structures, and anything else used for the visualizer.
    """

    def __init__(self, **kwargs):


        gc.collect() #Useful for python reload()..?
        super().__init__()

        self.kivy_application = kwargs["kivy_application"]
        self.resource_path = kwargs["resource_path"] # Absolute path to program where assets are located

        if self.kivy_application.operating_system == "Darwin" and getattr(sys, "frozen", False): #MacOS and packaged (not terminal executed)

            # Load saved configuration
            with open( os.path.join( self.kivy_application.darwin_network_visualizer_dir, "visualizer_config.json"), "r+") as configuration_file:
                self.config_variables_dict = json.load(configuration_file)

            # Load cached IP whois information
            with open( os.path.join( self.kivy_application.darwin_network_visualizer_dir, "whois.json"), "r+") as ip_whois_info_file:
                self.ip_whois_info_dict = json.load(ip_whois_info_file)

        else:

            # Load saved configuration
            with open(os.path.join(self.resource_path, "configuration/visualizer_config.json"), "r+") as configuration_file:
                self.config_variables_dict = json.load(configuration_file)

            # Load cached IP whois information
            with open(os.path.join(self.resource_path, "assets/database/whois.json"), "r+") as ip_whois_info_file:
                self.ip_whois_info_dict = json.load(ip_whois_info_file)


        # Views created for ScreenManager - Graph, Table, and Malicious
        self.graph_view = Screen(name="graph")
        self.table_view = Screen(name="table")
        self.malicious_view = Screen(name="malicious")
        self.loading_view = Screen(name="loading")



        #TODO:put these in a function?
        loading_layout = FloatLayout()
        loading_string = Label(text="Resetting...", font_size=sp(36))
        loading_layout.add_widget(loading_string)
        self.loading_view.add_widget(loading_layout)


        self.add_widget(self.graph_view)
        self.add_widget(self.table_view)
        self.add_widget(self.malicious_view)
        self.add_widget(self.loading_view)


        self.current = "graph"  # self.current is the variable name used by ScreenManager to select a View (induce a screen transition - see Kivy documentation)

        register(
                "default_font",
                os.path.join(self.resource_path, "assets/fonts/fontawesome-webfont"),
                os.path.join(self.resource_path, "assets/fonts/font-awesome.fontd"),
                )

        register(
                "extra_font",
                os.path.join(self.resource_path, "assets/fonts/fontello"),
                os.path.join(self.resource_path, "assets/fonts/fontello.fontd"),
                )

        self.window_x, self.window_y = kwargs["window_size"]
        self.center_x = self.window_x / 2
        self.center_y = self.window_y / 2

        #magic numbers
        self.window_ratio = (self.window_y - dp(37.0)) / (self.window_y)
        self.mercator_final_country_position = floor((self.window_x - (self.center_x / 2)) / dp(33)) #TODO: save position after start up run


        self.x_pixels_per_meter = self.window_x / 40030000.0 # circumfrence of earth in meters (around equator)

        self.y_pixels_per_meter = self.window_y / 18500000.0 # circumfrence/2 of earth in meters (from pole to pole)

        self.ip_total_count = 1
        self.city_total_count = 1 #init to zero?
        self.country_total_count = 0
        self.table_count = 0
        self.malicious_table_count = 0
       

        #TODO: these initial values probably could be changed..later
        self.ip_largest_data_in = 1000
        self.ip_largest_data_out = 1000
        self.city_largest_data_out = 1000
        self.city_largest_data_in = 1000
        self.country_largest_data_out = 1000
        self.country_largest_data_in = 1000

        self.new_packet_color_opacity = self.config_variables_dict["new_packet_color_opacity"]

        # Data Structures - See data structure documentation for proper use.

        self.sniffer_dictionary = {}  # Data from sniffer
        self.country_dictionary = {} # Contains all the created GUI widgets (country, city, ip) in heirarchy.
        self.interface_dictionary = {}  # Contains networking interface information
        self.ip_dictionary = {}  # Containes all the ip widgets
        self.city_dictionary = {} # Contains all the city widgets
        #TODO:fix variable naming 
        self.country_widgets = {}
        
        # Because of issues with nested dictionaries containing (non-trivial) widget objects there is a need to create seperate dictionaries to track active and inactive widgets
        self.inactive_ips = {}
        self.inactive_cities = {}
        self.inactive_countries = {}
        self.active_ips = {}
        self.active_cities = {}
        self.active_countries = {}


        self.ip_data_streams = {} # dictionary containing IP addresses with  GUI data streams
        
        


        # Curated list of malcious ip's. https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt
        self.malicious_ips_dictionary =  retrieve_malicious_ips({})
        
        self.malicious_ips_local_database = {}  # Populated from local sql database
        self.found_malicious_ips = {}
        self.built_table = {} # convience dictionary to quickly lookup if IP is in database
        self.malicious_table_dictionary = {}
        self.live_table_dictionary = {} # convience dictionary to store live table widgets
        self.todo_ip_whois_array = []  # array container for batch IP whois lookup
        self.resolved_whois_data = {}
        self.misc_update_dictionary = {
                                        "my_computer": None,
                                        "country": {},
                                        "city": {},
                                        "ip": {},
                                      }

        # self.protocol_color_dict = {
        #                             "TCP": self.config_variables_dict["color_dictionary"]["TCP Protocol Color"],
        #                             "UDP": self.config_variables_dict["color_dictionary"]["UDP Protocol Color"],
        #                             "OTHER": self.config_variables_dict["color_dictionary"]["OTHER Protocol Color"],
        #                             "ICMP": self.config_variables_dict["color_dictionary"]["ICMP Protocol Color"],
        #                            }

        self.settings_toggle_boolean = False
        self.connected_to_sniffer = self.config_variables_dict["auto_connect"]  # TODO:edge case which autoconnect, but remote connection not setup?



        if self.config_variables_dict["first_time_starting"] == True:

            self.config_variables_dict["first_time_starting"] = False #set to false for next time program is loaded
            self.first_time_starting = True

        else:
            self.first_time_starting = False
     
            

        self.country_labels = self.config_variables_dict["country_labels"]
        self.city_labels = self.config_variables_dict["city_labels"]
        self.ip_labels = self.config_variables_dict["ip_labels"]
 
        self.graph = True

        # variables to be populated
        self.sniffer_process = None
        self.sniffer_state = None
        self.current_connection_key = kwargs["connection_key"]
        self.data_socket = None  # ZMQ publish/subscribe pattern
        self.server_socket = None  
        self.sniffer_ip = None
        self.ip_whois_thread = None
        


        self.ip_database_lookup = pygeoip.GeoIP( os.path.join(self.resource_path, "assets/geolocation/GeoLiteCity.dat") )  # ip gelocation

        self.projection = Proj("epsg:32663")  # equirectangular projection (plate) on WGS84 (for mercator view) http://spatialreference.org/ref/epsg/wgs-84-plate-carree/

        self.my_mac_address = populate_network_interfaces()   

        self.init_database_()
        self.make_settings_panel()
        self.make_GUI_widgets()


        if self.config_variables_dict["auto_connect"] == True and not kwargs["connection_key"]:
            self.current_connection_key = self.config_variables_dict['last_connection']
            self.autoconnect_sniffer()
            self.populate_malicious_table()

        elif self.current_connection_key:

            self.switch_to_new_sniffer(self.current_connection_key)
            self.populate_malicious_table()


        if self.server_socket is not None: #Assume current_connection_key is set

            self.request_sniffer_state()
            self.set_sniffer_state()
            self.settings_panel.initalize_interface_dropdown()
        
        

        # Array of widgets for each Kivy Screenmanager view. When Sreenmanager switches views, the appropriate container of widgets is added/removed.
        # add widgets to these containers to populate them for the appropriate view. (Create a new array of widgets for a new view)

        # graph_view container
        self.graph_widgets = [
                                self.graph_widget_container,
                                self.my_computer,
                                self.main_settings_icon,
                                self.table_icon,
                                self.malicious_icon,
                                self.persistent_widget_container,
                             ]

        # table_view container
        self.table_widgets = [
                                self.table_scroll,
                                self.box_header_container,
                                self.livetable_menu,
                                self.graph_icon,
                                self.main_settings_icon,
                                self.malicious_icon,
                                self.persistent_widget_container,
                             ]

        # malicious_view container
        self.malicious_widgets = [
                                    self.malicious_ip_scroll,
                                    self.malicious_ip_container,
                                    self.malicious_menu,
                                    self.persistent_widget_container,
                                    self.graph_icon,
                                    self.main_settings_icon,
                                    self.table_icon,
                                 ]

        self.set_graph_view()  # start graph view on startup 

        Clock.schedule_interval(self.update_gui, 1 / 60)  # Main program loop to update GUI widget
        Clock.schedule_interval(self.update_from_sniffer, 1)  # Update data from sniffer --> self.sniffer_dictionary


        self.start_ip_whois_lookup_process()
        Clock.schedule_interval(self.check_ip_whois_lookup, 3)  # Batch lookup of IP whois


        Clock.schedule_interval(self.db_insert_ip_whois_info, 3)

    # End of GUI_Manager constructor



    def adjust_GUI_for_screen_resolution(self, scaling_factor) -> None:

        """
        This is a poor implementation for setting connection label with varying screen resolution. (Forced by how Kivy sets Labels without layout -- refactor later)
        """
                
        if scaling_factor < 0.75:
   
            self.settings_panel.connection_label.pos[0] = dp(130)
            self.settings_panel.connection_label.pos[1] = dp(-38)

 

    def switch_to_new_sniffer(self, connection_key: str) -> None:

        """
        Switch to new network sniffer connection
        """

        sniffer_port = int(self.config_variables_dict["stored_connections"][connection_key]["connection_info"][1])
        sniffer_data_port = sniffer_port + 1

        connect_string_sniffer = f"tcp://{self.config_variables_dict['stored_connections'][connection_key]['connection_info'][0]}:{sniffer_port}"
        connect_string_subscribe = f"tcp://{self.config_variables_dict['stored_connections'][connection_key]['connection_info'][0]}:{sniffer_data_port}"

        self.current_connection_key = server_name = connection_key


        self.settings_panel.connection_label.text = f"[color=#00ff00][b]Connected[/b][/color] to [color=#00ff00][b]{server_name}[/color][/b] on port [color=#00ff00][b]{sniffer_port}[/color][/b]"

        if self.config_variables_dict['stored_connections'][connection_key]['connection_info'][0] == "localhost" and self.sniffer_process == None:

            try:
                keywords = {"port": sniffer_port}
                self.sniffer_process = Process(name="sniffer", target=Sniffer, kwargs=keywords)  # start sniffer as new process for localhost condition
                self.sniffer_process.start()
                atexit.register(self.sniffer_process.terminate)  # register sniffer cleanup function
            except:
                pass


        try:

            context = zmq.Context()

            if self.kivy_application.operating_system == "Darwin" and getattr(sys, "frozen", False): #MacOS and packaged (not terminal executed)

                keys = zmq.auth.load_certificate( os.path.join(self.kivy_application.darwin_network_visualizer_dir, "keys/client.key_secret") )
                server_key, _ = zmq.auth.load_certificate( os.path.join(self.kivy_application.darwin_network_visualizer_dir, "keys/server.key") )

            else:
                keys = zmq.auth.load_certificate( os.path.join(self.resource_path, "configuration/keys/client.key_secret") )
                server_key, _ = zmq.auth.load_certificate( os.path.join(self.resource_path, "configuration/keys/server.key") )


        
            self.server_socket = pynng.Req0()
            self.server_socket.dial(connect_string_sniffer)

            # self.server_socket = context.socket(zmq.REQ)  # client/server pattern for message passing
            # self.server_socket.setsockopt(zmq.CURVE_PUBLICKEY, keys[0])
            # self.server_socket.setsockopt(zmq.CURVE_SECRETKEY, keys[1])
            # self.server_socket.setsockopt(zmq.CURVE_SERVERKEY, server_key)
            # self.server_socket.connect(connect_string_sniffer)

            self.data_socket = context.socket(zmq.SUB)  # PUB/SUB pattern for sniffer data
            self.data_socket.setsockopt(zmq.CURVE_PUBLICKEY, keys[0])
            self.data_socket.setsockopt(zmq.CURVE_SECRETKEY, keys[1])
            self.data_socket.setsockopt(zmq.CURVE_SERVERKEY, server_key)
            self.data_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            self.data_socket.connect(connect_string_subscribe)

            self.config_variables_dict["last_connection"] = connection_key
 

        except Exception as e:

            print("Issue setting up ZMQ sockets", e)
            self.kivy_application.get_running_app().stop()  # Do we want to shutdown the application if program can't setup ZMQ sockets?



    def autoconnect_sniffer(self):

        """
        Setup ZMQ client/server and pub/sub sockets. If LocalHost, start Sniffer as new process.
        """

        self.settings_panel.auto_connect_checkbox.active = True

        server_name = self.config_variables_dict["last_connection"]
        self.current_connection_key = server_name

        sniffer_ip = self.config_variables_dict["stored_connections"][server_name]["connection_info"][0] 
        
        sniffer_port = self.config_variables_dict["stored_connections"][server_name]["connection_info"][1]
        sniffer_data_port = sniffer_port + 1

        connect_string_sniffer = f"tcp://{sniffer_ip}:{sniffer_port}"
        connect_string_subscribe = f"tcp://{sniffer_ip}:{sniffer_data_port}"

        if sniffer_ip == "localhost":

            keywords = {"port": sniffer_port}
            self.sniffer_process = Process( name="sniffer", target=Sniffer, kwargs=keywords )  # start sniffer as new process for localhost condition
            self.sniffer_process.start()
            atexit.register( self.sniffer_process.terminate )  # register sniffer cleanup function


       

        try:

            context = zmq.Context()

            if self.kivy_application.operating_system == "Darwin" and getattr(sys, "frozen", False): #MacOS and packaged (not terminal executed)
            
                keys = zmq.auth.load_certificate( os.path.join(self.kivy_application.darwin_network_visualizer_dir, "keys/client.key_secret") )
                server_key, _ = zmq.auth.load_certificate( os.path.join(self.kivy_application.darwin_network_visualizer_dir, "keys/server.key") )

            else:

                keys = zmq.auth.load_certificate( os.path.join(self.resource_path, "configuration/keys/client.key_secret"))
                server_key, _ = zmq.auth.load_certificate( os.path.join(self.resource_path, "configuration/keys/server.key"))



            self.server_socket = pynng.Req0()
            self.server_socket.dial(connect_string_sniffer)

            # self.server_socket = context.socket(zmq.REQ)  # client/server pattern for message passing
            # self.server_socket.setsockopt(zmq.CURVE_PUBLICKEY, keys[0])
            # self.server_socket.setsockopt(zmq.CURVE_SECRETKEY, keys[1])
            # self.server_socket.setsockopt(zmq.CURVE_SERVERKEY, server_key)
            # self.server_socket.connect(connect_string_sniffer)
            
           

            self.data_socket = context.socket(zmq.SUB)  # PUB/SUB pattern for sniffer data
            self.data_socket.setsockopt(zmq.CURVE_PUBLICKEY, keys[0])
            self.data_socket.setsockopt(zmq.CURVE_SECRETKEY, keys[1])
            self.data_socket.setsockopt(zmq.CURVE_SERVERKEY, server_key)
            self.data_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            self.data_socket.connect(connect_string_subscribe)

            self.settings_panel.connection_label.text = f"[color=#00ff00][b]Connected[/b][/color] to [color=#00ff00][b]{server_name}[/color][/b] on port [color=#00ff00][b]{sniffer_port}[/color][/b]"

        except Exception as e:
            print("Issue setting up ZMQ sockets")



    def request_sniffer_state(self) -> None:

        """
        Request sniffer configuration variables 
        """

        self.server_socket.send(b'state')
        msg = self.server_socket.recv()

        self.sniffer_state = json.loads(msg)



    def set_sniffer_state(self) -> None:

        """
        Set display information from sniffer state dictionary
        """


        ############

        if self.sniffer_state["active_sniffing"] == True:

            self.settings_panel.activate_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/green_button.png")
            self.settings_panel.activate_sniffer_button.text = "Sniffer Activated"

        else:
            self.settings_panel.activate_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/red_button.png")
            self.settings_panel.activate_sniffer_button.text = "Sniffer Deactivated"

        ############

        try:
            my_ip_info = self.ip_database_lookup.record_by_addr(self.sniffer_state["ip_address"])

            self.my_computer.set_position(my_ip_info)

        except:

            my_ip_info = None


        self.interface_dictionary[self.sniffer_ip] = my_ip_info

        


        ############

        self.settings_panel.interface_label.text = f"""Interface: [color=#00ff00][b]{self.sniffer_state["sniffing_interface"]}[/b][/color]"""

        ###########


        self.interface_dictionary = self.sniffer_state["interface_dictionary"]




    def mix_colors(self, protocols: dict) -> tuple[float, float, float, float]:

        """
        Converts to LAB color space, mixes colors then converts back to RGB.
        """

        channel_a = 0
        channel_b = 0
        channel_c = 0
        count = 0

        for protocol in protocols.keys():

            key = protocol + " Protocol Color"

            #TODO:implement rgb2lab without using skimage
            lab_color = rgb2lab(self.config_variables_dict["color_dictionary"][key][0:3])

            channel_a += lab_color[0]
            channel_b += lab_color[1]
            channel_c += lab_color[2]

            count += 1

        if count == 0:
            count = 1

        sum_a_avg = channel_a / count
        sum_b_avg = channel_b / count
        sum_c_avg = channel_c / count

        rgb_color = lab2rgb([sum_a_avg, sum_b_avg, sum_c_avg])

        return list(rgb_color)



    def update_gui(self, time_delta: tuple) -> None:

        """
        Main Program Loop for updating GUI widgets based on (self.current) View (graph, table, malicious, etc)
        """

        
        total_data_out_accumulator = 0
        total_data_in_accumulator = 0

        inactive_ip_display_threshold = time.time() - self.settings_panel.ip_display_slider.value 
        remove_inactive_ips = self.settings_panel.inactive_ip_display_checkbox.active

        

        data_in_color = get_hex_from_color( self.config_variables_dict["color_dictionary"]["Data IN Color"] )
        data_out_color = get_hex_from_color( self.config_variables_dict["color_dictionary"]["Data OUT Color"] )

        if self.current == "graph":  # Start graph loop

            self.graph_widget_container.clear_widgets()
            self.my_computer.update(state=self.graph)
            

            for country in self.country_dictionary:  # Start of Country loop

                country_data_in_accumulator = 0
                country_data_out_accumulator = 0
                country_new_data = False

                country_widget = self.country_dictionary[country][0]
                country_total_city_widgets = len(self.country_dictionary[country][1])  # len(city dictionary)
                country_widget.city_total_count = country_total_city_widgets

                country_draw_angle = angle_between_points(self.my_computer.icon_scatter_widget.pos, country_widget.icon_scatter_widget.pos)
                country_widget.country_draw_angle = country_draw_angle

                ip_total_count = 0

                country_color_dict = {}


                
                for city_index, city in enumerate(self.country_dictionary[country][1]):  # Start of City loop

                    city_data_in_accumulator = 0
                    city_data_out_accumulator = 0

                    city_widget = self.country_dictionary[country][1][city][0]
                    city_number_of_ips = (len(self.country_dictionary[country][1][city]) - 1)

                    city_color_dict = {}
  


                    for ip_index, ip_widget in enumerate(self.country_dictionary[country][1][city]):  # Start of IP loop
                        
                        if ip_index == 0: #skip city widget
                            continue

                        ip_address = ip_widget.id

                        city_data_in_accumulator += ip_widget.ip_data["data_in"]
                        city_data_out_accumulator += ip_widget.ip_data["data_out"]

                        if ip_widget.ip_data["data_in"] > self.ip_largest_data_in:
                            self.ip_largest_data_in = ip_widget.ip_data["data_in"]

                        if ip_widget.ip_data["data_out"] > self.ip_largest_data_out:
                            self.ip_largest_data_out = ip_widget.ip_data["data_out"]


                        last_packet = ip_widget.ip_data["last_packet"]
                        city_color_dict[last_packet] = True
                        
                
                        if ( ip_widget.show == True ) and ( ip_address in self.active_ips[country][city] ): 

                            ip_widget.update(
                                            city_widget = city_widget,
                                            protocol_color = self.config_variables_dict["color_dictionary"][last_packet + " Protocol Color"].copy()
                                            )
                            
                            self.graph_widget_container.add_widget(ip_widget)
                        

                            if remove_inactive_ips  and ( ip_widget.new_packet_timestamp < inactive_ip_display_threshold ):
            
                                self.inactive_ips[country][city][ip_address] = True
                                self.active_ips[country][city].pop(ip_address)


                        # End of IP loop

                    


                    # Continue City loop

                    if ( len(self.active_ips[country][city].keys() ) == 0) and ( city in self.active_cities[country] ):

                        self.active_cities[country].pop(city)
                        self.inactive_cities[country][city] = True

                    
                    ip_total_count += ip_index + 1

                    city_mixed_color = self.mix_colors(city_color_dict)

                    country_color_dict = (city_color_dict | country_color_dict)  # combine dictionaries python >3.9

                    if city_data_out_accumulator > self.city_largest_data_out:
                        self.city_largest_data_out = city_data_out_accumulator

                    if city_data_in_accumulator > self.city_largest_data_in:
                        self.city_largest_data_in = city_data_in_accumulator

                    city_widget.total_data_out = city_data_out_accumulator
                    city_widget.total_data_in = city_data_in_accumulator

                    country_data_in_accumulator += city_data_in_accumulator
                    country_data_out_accumulator += city_data_out_accumulator

                    if city_widget.show == True and ( city in self.active_cities[country] ):

                        city_widget.update(
                                            state=self.graph,
                                            protocol_color=city_mixed_color
                                            )

                        self.graph_widget_container.add_widget(city_widget)

                    # End of City loop

                # Continue Country loop

                country_mixed_color = self.mix_colors(country_color_dict)

                country_widget.ip_total_count = ip_total_count

                country_widget.new_data = country_new_data

                country_widget.total_data_in = country_data_in_accumulator
                country_widget.total_data_out = country_data_out_accumulator

                if country_data_in_accumulator > self.country_largest_data_in:
                    self.country_largest_data_in = country_data_in_accumulator

                if country_data_out_accumulator > self.country_largest_data_out:
                    self.country_largest_data_out = country_data_out_accumulator

                total_data_out_accumulator += country_data_out_accumulator
                total_data_in_accumulator += country_data_in_accumulator

                if country_widget.show == True:
                    country_widget.update(state=self.graph, protocol_color=country_mixed_color)

                    self.graph_widget_container.add_widget(country_widget)

                # End of Country loop

            # Continue Graph loop

            self.my_computer.total_data_out = total_data_out_accumulator
            self.my_computer.total_data_in = total_data_in_accumulator

            self.my_computer.total_data_in_label.text = f"Data IN (GB): [b][color={data_in_color}]{self.my_computer.total_data_in/1000000000.0:.3f} [/color][/b]"
            self.my_computer.total_data_out_label.text = f"  Data OUT (GB): [b][color={data_out_color}]{self.my_computer.total_data_out/1000000000.0:.3f}[/color][/b]"

            summary_data_color = get_hex_from_color(self.config_variables_dict["color_dictionary"]["Summary Data Color"])

            for country in self.misc_update_dictionary["country"].keys():

                self.misc_update_dictionary["country"][country].data_IN_label.text = f" Data IN (MB): [b][color={data_in_color}]{self.misc_update_dictionary['country'][country].total_data_in/1000000.0:.3f} [/color][/b]"

                self.misc_update_dictionary["country"][country].data_OUT_label.text = f" Data OUT (MB): [b][color={data_out_color}]{self.misc_update_dictionary['country'][country].total_data_out/1000000.0:.3f}[/color][/b]"

                city_total_count = self.misc_update_dictionary["country"][country].city_total_count

                self.misc_update_dictionary["country"][country].total_cities_label.text = f"[b][color={summary_data_color}]{city_total_count - 1 }[/color][/b]"
                

                ip_total_count = self.misc_update_dictionary["country"][country].ip_total_count

                self.misc_update_dictionary["country"][country].total_ip_label.text = f"[b][color={summary_data_color}]{ip_total_count}[/color][/b]"
                

            for city in self.misc_update_dictionary["city"].keys():

                self.misc_update_dictionary["city"][city].data_IN_label.text = f" Data IN (MB): [b][color={data_in_color}]{self.misc_update_dictionary['city'][city].total_data_in/1000000.0:.3f}  [/color][/b]"

                self.misc_update_dictionary["city"][city].data_OUT_label.text = f" Data OUT (MB): [b][color={data_out_color}]{self.misc_update_dictionary['city'][city].total_data_out/1000000.0:.3f}[/color][/b]"

                ip_total_count = self.misc_update_dictionary["city"][city].ip_total_count

                self.misc_update_dictionary["city"][city].total_ip_label.text = f"[b][color={summary_data_color}]{ip_total_count}[/color][/b]"
                

            for ip in self.misc_update_dictionary["ip"].keys():

                self.misc_update_dictionary["ip"][ip].data_IN_label.text = f"Data IN (MB): [b][color={data_in_color}]{self.misc_update_dictionary['ip'][ip].ip_data['data_in']/1000000.0:.6f}[/color][/b]"

                self.misc_update_dictionary["ip"][ip].data_OUT_label.text = f"  Data OUT (MB): [b][color={data_out_color}]{self.misc_update_dictionary['ip'][ip].ip_data['data_out']/1000000.0:.6f}[/color][/b]"

                self.misc_update_dictionary["ip"][ip].packet_label.text = f"Packet Count: [b][color={summary_data_color}] {self.misc_update_dictionary['ip'][ip].ip_data['packet_count']}[/b][/color]"

            # End of Graph loop



        elif self.current == "table":  # Start table loop

            self.graph_widget_container.clear_widgets()

            for country in self.country_dictionary:  # Start of Country loop

                country_data_in_accumulator = 0
                country_data_out_accumulator = 0

                for city_index, city in enumerate(self.country_dictionary[country][1]):  # Begin City Loop

                    city_data_in_accumulator = 0
                    city_data_out_accumulator = 0

                    for ip_index, ip_widget in enumerate(self.country_dictionary[country][1][city]):  # Begin IP loop

                        if ip_index == 0:
                            continue

                        city_data_in_accumulator += ip_widget.ip_data["data_in"]
                        city_data_out_accumulator += ip_widget.ip_data["data_out"]
                        # End of IP loop

                    country_data_in_accumulator += city_data_in_accumulator
                    country_data_out_accumulator += city_data_out_accumulator
                    # End of City loop

                total_data_out_accumulator += country_data_out_accumulator
                total_data_in_accumulator += country_data_in_accumulator
                # End of Country loop

            # Continue table loop
            self.my_computer.total_data_out = total_data_out_accumulator
            self.my_computer.total_data_in = total_data_in_accumulator
            # End of table loop


            self.live_data_in_button.text = f'[color={get_hex_from_color(self.config_variables_dict["color_dictionary"]["Data IN Color"])}] Data IN  {self.my_computer.total_data_in/1000000.0:.3f} (MB)[/color]   {icon("fa-sort")}'


            self.live_data_out_button.text = f'[color={get_hex_from_color(self.config_variables_dict["color_dictionary"]["Data OUT Color"])}] Data OUT  {self.my_computer.total_data_out/1000000.0:.3f} (MB)[/color]   {icon("fa-sort")}'

            self.ip_label_header.text = f'IP Address ({len(self.ip_dictionary.keys())})   {icon("fa-sort")}'




        elif self.current == "malicious":  # Start malicious loop

            self.graph_widget_container.clear_widgets()

            for country in self.country_dictionary:  # Start of Country loop

                country_data_in_accumulator = 0
                country_data_out_accumulator = 0

                for city_index, city in enumerate(self.country_dictionary[country][1]):  # Begin City Loop

                    city_data_in_accumulator = 0
                    city_data_out_accumulator = 0

                    for ip_index, ip_widget in enumerate(self.country_dictionary[country][1][city]):  # Begin IP loop
                        
                        if ip_index == 0:
                            continue

                        city_data_in_accumulator += ip_widget.ip_data["data_in"]
                        city_data_out_accumulator += ip_widget.ip_data["data_out"]
                        # End of IP loop

                    country_data_in_accumulator += city_data_in_accumulator
                    country_data_out_accumulator += city_data_out_accumulator
                    # End of City loop

                total_data_out_accumulator += country_data_out_accumulator
                total_data_in_accumulator += country_data_in_accumulator
                # End of Country loop

            # Continue malicious loop
            self.my_computer.total_data_out = total_data_out_accumulator
            self.my_computer.total_data_in = total_data_in_accumulator
            # End of malicious loop

        # End of GUI loop



    def update_from_sniffer(self, time_delta: tuple) -> None:

        """
        Update GUI widgets and/or make new GUI widgets from network sniffer data.
        """

        self.recieve_data_from_sniffer()

    
        for ip in self.sniffer_dictionary.keys():  # iterate over the json dictionary sent from network_sniffer.py

            if ip in self.ip_dictionary:  # IP, City and Country widgets exist. Just update IP data.
               
                self.ip_dictionary[ip].data_in_delta += (self.sniffer_dictionary[ip]["data_in"] - self.ip_dictionary[ip].ip_data["data_in"])
                self.ip_dictionary[ip].data_out_delta += (self.sniffer_dictionary[ip]["data_out"] - self.ip_dictionary[ip].ip_data["data_out"])
                self.ip_dictionary[ip].ip_data = self.sniffer_dictionary[ip]

                packet_timestamp  = self.sniffer_dictionary[ip]["new_packet_timestamp"]
                new_timestamp = time.time() #new timestamp for when data is processed by Visualizer

                
                if packet_timestamp > self.ip_dictionary[ip].new_packet_timestamp:

                    self.ip_dictionary[ip].new_packet_timestamp = new_timestamp

                    self.ip_dictionary[ip].time_stamp = datetime.datetime.fromtimestamp(new_timestamp).strftime("%H:%M:%S %d-%m-%Y")
    
                    city = self.ip_dictionary[ip].city
                    country = self.ip_dictionary[ip].country

                    if city in self.inactive_cities[country]:

                        self.inactive_cities[country].pop(city)
                        self.active_cities[country][city] = True


                    if ip in self.inactive_ips[country][city]:
                        
                        self.inactive_ips[country][city].pop(ip)
                        self.active_ips[country][city][ip] = True



                if packet_timestamp > self.ip_dictionary[ip].country_widget.new_packet_timestamp:
                    self.ip_dictionary[ip].country_widget.new_packet_timestamp = new_timestamp

                if packet_timestamp > self.ip_dictionary[ip].city_widget.new_packet_timestamp:
                    self.ip_dictionary[ip].city_widget.new_packet_timestamp = new_timestamp


            else:  # Case:  IP widget doesn't exist

                geoip_info = self.sniffer_dictionary[ip]["geoip_info"]

                if geoip_info == None:

                    city = "Unresolved"
                    country = "Unresolved"
                    ip_longitude = "Unresolved"
                    ip_latitude = "Unresolved"
                    country_code = "Unresolved"

                elif geoip_info == 'Local':

                    city = "Local"
                    country = "Local"
                    ip_longitude = "Local"
                    ip_latitude = "Local"
                    country_code = "Local"

                else:

                    country = remove_inline_quotes(geoip_info["country_name"])
                    if country == None: country = 'Unresolved'
                    
                    city = remove_inline_quotes(geoip_info["city"])
                    if city == None: city = 'Unresolved'

                    country_code = geoip_info["country_code"]
                    ip_longitude = geoip_info["longitude"]
                    ip_latitude = geoip_info["latitude"]


                ip_longitude_x, ip_latitude_y = self.calculate_mercator_coordinates( ip_longitude, ip_latitude )

                ip_placeholder = IP_Widget(
                                            gui_manager=self,
                                            ip=ip,
                                            ip_data=self.sniffer_dictionary[ip],
                                            window_x=self.window_x,
                                            window_y=self.window_y,
                                            country=country,
                                            city=city,
                                            ip_latitude=ip_latitude,
                                            ip_longitude=ip_longitude,
                                            ip_latitude_y=ip_latitude_y,
                                            ip_longitude_x=ip_longitude_x,
                                            resource_path=self.resource_path,
                                          )

                
                # Check after IP_widget is created in order to have the ip_placeholder reference for whois lookup
                if geoip_info == 'Local':
                    pass

                elif ip in self.ip_whois_info_dict.keys():

                    ip_whois_description = self.ip_whois_info_dict[ip]["nets"][0]["description"]
                    ip_placeholder.whois_description.text = ip_whois_description
                    self.live_table_dictionary[ip].children[6].text = ip_whois_description

                    cursor = db.cursor()
                    cursor.execute(f"""UPDATE Live SET description = "{ip_whois_description}" WHERE ip="{ip}" """)
                    db.commit()

                else:
                    #self.todo_ip_whois_array.append( (ip, ip_placeholder) )
                    self.todo_ip_whois_array.append(ip)
                

                

                if (ip in self.malicious_ips_dictionary) or (ip in self.malicious_ips_local_database):

                    ip_placeholder.tag()

                    if ip in self.ip_whois_info_dict.keys():

                        ip_whois_description = self.ip_whois_info_dict[ip]["nets"][0]["description"]

                        self.malicious_table_dictionary[ip].children[6].text = ip_whois_description

                        cursor = db.cursor()
                        
                        current_connection_key = self.current_connection_key.replace(" ", "")

                        cursor.execute(f"""UPDATE {current_connection_key + '_malicious_ips'} SET description = "{ip_whois_description}" WHERE ip="{ip}" """)
                        db.commit()


                self.ip_dictionary[ip] = ip_placeholder  # add IP widget into a flat convenience lookup dictionary, seperate from the hierarchical Country->City->IP dictionary

                self.ip_total_count += 1  #  Update total_ip_label.text eventually

                #### ip widget made, now check to see if country and city widget exist

                if country in self.country_dictionary:  # Country widget exists

                    ip_placeholder.country_widget = self.country_dictionary[country][0]

                    country_widget = self.country_dictionary[country][0]

                    if (city in self.country_dictionary[country][1]):  # City widget exists

                        ip_placeholder.city_widget = self.country_dictionary[country][1][city][0]

                        city_widget = self.country_dictionary[country][1][city][0]

                        self.country_dictionary[country][1][city][0].ip_total_count += 1  # first item in array is city widget
                        self.country_dictionary[country][1][city].append(ip_placeholder)  # add ip widget to array in city dictionary

                        self.country_dictionary[country][1][city][0].set_ips_mercator_inital_position()

                        if (country_widget.show_ip_widgets == False) or (self.graph == False) or (city_widget.show_ip_widgets == False) or (self.my_computer.show_ip_widgets == False):
                             ip_placeholder.show = False


                        
                        self.active_ips[country][city][ip] = True
                        self.active_cities[country][city] = True
          

                    else:  # Case: Country widget exists, but no city widget exists. Build city widget

                        country_widget = self.country_dictionary[country][0]  # first item in array is country widget
   
         
                        city_widget = City_Widget(
                                                    gui_manager=self,
                                                    center_x=self.center_x,
                                                    center_y=self.center_y,
                                                    window_x=self.window_x,
                                                    window_y=self.window_y,
                                                    city=city,
                                                    country=country,
                                                    latitude=ip_latitude,
                                                    longitude=ip_longitude,
                                                    latitude_y=ip_latitude_y,
                                                    longitude_x=ip_longitude_x,
                                                    resource_path=self.resource_path,
                                                    graph_state=self.graph
                                                 )

                        self.city_dictionary[country][city] = city_widget

                        self.active_cities[country][city] = True

                        self.active_ips[country].setdefault(city, {ip: True} )

                        self.inactive_ips[country][city] = {}


                        if ( country_widget.show_city_widgets == False) or (self.my_computer.show_city_widgets == False):

                            city_widget.show = False
                            city_widget.show_ip_widgets = False

                        if (country_widget.show_ip_widgets == False) or (self.graph == False) or (city_widget.show_ip_widgets == False) or (self.my_computer.show_ip_widgets == False):
                             ip_placeholder.show = False


                        ip_placeholder.city_widget = city_widget

                        self.country_dictionary[country][1].setdefault(city, []).append(city_widget)  # set City widget to first position in array. See data structure documentation for clarification.
                        self.country_dictionary[country][1][city].append(ip_placeholder)  # add ip widget to array in city dictionary

                        city_widget.set_ips_mercator_inital_position()

                        self.city_total_count += 1  # After we update total_cities_label.text

  

                else:  # Case: Country widget and City widget don't exist.  Build Country and City widget

                    # initalize position for country widget on screen for graph view
                    country_screen_x = self.window_x * random()
                    country_screen_y = self.window_y * random()

                    country_widget = Country_Widget(
                                                    screen_x=country_screen_x,
                                                    screen_y=country_screen_y,
                                                    gui_manager=self,
                                                    center_x=self.center_x,
                                                    center_y=self.center_y,
                                                    window_x=self.window_x,
                                                    window_y=self.window_y,
                                                    country=country,
                                                    country_code=country_code,
                                                    country_index=self.country_total_count,
                                                    resource_path=self.resource_path,
                                                    graph_state=self.graph,
                                                   )

                    self.country_widgets[country] = country_widget
                    

                    if self.my_computer.show_country_widgets == False:
                        country_widget.show = False

                    if self.my_computer.show_city_widgets == False:
                        country_widget.show_city_widgets = False

                    if self.my_computer.show_ip_widgets == False:
                        country_widget.show_ip_widgets = False


                    self.country_dictionary.setdefault(country, [country_widget]).append({})  # Append to country dictionary. Set first item in array as country widget and second item as city dictionary. See data structure documentation for clarification.

                    city_widget = City_Widget(
                                                gui_manager=self,
                                                center_x=self.center_x,
                                                center_y=self.center_y,
                                                window_x=self.window_x,
                                                window_y=self.window_y,
                                                city=city,
                                                country=country,
                                                latitude=ip_latitude,
                                                longitude=ip_longitude,
                                                latitude_y=ip_latitude_y,
                                                longitude_x=ip_longitude_x,
                                                resource_path=self.resource_path,
                                                graph_state=self.graph,
                                              )

                    self.city_dictionary.setdefault(country, {city: city_widget})
                
                    self.active_cities.setdefault(country, {city : True})
                    self.inactive_cities[country] = {}

                    self.active_ips.setdefault( country, {city : {ip : True} } )
                    self.inactive_ips.setdefault(country, { city : {} } )


                    if ( country_widget.show_city_widgets == False) or (self.my_computer.show_city_widgets == False):

                            city_widget.show = False
                            city_widget.show_ip_widgets = False
                            ip_placeholder.show = False


                    if (country_widget.show_ip_widgets == False) or (self.graph == False) or (city_widget.show_ip_widgets == False) or (self.my_computer.show_ip_widgets == False):
                             ip_placeholder.show = False

                    self.country_dictionary[country][1].setdefault(city, []).append(city_widget)  # set City widget to first position in array. See data structure documentation for clarification.
                    self.country_dictionary[country][1][city].append(ip_placeholder)  # add ip widget to array in city dictionary

                    city_widget.set_ips_mercator_inital_position()

                    ip_placeholder.city_widget = city_widget
                    ip_placeholder.country_widget = country_widget
                    ip_placeholder.set_position()

                    self.city_total_count += 1  # After we update total_cities_label.text
       
                    self.country_total_count += 1  # After we update total_countries_label.text

                    
        self.set_summary_data()

        for ip in self.ip_data_streams.keys():
            self.ip_dictionary[ip].data_stream_text.text = self.ip_dictionary[ip].ip_data["stream_data"]



    def set_summary_data(self) -> None:

        """
        Set Summary data for My Computer menu
        """
        
        summary_data_color = get_hex_from_color(self.config_variables_dict["color_dictionary"]["Summary Data Color"])

        self.my_computer.total_ip_label.text = f"[b][color={summary_data_color}] {self.ip_total_count - 1 } [/color][/b]"
        
        self.my_computer.total_cities_label.text = f"[b][color={summary_data_color}]{self.city_total_count - 1}[/color][/b]"
        
        self.my_computer.total_countries_label.text = f"[b][color={summary_data_color}]{self.country_total_count}[/color][/b]"
        

        cursor = db.cursor()

        if self.current_connection_key == None:
            return
        current_connection_key = self.current_connection_key.replace(" ", "")
        malicious_ips_database_name = current_connection_key + "_malicious_ips"
        
        cursor.execute(f"SELECT * from {malicious_ips_database_name}")
        malicious_ips = cursor.fetchall()
        self.my_computer.malicious_ip_count.text = f"[color=FF0000]Detected Malicious IP's: [b]{str(len(malicious_ips))}[/b]"
    


    def recieve_data_from_sniffer(self) -> None:

        """
        Get data (sniffer_dictionary) from network sniffer.
        """

        try:
            json_data = self.data_socket.recv(flags=zmq.NOBLOCK)
            self.sniffer_dictionary = json.loads(json_data)

        except Exception as e:
            pass


    def start_ip_whois_lookup_process(self):

        """
        Start a IP whois lookup process.
        """

        self.parent_conn, child_conn = Pipe()
        
        p = Process(target=ip_whois_lookup_process, args=(child_conn,))
        p.start()



    def check_ip_whois_lookup(self, time_delta: float):

        """
        Communicate with ip_whois_lookup_process and update associated GUI information. 
        """

        todo_ip_whois_array_copy = self.todo_ip_whois_array.copy()
        
        self.parent_conn.send(todo_ip_whois_array_copy)
        self.todo_ip_whois_array = []
        

        if self.parent_conn.poll():

            finished_ip_whois_lookup_from_child = self.parent_conn.recv()

            for ip_key in finished_ip_whois_lookup_from_child.keys():

                try:
                    ip_whois_info = finished_ip_whois_lookup_from_child[ip_key]
                    ip_whois_description = ip_whois_info["nets"][0]["description"] 
                    self.ip_dictionary[ip_key].whois_description.text = ip_whois_description
                    self.ip_whois_info_dict[ip_key] = ip_whois_info
                    self.resolved_whois_data[ip_key] = ip_whois_description


                    #this will break if the number of columns will change. 
                    self.live_table_dictionary[ip_key].children[6].text = ip_whois_description # TODO: use isInstance() or id to search children instead of hard coded description at children[5]

                    if self.malicious_table_dictionary[ip_key]:
                        self.malicious_table_dictionary[ip_key].children[6].text = ip_whois_description # TODO: use isInstance() or id property to search children instead of hard coded description at children[6]
                except:

                    #TODO: Error handling
                    pass
            

        else: 
            pass




    def db_insert_ip_whois_info(self, time_delta: float) -> None:

        """
        Insert whois information into sqlite3 database. Done this way to prevent issue with opening db.cursor in seperate thread. <--- maybe not releveant anymore since architecture was switched to multiprocess instead of multithread. 
        """


        if not self.resolved_whois_data:  # if self.resolved_whois_data dictionary is not empty
            cursor = db.cursor()

            for ip in self.resolved_whois_data:
     
                cursor.execute(f"""UPDATE Live SET description = "{self.resolved_whois_data[ip]}" WHERE ip="{ip}" """)
                db.commit()


                if (ip in self.malicious_ips_dictionary) or (ip in self.malicious_ips_local_database):

                    self.malicious_table_dictionary[ip].children[6].text = self.resolved_whois_data[ip]
                    current_connection_key = self.current_connection_key.replace(" ", "")
                    cursor.execute(f"""UPDATE {current_connection_key + '_malicious_ips'} SET description = "{self.resolved_whois_data[ip]}" WHERE ip="{ip}" """)
                    db.commit()


                del self.resolved_whois_data[ip]




    def set_graph_view(self, *button: Button):

        """
        Transition screenmanager to graph view and display appropriate widgets.
        """

        self.graph_widget_container.clear_widgets()
        current_view = self.current  # get current screenmanager state

        if self.graph == False:
            self.graph_view.add_widget(self.mercator_container)

        ###### Clean up previous view

        if current_view == "table":
            Clock.unschedule(self.update_table)
            self.table_view.clear_widgets()
            for country in self.country_dictionary:
                country_widget = self.country_dictionary[country][0]
                country_widget.icon_scatter_widget.remove_widget(country_widget.label)

        elif current_view == "malicious":
            Clock.unschedule(self.update_malicious_table)
            self.malicious_view.clear_widgets()
            for country in self.country_dictionary:
                country_widget = self.country_dictionary[country][0]
                country_widget.icon_scatter_widget.remove_widget(country_widget.label)

        #####

        # Produce graph view

        if ( self.settings_panel.color_picker_popup_open == True ) and (self.settings_panel.color_picker_layout not in self.persistent_widget_container.children):
            self.persistent_widget_container.add_widget(self.settings_panel.color_picker_layout)

        if self.misc_update_dictionary["my_computer"]:
            self.persistent_widget_container.add_widget(self.misc_update_dictionary["my_computer"].menu_popup)

        for country in self.misc_update_dictionary["country"].keys():
            self.persistent_widget_container.add_widget(self.misc_update_dictionary["country"][country].menu_popup)

        for city in self.misc_update_dictionary["city"].keys():
            self.persistent_widget_container.add_widget(self.misc_update_dictionary["city"][city].menu_popup)

        for ip in self.misc_update_dictionary["ip"].keys():
                self.persistent_widget_container.add_widget(self.misc_update_dictionary["ip"][ip].menu_popup)

        for widget in self.graph_widgets:
            self.graph_view.add_widget(widget)
 

        self.transition.direction = "right"
        self.current = "graph"  # set screenmanager view



    def set_table_view(self, button: Button) -> None:

        """
        Transition screenmanager to table view and display appropriate widgets.
        """

        current_view = self.current  # get current screenmanager state

        ##### Clean up previous view
        if current_view == "graph":
            self.graph_view.clear_widgets()

            if self.settings_panel.color_picker_popup_open == True:
                self.persistent_widget_container.remove_widget(self.settings_panel.color_picker_layout)

            if self.misc_update_dictionary["my_computer"]:
                self.persistent_widget_container.remove_widget(self.misc_update_dictionary["my_computer"].menu_popup)

            for country in self.misc_update_dictionary["country"].keys():
                self.persistent_widget_container.remove_widget(self.misc_update_dictionary["country"][country].menu_popup)

            for city in self.misc_update_dictionary["city"].keys():
                self.persistent_widget_container.remove_widget(self.misc_update_dictionary["city"][city].menu_popup)

            for ip in self.misc_update_dictionary["ip"].keys():
                self.persistent_widget_container.remove_widget(self.misc_update_dictionary["ip"][ip].menu_popup)

        elif current_view == "malicious":
            Clock.unschedule(self.update_malicious_table)
            self.malicious_view.clear_widgets()
        #####

        # Produce table view
        for widget in self.table_widgets:
            self.table_view.add_widget(widget)

        self.transition.direction = "down"
        self.current = "table"  # set screenmanager view

        Clock.schedule_interval(self.update_table, 1)



    def set_malicious_view(self, button: Button) -> None:

        """
        Transition screenmanager to malicious view and display appropriate widgets.
        """

        current_view = self.current  # get current screenmanager state

        ##### Clean up previous view
        if current_view == "graph":
            self.graph_view.clear_widgets()

            if self.settings_panel.color_picker_popup_open == True:
                self.persistent_widget_container.remove_widget(self.settings_panel.color_picker_layout)

            if self.misc_update_dictionary["my_computer"]:
                self.persistent_widget_container.remove_widget(self.misc_update_dictionary["my_computer"].menu_popup)

            for country in self.misc_update_dictionary["country"].keys():
                self.persistent_widget_container.remove_widget(self.misc_update_dictionary["country"][country].menu_popup)

            for city in self.misc_update_dictionary["city"].keys():
                self.persistent_widget_container.remove_widget(self.misc_update_dictionary["city"][city].menu_popup)

            for ip in self.misc_update_dictionary["ip"].keys():
                self.persistent_widget_container.remove_widget(self.misc_update_dictionary["ip"][ip].menu_popup)

        elif current_view == "table":
            Clock.unschedule(self.update_table)
            self.table_view.clear_widgets()
        #####

        # Produce malicious view

        for widget in self.malicious_widgets:
            self.malicious_view.add_widget(widget)

        self.transition.direction = "up"
        self.current = "malicious"  # set screenmanager view

        self.malicious_data_in_button.text = f'[color=FF0000] Data IN (MB)[/color]   {icon("fa-sort")}'

        self.malicious_data_out_button.text = f'[color=FF0000] Data OUT (MB)[/color]   {icon("fa-sort")} '

        Clock.schedule_interval(self.update_malicious_table, 0.5)



    def update_mercator_particles(self, dt):

        """
        Animate particles for world view (mercator)
        """

        for country in self.country_dictionary:

            for city in self.country_dictionary[country][1]:
                data_in = 0
                data_out = 0

                for ip in self.country_dictionary[country][1][city][1:]:

                    data_in += ip.data_in_delta
                    data_out += ip.data_out_delta

                    ip.data_in_delta = 0
                    ip.data_out_delta = 0

                if data_in > 0:
                    self.country_dictionary[country][1][city][0].animate_mercator(data_in)



    def update_table(self, time_delta) -> None:

        """
        Scheduled function for updating data in the table view
        """

        cursor = db.cursor()

        for n, ip in enumerate(self.sniffer_dictionary.keys()):

            data_out = self.sniffer_dictionary[ip]["data_out"]
            data_in = self.sniffer_dictionary[ip]["data_in"]
            total_packets = self.sniffer_dictionary[ip]["packet_count"]

            time_stamp = datetime.datetime.fromtimestamp(self.sniffer_dictionary[ip]["new_packet_timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    
            display_stamp = datetime.datetime.fromtimestamp(self.sniffer_dictionary[ip]["new_packet_timestamp"]).strftime("%H:%M:%S %d-%m-%Y")

            ip_widget = self.ip_dictionary[ip]


            delta_time = time.time() - ip_widget.new_packet_timestamp
            opacity = map_to_range(delta_time, self.new_packet_color_opacity, 0, 0.6, 1)
            

      

            if opacity < 0.6:
                protocol_color = (1, 1, 1, 0.3)

            else:
                protocol_color  = self.config_variables_dict["color_dictionary"][ip_widget.ip_data["last_packet"] + " Protocol Color"].copy()
                protocol_color.append(opacity)
                    
            ip_widget.protocol_color = protocol_color


            self.live_table_dictionary[ip].children[0].text = f"{self.sniffer_dictionary[ip]['data_out']/1000000:.6f}"
            self.live_table_dictionary[ip].children[0].color = protocol_color

            self.live_table_dictionary[ip].children[1].text = f"{self.sniffer_dictionary[ip]['data_in']/1000000:.6f}"
            self.live_table_dictionary[ip].children[1].color = protocol_color

            self.live_table_dictionary[ip].children[2].text = str(total_packets)
            self.live_table_dictionary[ip].children[2].color = protocol_color

            self.live_table_dictionary[ip].children[3].text = display_stamp
            self.live_table_dictionary[ip].children[3].color = protocol_color

            cursor.execute(f"""UPDATE OR IGNORE Live SET time_stamp = "{time_stamp}", total_packets = "{total_packets}", data_in = "{data_in}", data_out = "{data_out}" WHERE ip = "{ip}" """)

            db.commit()



    def update_malicious_table(self, time_delta) -> None:

        """
        Scheduled function for updating data in the malicious table view
        """

        cursor = db.cursor()

        for ip in self.malicious_table_dictionary.keys():

            if ip not in self.sniffer_dictionary:
                pass

            else:

                ip_widget = self.ip_dictionary[ip]

                data_out = self.sniffer_dictionary[ip]["data_out"]
                data_in = self.sniffer_dictionary[ip]["data_in"]
                packet_count = self.sniffer_dictionary[ip]["packet_count"]
                time_stamp = datetime.datetime.fromtimestamp(self.sniffer_dictionary[ip]["new_packet_timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
    
                display_stamp = datetime.datetime.fromtimestamp(self.sniffer_dictionary[ip]["new_packet_timestamp"]).strftime("%H:%M:%S %d-%m-%Y")

                delta_time = time.time() - ip_widget.new_packet_timestamp
                opacity = map_to_range(delta_time, self.new_packet_color_opacity, 0, 0.6, 1)

                
                if opacity < 0.6:
                    protocol_color = (1, 1, 1, 0.3)

                else:
                    protocol_color  = self.config_variables_dict["color_dictionary"][ip_widget.ip_data["last_packet"] + " Protocol Color"].copy()
                    protocol_color.append(opacity)
                        
                ip_widget.protocol_color = protocol_color
            
              

                self.malicious_table_dictionary[ip].children[0].text = f"{self.sniffer_dictionary[ip]['data_out']/1000000:.6f}"
                self.malicious_table_dictionary[ip].children[0].color = protocol_color


                self.malicious_table_dictionary[ip].children[1].text = f"{self.sniffer_dictionary[ip]['data_in']/1000000:.6f}"
                self.malicious_table_dictionary[ip].children[1].color = protocol_color

                self.malicious_table_dictionary[ip].children[2].text = str(packet_count)
                self.malicious_table_dictionary[ip].children[2].color = protocol_color

                self.malicious_table_dictionary[ip].children[3].text = display_stamp
                self.malicious_table_dictionary[ip].children[3].color = protocol_color
                
                current_connection_key = self.current_connection_key.replace(" ", "")
                malicious_ips_database_name = current_connection_key + "_malicious_ips"
                cursor.execute(f"""UPDATE OR IGNORE {malicious_ips_database_name} SET display_stamp = "{display_stamp}", time_stamp = "{time_stamp}", packet_count = "{packet_count}", data_in = "{data_in}", data_out = "{data_out}" WHERE ip = "{ip}" """
                )

                db.commit()



    def sort_table(self, calling_button: Button) -> None:

        """
        Callable to sort the Table View data if one of the header columns is clicked
        """

        cursor = db.cursor()

        if calling_button.count % 2 == 0:
            cursor.execute(f"""SELECT * FROM Live ORDER BY "{calling_button.sorting_key}" DESC""")

        else:
            cursor.execute(f"""SELECT * FROM Live ORDER BY "{calling_button.sorting_key}" ASC""")

        calling_button.count += 1


        sorted_ips = cursor.fetchall()
        
        self.live_table.clear_widgets()
        self.table_count = 0

        for ip in sorted_ips:

            if self.table_count % 2 == 0 and ip[0] not in self.malicious_table_dictionary:

                for n, row_item in enumerate(self.live_table_dictionary[ip[0]].children):

                    if isinstance(row_item, BoxLayout):
                        row_item.children[1].background_color = (0, 1, 0, 0.8)

                    elif n in (0, 1, 2, 3):
                        row_item.color = self.ip_dictionary[ip[0]].protocol_color
                    
                    else:
                        row_item.color = (1, 1, 1, 1)

            elif self.table_count % 2 != 0 and ip[0] not in self.malicious_table_dictionary:

                for n, row_item in enumerate(self.live_table_dictionary[ip[0]].children):

                    if isinstance(row_item, BoxLayout):

                        row_item.children[1].background_color = (0, 1, 0, 0.3)

                    elif n in (0, 1, 2, 3):
                        row_item.color = self.ip_dictionary[ip[0]].protocol_color
                    
                    else:
                        row_item.color = (1, 1, 1, 0.7)

            
            self.live_table.add_widget(self.live_table_dictionary[ip[0]])
            self.table_count += 1



    def sort_malicious_table(self, calling_button: Button) -> None:

        """
        Callable to sort the Malicious Table View data if one of the header columns is clicked
        """

        cursor = db.cursor()

        current_connection_key = self.current_connection_key.replace(" ", "")
        malicious_ips_database_name = current_connection_key + "_malicious_ips"

        if calling_button.count % 2 == 0:

            cursor.execute(f"""SELECT * FROM {malicious_ips_database_name} ORDER BY "{calling_button.sorting_key}" DESC""")

        else:
            cursor.execute(f"""SELECT * FROM {malicious_ips_database_name} ORDER BY "{calling_button.sorting_key}" ASC""")

        calling_button.count += 1

        sorted_ips = cursor.fetchall()

        self.malicious_table.clear_widgets()
        self.malicious_table_count = 0

        for ip in sorted_ips:

            if self.malicious_table_count % 2 == 0:
                for n, row_item in enumerate(self.malicious_table_dictionary[ip[0]].children):
                    if isinstance(row_item, BoxLayout):
                        row_item.children[1].background_color = (0.3, 0.3, 0.3, 1)

                    elif n in (0, 1, 2, 3):

                        if ip[0] in self.ip_dictionary:
                            row_item.color = self.ip_dictionary[ip[0]].banned_color_opacity
                        else:
                            row_item.color = (1, 1, 1, 0.3)

                    else:
                        row_item.color = (1, 1, 1, 1)

            else:

                for n, row_item in enumerate(self.malicious_table_dictionary[ip[0]].children):
                    if isinstance(row_item, BoxLayout):
                        row_item.children[1].background_color = (0.15, 0.15, 0.15, 1)

                    elif n in (0, 1, 2, 3):
                        if ip[0] in self.ip_dictionary:
                            row_item.color = self.ip_dictionary[ip[0]].banned_color_opacity
                        else:
                            row_item.color = (1, 1, 1, 0.3)

                    else:
                        row_item.color = (1, 1, 1, 0.7)

            self.malicious_table.add_widget(self.malicious_table_dictionary[ip[0]])
            self.malicious_table_count += 1



    
    def make_settings_panel(self) -> None:

        """
        Convience function for constructing Settings Panel -- need to construct this first before make_GUI_widgets().
        """

        self.settings_panel = Settings_Panel(resource_path=self.resource_path)
        self.settings_panel.gui_manager = self

        if self.first_time_starting == True:
            self.settings_panel.generate_keys()

        self.settings_panel.init_accordion()



    def toggle_mercator_graph_display(self, checkbox: CheckBox, value: bool) -> None:

        """
        Toggle between mercator and graph display
        """

        if value == True:

            self.graph_view.add_widget(self.mercator_container, len(self.graph_view.children) + 1)

        else:
            self.graph_view.remove_widget(self.mercator_container)



    def toggle_mercator_graph_position(self, checkbox: CheckBox, value: bool) -> None:

        """
        Set positions for mercator or graph display
        """

        if value == True:

            for country in self.country_dictionary:
                country_widget = self.country_dictionary[country][0]
                country_widget.set_mercator_layout()

                for city in self.country_dictionary[country][1]:
                    city_widget = self.country_dictionary[country][1][city][0]
                    city_widget.set_mercator_layout()

                    for ip_widget in self.country_dictionary[country][1][city][1:]:
                        ip_widget.set_mercator_layout()

        else:

            for country in self.country_dictionary:
                country_widget = self.country_dictionary[country][0]
                country_widget.set_graph_layout()

                for city in self.country_dictionary[country][1]:
                    city_widget = self.country_dictionary[country][1][city][0]
                    city_widget.set_graph_layout()

                    for ip_widget in self.country_dictionary[country][1][city][1:]:
                        ip_widget.set_graph_layout()



    def make_GUI_widgets(self) -> None:

        """
        Convience function for constructing GUI widgets.
        """

        self.graph_widget_container = FloatLayout()
        self.persistent_widget_container = FloatLayout()

        self.persistent_widget_container.add_widget(self.settings_panel.connection_label_layout)

        # Building menu icons (triggers view changes)
        self.main_settings_icon = self.make_icon(
                                                image=os.path.join(self.resource_path, "assets/images/UI/shield.png"),
                                                on_press_toggle=self.settings_panel_toggle,
                                                icon_pos=self.config_variables_dict["position_dictionary"]["main_settings_icon_pos"],
                                                identity="main_settings",
                                                )   

        self.table_icon = self.make_icon(
                                        image=os.path.join(self.resource_path, "assets/images/UI/table_view.png"),
                                        on_press_toggle=self.set_table_view,
                                        icon_pos=self.config_variables_dict["position_dictionary"]["table_icon_pos"],
                                        identity="table_icon",
                                        )

        self.graph_icon = self.make_icon(
                                        image=os.path.join(self.resource_path, "assets/images/UI/graph.png"),
                                        on_press_toggle=self.set_graph_view,
                                        icon_pos=self.config_variables_dict["position_dictionary"]["graph_icon_pos"],
                                        identity="graph_icon",
                                        )

        self.malicious_icon = self.make_icon(
                                            image=os.path.join(self.resource_path, "assets/images/UI/malicious.png"),
                                            on_press_toggle=self.set_malicious_view,
                                            icon_pos=self.config_variables_dict["position_dictionary"]["malicious_icon_pos"],
                                            identity="malicious_icon",
                                            )

        # Building Graph Wigets
        self.my_computer = My_Computer(
                                        id="My Computer",
                                        window_x=self.window_x,
                                        window_y=self.window_y,
                                        gui_manager=self,
                                        center_position=(self.center_x, self.center_y),
                                        resource_path=self.resource_path,
                                        current_connection_key = self.current_connection_key
                                        )

        self.mercator_container = Widget()  # for mercator background image
        self.mercator_container.size = (self.window_x, self.window_y)

        self.mercator_image = Image(
            source = os.path.join(self.resource_path, "assets/images/UI/mercator.png"),
            size_hint = (None, None),
            keep_ratio = False,
            allow_stretch = True,
            size = (self.window_x, self.window_y),
        )

        self.mercator_container.add_widget(self.mercator_image)

        # Building Table  Widgets
        self.table_scroll = ScrollView( scroll_distance=50, size_hint_y = self.window_ratio - 0.05, pos = (0, dp(48)) )

        self.live_table = GridLayout(
            size_hint = (None, None),
            col_default_width = self.window_x / 2,
            row_default_height = dp(25),
            cols = 1,
            padding = (dp(5), 0),
        )

        self.live_table.bind(minimum_height=self.live_table.setter("height"))
        self.live_table.bind(minimum_width=self.live_table.setter("width"))
   
        self.box_header_container = AnchorLayout(anchor_y="top")
        self.box_header = self.create_table_header()

        self.box_header_container.add_widget(self.box_header)
        self.table_scroll.add_widget(self.live_table)



    def clear_malicious_table(self, *args) -> None:

        """
        Clear malcious_ips table and re-create it.
        """
        
        cursor = db.cursor()

        current_connection_key = self.current_connection_key.replace(" ", "")
        malicious_ips_database_name = current_connection_key + "_malicious_ips"

        cursor.execute(f"SELECT * from {malicious_ips_database_name}")
        malicious_ips = cursor.fetchall()

        for ip in malicious_ips:
            try:
                self.ip_dictionary[ip[0]].tag()
            except:
                pass
         

        cursor.execute(f"DELETE FROM {malicious_ips_database_name}")
        cursor.execute("VACUUM")

        db.commit()

        self.malicious_table_dictionary.clear()
        self.malicious_table.clear_widgets()

        self.malicious_table_dropdown.dismiss()



    def open_malicious_dropdown(self, calling_button: Button) -> None:

        """
        Kivy dropdown bug hack
        """

        self.malicious_table_dropdown.open(calling_button)



    def clear_livetable(self, *args) -> None:

        """ 
        Reset Live Table
        """

        cursor = db.cursor()
        cursor.execute("DELETE FROM Live")
        cursor.execute("VACUUM")

        db.commit()

        self.live_table.clear_widgets()
        self.live_table_dictionary = {}
        self.livetable_dropdown.dismiss()



    def save_live_table(self, *args) -> None:

        """
        Save sniffer dictionary into sqlite database
        """

        json_session_data = self.sniffer_dictionary # JSON serialization faciliated by sqlite registration on insertion (see database_config.py for dictionary type)

        time_stamp = time.time()
        date_timestamp = datetime.datetime.fromtimestamp(time_stamp).strftime("%Y-%m-%d %H:%M:%S")

         
        cursor = db.cursor()
        cursor.execute(f"""INSERT OR IGNORE INTO sessions (session_name, session_data) VALUES ("{date_timestamp}", "{json_session_data}")""")
        db.commit()

        self.livetable_dropdown.dismiss()

    
    def save_malicious_table(self, *args) -> None:

        """ 
        Save sniffer dictionary into sqlite database
        """

        time_stamp = time.time()
        date_timestamp = datetime.datetime.fromtimestamp(time_stamp).strftime("%Y_%m_%d_%H_%M_%S")
        date_timestamp = "malicious_" + date_timestamp
         
        cursor = db.cursor()

        current_connection_key = self.current_connection_key.replace(" ", "")
        malicious_ips_database_name = current_connection_key + "_malicious_ips"

        cursor.execute(f"""CREATE TABLE {date_timestamp} AS SELECT * FROM {malicious_ips_database_name} WHERE 0""")

        cursor.execute(f"""INSERT INTO {date_timestamp} SELECT * FROM {malicious_ips_database_name};""")
        db.commit()

        self.malicious_table_dropdown.dismiss()



    def open_livetable_dropdown(self, calling_button: Button) -> None:

        """
        Kivy dropdown bug hack
        """

        self.livetable_dropdown.open(calling_button)


    def ip_malicious_dropdown(self, dropdown, button):

        """
        Kivy dropdown bug hack
        """

        dropdown.open(button)



    def init_database_(self):

        """
        Initialize sqlite3 database
        """

        cursor = db.cursor()
        
        cursor.execute("DROP TABLE IF EXISTS Live")
        db.commit()

        cursor.execute(
            "CREATE TABLE Live (ip TEXT PRIMARY KEY, description TEXT DEFAULT 'NONE', time_stamp TEXT DEFAULT 'NONE', location_city TEXT DEFAULT 'NONE', location_country TEXT DEFAULT 'NONE', longitude INTEGER, latitude INTEGER, total_packets INTEGER DEFAULT 0, data_in INTEGER DEFAULT 0, data_out INTEGER DEFAULT 0, tcp_packets INTEGER DEFAULT 0, udp_packets INTEGER DEFAULT 0, other_packets INTEGER DEFAULT 0, blocked INTEGER DEFAULT 0, safe_listed INTEGER DEFAULT 0, flagged INTEGER DEFAULT 0)"
        )


        cursor.execute("CREATE TABLE IF NOT EXISTS sessions (session_name TEXT PRIMARY KEY, session_data dictionary )")

  

        for stored_connection in self.config_variables_dict["stored_connections"]:

            stored_connection = stored_connection.replace(" ", "")
            malicious_ips_database_name = stored_connection + "_malicious_ips"


            #TODO: Error handling for unaccetable table names i.e. names that start with a number
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {malicious_ips_database_name} (ip TEXT PRIMARY KEY, description TEXT DEFAULT 'NONE', ban_lists INTEGER DEFAULT 0, display_stamp TEXT DEFAULT 'NONE', time_stamp TEXT DEFAULT 'NONE', location_country TEXT DEFAULT 'NONE', packet_count INTEGER DEFAULT 0, data_in INTEGER DEFAULT 0, data_out INTEGER DEFAULT 0,  ip_data dictionary, abuse_email TEXT DEFAULT 'NONE', whois_info dictionary)"
                )

        db.commit()

      

        


        #TODO: Place these somewhere else.. 
        self.malicious_ip_scroll = ScrollView(
                                                scroll_distance=50,
                                                size_hint_y=self.window_ratio - 0.05,
                                                size_hint_x=1,
                                                pos=(0, dp(48)),
                                                )   


        self.livetable_dropdown = DropDown()

        clear_livetable_button = Button(
                                        text="Save Session Data",
                                        size_hint=(None, None),
                                        width=dp(200),
                                        height=dp(25),
                                        background_color=(1, 1, 1, 0.3),
                                        border = (0,0,0,0),
                                        on_press=self.save_live_table,
                                        )

        self.livetable_dropdown.add_widget(clear_livetable_button)

        livetable_menu_button = Button(
                                        text="Menu",
                                        pos=(self.center_x - dp(100), dp(5)),
                                        size_hint=(None, None),
                                        size=(dp(200), dp(25)),
                                        background_color=(1, 1, 1, 0.3),
                                        border = (0,0,0,0)
                                        )   

        livetable_menu_button.bind(on_press=self.open_livetable_dropdown)

        self.livetable_menu = FloatLayout()
        self.livetable_menu.add_widget(livetable_menu_button)



        self.malicious_table_dropdown = DropDown()

        clear_malicious_table_button = Button(
                                            text="Clear Table",
                                            size_hint=(None, None),
                                            width=dp(200),
                                            height=dp(25),
                                            background_color=(1, 1, 1, 0.3),
                                            border = (0,0,0,0),
                                            on_press=self.clear_malicious_table,
                                            )

        save_malicious_table_button = Button(
                                            text="Save Malicious Data",
                                            size_hint=(None, None),
                                            width=dp(200),
                                            height=dp(25),
                                            background_color=(1, 1, 1, 0.3),
                                            border = (0,0,0,0),
                                            on_press=self.save_malicious_table,
                                            )                                            

        self.malicious_table_dropdown.add_widget(clear_malicious_table_button)
        self.malicious_table_dropdown.add_widget(save_malicious_table_button)

        malicious_menu_button = Button(
                                        text="Menu",
                                        pos=(self.center_x - dp(100), dp(5)),
                                        size_hint=(None, None),
                                        size=(dp(200), dp(25)),
                                        border = (0,0,0,0),
                                        background_color=(1, 1, 1, 0.3),
                                        )
        malicious_menu_button.bind(on_press=self.open_malicious_dropdown)

        self.malicious_menu = FloatLayout()
        self.malicious_menu.add_widget(malicious_menu_button)

        self.malicious_table = GridLayout(
                                            size_hint=(None, None),
                                            col_default_width=self.window_x,
                                            row_default_height=dp(25),
                                            cols=1,
                                            padding=(dp(5), 0),
                                            )

        self.malicious_table.bind(minimum_height=self.malicious_table.setter("height"))
        self.malicious_table.bind(minimum_width=self.malicious_table.setter("width"))

        self.malicious_ip_container = AnchorLayout(anchor_y="top", anchor_x="left")
        self.malicious_ip_header = self.create_malicious_header()

        self.malicious_ip_scroll.add_widget(self.malicious_table)
        self.malicious_ip_container.add_widget(self.malicious_ip_header)
        


    def populate_malicious_table(self) -> None:

        """
        Populate malicious table view from malicious sqlite table
        """

        cursor = db.cursor()

        current_connection_key = self.current_connection_key.replace(" ", "")

        malicious_ips_database_name = current_connection_key + "_malicious_ips"
        cursor.execute(f"SELECT * from {malicious_ips_database_name}")
        malicious_ips = cursor.fetchall()

        for ip in malicious_ips:
        
            self.malicious_ips_local_database[ip[0]] = ip[2] # ip_key : confidence_score
            malicious_row = self.generate_malicious_table_row(ip)
            self.malicious_table_dictionary[ip[0]] = malicious_row
            self.malicious_table.add_widget(malicious_row)



    def untag_ip(self, button, dropdown) -> None:

        """
        Untag malicious IP
        """

        ip = button.data[0]
        dropdown.dismiss()

        if ip in self.ip_dictionary:
            self.ip_dictionary[ip].tag()
        
        else:
            
            malicious_row = self.malicious_table_dictionary[ip]
            self.malicious_table.remove_widget(malicious_row)
            del self.malicious_table_dictionary[ip]
            del self.malicious_ips_local_database[ip]

            current_connection_key = self.current_connection_key.replace(" ", "")

            malicious_ips_database_name = current_connection_key + "_malicious_ips"
            cursor = db.cursor()
            sql = f"""DELETE FROM {malicious_ips_database_name} WHERE ip="{ip}" """
            cursor.execute(sql)
            db.commit()

    

    def copy_ip_address(self, calling_button:Button, dropdown) -> None:

        """
        Copy IP address to clipboard
        """

        try: #Some OS's may not have clipboard functionality
            pyperclip.copy(calling_button.data[0])
        except:
            pass

        dropdown.dismiss()



    def copy_abuse_emails(self, calling_button:Button, dropdown) -> None:

        """
        Copy IP Abuse emails to clipboard
        """

        try: #Some OS's may not have clipboard functionality
            pyperclip.copy(calling_button.data[9])
        except: 
            pass

        dropdown.dismiss()



    def copy_whois_information(self, calling_button:Button, dropdown) -> None:
        
        """
        Copy whois information to clipboard
        """

        try: #Some OS's may not have clipboard functionality
            whois_information = calling_button.data[10]
            pyperclip.copy(str(whois_information))
        except:
            pass

        dropdown.dismiss()


    

    def generate_malicious_table_row(self, ip_data: tuple) -> BoxLayout:

        """
        Construct a row for Malicious view
        """
      

        length_per_label = self.window_x / 6

        box_layout = BoxLayout(
                                orientation="horizontal",
                                size_hint=(None, None),
                                pos=(0, 0),
                                padding=1,
                                size=(self.window_x, dp(30)),
                            )

        ip_dropdown = DropDown()

        dropdown_tag_button = Button(
                                    text="Untag",
                                    size_hint=(None, None),
                                    width=sp(135),
                                    height=sp(22),
                                    border = (0,0,0,0),
                                    color=(0,1,0,1),
                                    background_color=(0, 0, 0, 0.8),
                                )

        dropdown_tag_button.data = ip_data

        dropdown_tag_button.bind(on_release=lambda btn = dropdown_tag_button, ip_dropdown=ip_dropdown: self.untag_ip(btn, ip_dropdown))

        ip_dropdown.add_widget(dropdown_tag_button)


        btn = Button(
                    text="Copy IP Address",
                    size_hint=(None, None),
                    width=sp(135),
                    height=sp(22),
                    color=(1, 1, 1, 1),
                    border = (0,0,0,0),
                    background_color = (0, 0, 0, 0.8),
                    )

        btn.data = ip_data
        btn.bind(on_release=lambda btn = btn, ip_dropdown=ip_dropdown: self.copy_ip_address(btn, ip_dropdown))
        ip_dropdown.add_widget(btn)


        btn = Button(
                    text="Copy Abuse Email",
                    size_hint=(None, None),
                    width=sp(135),
                    height=sp(22),
                    color=(1, 1, 1, 1),
                    background_color = (0, 0, 0, 0.8),
                    )

        btn.data = ip_data
        btn.bind(on_release=lambda btn = btn, ip_dropdown=ip_dropdown: self.copy_abuse_emails(btn, ip_dropdown))
        ip_dropdown.add_widget(btn)

        btn = Button(
                    text="Copy Whois Info",
                    size_hint=(None, None),
                    width=sp(135),
                    height=sp(22),
                    color=(1, 1, 1, 1),
                    background_color = (0, 0, 0, 0.8),
                    )

        btn.data = ip_data
        btn.bind(on_release=lambda btn = btn, ip_dropdown=ip_dropdown: self.copy_whois_information(btn, ip_dropdown))
        ip_dropdown.add_widget(btn)


        ip_button = Button()
        ip_button.text = ip_data[0]
        ip_button.id = ip_data[0]
        ip_button.border = (0,0,0,0)
        ip_button.on_press = lambda call_button=ip_button, ip_dropdown=ip_dropdown: self.ip_malicious_dropdown(ip_dropdown, call_button)


        if self.malicious_table_count % 2 == 0:
            ip_button.background_color = (0.3, 0.3, 0.3, 1)
            ip_button.color = (1, 0, 0, 1)
            text_color = (1, 1, 1, 1)

        else:
            ip_button.background_color = (0.15, 0.15, 0.15, 1)
            ip_button.color = (1, 0, 0, 1)
            text_color = (1, 1, 1, 0.7)

        self.malicious_table_count += 1

        description_label = self.make_label(ip_data[1], length_per_label)
        description_label.color = text_color

        banlist_count_label = self.make_label(str(ip_data[2]), length_per_label)
        banlist_count_label.color = text_color

        country_label = self.make_label(ip_data[5], length_per_label)
        country_label.color = text_color

        timestamp_label = self.make_label(ip_data[3], length_per_label)
        timestamp_label.color = (1, 1, 1, 0.3)

        packet_label = self.make_label(str(ip_data[6]), length_per_label)
        packet_label.color = (1, 1, 1, 0.3)

        data_in_label = self.make_label(f"{ip_data[7]/1000000:.6f}", length_per_label)
        data_in_label.color = (1, 1, 1, 0.3)

        data_out_label = self.make_label(f"{ip_data[8]/1000000:.6f}", length_per_label)
        data_out_label.color = (1, 1, 1, 0.3)

        ip_button_container = BoxLayout(orientation="horizontal")
        ip_button_container.add_widget(Label(size_hint_x=0.1))
        ip_button_container.add_widget(ip_button)
        ip_button_container.add_widget(Label(size_hint_x=0.1))

        box_layout.add_widget(ip_button_container)
        box_layout.add_widget(description_label)
        box_layout.add_widget(banlist_count_label)
        box_layout.add_widget(country_label)
        box_layout.add_widget(timestamp_label)
        box_layout.add_widget(packet_label)
        box_layout.add_widget(data_in_label)
        box_layout.add_widget(data_out_label)

        return box_layout




    def create_table_header(self) -> BoxLayout:

        """
        Convience function for creating table view header buttons
        """

        register(
                "default_font",
                os.path.join(self.resource_path, "assets/fonts/fontawesome-webfont"),
                os.path.join(self.resource_path, "assets/fonts/font-awesome.fontd"),
                )

        box = BoxLayout(
                        orientation="horizontal",
                        pos_hint=(None, None),
                        size_hint=(None, 0.04),
                        size=(self.window_x, 0),
                        )

        self.ip_label_header = Button()
        self.ip_label_header.text = f'IP Address   {icon("fa-sort")}'
        self.ip_label_header.sorting_key = "ip"
        self.ip_label_header.border = (0,0,0,0)
        self.ip_label_header.background_color = (0.3, 0.3, 0.3, 0.7)
        self.ip_label_header.on_press = lambda: self.sort_table( calling_button=self.ip_label_header)
        self.ip_label_header.count = 0
        self.ip_label_header.markup = True

        description_button = Button()
        description_button.text = f'Description   {icon("fa-sort")}'
        description_button.sorting_key = "description"
        description_button.on_press = lambda: self.sort_table( calling_button=description_button)
        description_button.background_color = (0.3, 0.3, 0.3, 0.7)
        description_button.count = 0
        description_button.markup = True
        description_button.border = (0,0,0,0)

        city_button = Button()
        city_button.text = f'City   {icon("fa-sort")}'
        city_button.sorting_key = "location_city"
        city_button.on_press = lambda: self.sort_table(calling_button=city_button)
        city_button.background_color = (0.3, 0.3, 0.3, 0.7)
        city_button.count = 0
        city_button.markup = True
        city_button.border = (0,0,0,0)

        country_button = Button()
        country_button.text = f'Country   {icon("fa-sort")}'
        country_button.sorting_key = "location_country"
        country_button.on_press = lambda: self.sort_table(calling_button=country_button)
        country_button.background_color = (0.3, 0.3, 0.3, 0.7)
        country_button.count = 0
        country_button.markup = True
        country_button.border = (0,0,0,0)

        last_packet_timestamp_button = Button()
        last_packet_timestamp_button.text = f'Last Packet   {icon("fa-sort")}'
        last_packet_timestamp_button.sorting_key = "time_stamp"
        last_packet_timestamp_button.on_press = lambda: self.sort_table(calling_button=last_packet_timestamp_button)
        last_packet_timestamp_button.background_color = (0.3, 0.3, 0.3, 0.7)
        last_packet_timestamp_button.count = 0
        last_packet_timestamp_button.markup = True
        last_packet_timestamp_button.border = (0,0,0,0)

        packets_button = Button()
        packets_button.text = f'Total Packets   {icon("fa-sort")}'
        packets_button.sorting_key = "total_packets"
        packets_button.on_press = lambda: self.sort_table(calling_button=packets_button)
        packets_button.background_color = (0.3, 0.3, 0.3, 0.7)
        packets_button.count = 0
        packets_button.markup = True
        packets_button.border = (0,0,0,0)

        self.live_data_in_button = Button()
        self.live_data_in_button.markup = True
        # self.live_data_in_button.text = f'[color={get_hex_from_color(self.config_variables_dict["Data IN Color"])}] Data IN (MB) [/color]'
        self.live_data_in_button.sorting_key = "data_in"
        self.live_data_in_button.on_press = lambda: self.sort_table( calling_button=self.live_data_in_button )
        self.live_data_in_button.background_color = (0.3, 0.3, 0.3, 0.7)
        self.live_data_in_button.count = 0
        self.live_data_in_button.border = (0,0,0,0)

        self.live_data_out_button = Button()
        self.live_data_out_button.markup = True
        # self.live_data_out_button.text = f'[color={get_hex_from_color(self.config_variables_dict["Data OUT Color"])}] Data OUT (MB) [/color]'
        self.live_data_out_button.sorting_key = "data_out"
        self.live_data_out_button.on_press = lambda: self.sort_table( calling_button=self.live_data_out_button )
        self.live_data_out_button.background_color = (0.3, 0.3, 0.3, 0.7)
        self.live_data_out_button.count = 0
        self.live_data_out_button.border = (0,0,0,0)

        box.add_widget(self.ip_label_header)
        box.add_widget(description_button)
        box.add_widget(city_button)
        box.add_widget(country_button)
        box.add_widget(last_packet_timestamp_button)
        box.add_widget(packets_button)
        box.add_widget(self.live_data_in_button)
        box.add_widget(self.live_data_out_button)

        return box



    def create_malicious_header(self) -> BoxLayout:

        """
        Convience function for building malicious view header buttons.
        """

        box = BoxLayout(
                        orientation="horizontal",
                        pos_hint=(None, None),
                        size_hint=(None, 0.04),
                        size=(self.window_x, 0),
                        )

        self.malicious_ip_label_header = Button()
        self.malicious_ip_label_header.text = f'[color=FF0000]Malicious IP[/color]   {icon("fa-sort")}'
        self.malicious_ip_label_header.sorting_key = "ip"
        self.malicious_ip_label_header.background_color = (0.3, 0.3, 0.3, 0.8)
        self.malicious_ip_label_header.count = 0
        self.malicious_ip_label_header.on_press = lambda: self.sort_malicious_table( calling_button=self.malicious_ip_label_header)
        self.malicious_ip_label_header.markup = True
        self.malicious_ip_label_header.border = (0,0,0,0)

        description_button = Button()
        description_button.text = f'[color=FF0000]Description[/color]   {icon("fa-sort")}'
        description_button.sorting_key = "description"
        description_button.on_press = lambda: self.sort_malicious_table( calling_button=description_button )
        description_button.background_color = (0.3, 0.3, 0.3, 0.8)
        description_button.count = 0
        description_button.markup = True
        description_button.border = (0,0,0,0)

        ban_lists_button = Button()
        ban_lists_button.text = f'[color=FF0000]# of Ban Lists[/color]   {icon("fa-sort")}'
        ban_lists_button.sorting_key = "ban_lists"
        ban_lists_button.on_press = lambda: self.sort_malicious_table(calling_button=ban_lists_button)
        ban_lists_button.background_color = (0.3, 0.3, 0.3, 0.8)
        ban_lists_button.count = 0
        ban_lists_button.markup = True
        ban_lists_button.border = (0,0,0,0)

        time_stamp_button = Button()
        time_stamp_button.text = f'[color=FF0000]Last Packet[/color]   {icon("fa-sort")}'
        time_stamp_button.sorting_key = "time_stamp"
        time_stamp_button.on_press = lambda: self.sort_malicious_table(calling_button=time_stamp_button)
        time_stamp_button.background_color = (0.3, 0.3, 0.3, 0.8)
        time_stamp_button.count = 0
        time_stamp_button.markup = True
        time_stamp_button.border = (0,0,0,0)

        country_button = Button()
        country_button.text = f'[color=FF0000]Country[/color]   {icon("fa-sort")}'
        country_button.sorting_key = "location_country"
        country_button.on_press = lambda: self.sort_malicious_table(calling_button=country_button)
        country_button.background_color = (0.3, 0.3, 0.3, 0.8)
        country_button.count = 0
        country_button.markup = True
        country_button.border = (0,0,0,0)

        packets_button = Button()
        packets_button.text = f'[color=FF0000]Total Packets[/color]   {icon("fa-sort") }'
        packets_button.sorting_key = "packet_count"
        packets_button.on_press = lambda: self.sort_malicious_table(calling_button=packets_button)
        packets_button.background_color = (0.3, 0.3, 0.3, 0.8)
        packets_button.count = 0
        packets_button.markup = True
        packets_button.border = (0,0,0,0)

        self.malicious_data_in_button = Button()
        self.malicious_data_in_button.markup = True
        # self.malicious_data_in_button.text = f'[color={get_hex_from_color(self.config_variables_dict["Data IN Color"])}] Data IN (MB) [/color]'
        self.malicious_data_in_button.sorting_key = "data_in"
        self.malicious_data_in_button.on_press = lambda: self.sort_malicious_table(calling_button=self.malicious_data_in_button)
        self.malicious_data_in_button.background_color = (0.3, 0.3, 0.3, 0.8)
        self.malicious_data_in_button.count = 0
        self.malicious_data_in_button.border = (0,0,0,0)

        self.malicious_data_out_button = Button()
        self.malicious_data_out_button.markup = True
        # self.malicious_data_out_button.text = f'[color={get_hex_from_color(self.config_variables_dict["Data OUT Color"])}] Data OUT (MB) [/color]'
        self.malicious_data_out_button.sorting_key = "data_out"
        self.malicious_data_out_button.on_press = lambda: self.sort_malicious_table(calling_button=self.malicious_data_out_button)
        self.malicious_data_out_button.background_color = (0.3, 0.3, 0.3, 0.8)
        self.malicious_data_out_button.count = 0
        self.malicious_data_out_button.border = (0,0,0,0)

        box.add_widget(self.malicious_ip_label_header)
        box.add_widget(description_button)
        box.add_widget(ban_lists_button)
        box.add_widget(country_button)
        box.add_widget(time_stamp_button)
        box.add_widget(packets_button)
        box.add_widget(self.malicious_data_in_button)
        box.add_widget(self.malicious_data_out_button)

        return box



    def make_icon(self, image: str, on_press_toggle: Callable, icon_pos: int, identity: str) -> FloatLayout:

        """
        Convience function for creating menu GUI icons
        """

        if self.first_time_starting:
            position = [dp(icon_pos[0]), icon_pos[1]]

        else:
            position = [icon_pos[0], icon_pos[1]]

        icon_scatter_widget = Scatter(size_hint=(None, None), pos=position, size=(dp(40), dp(40)))

        with icon_scatter_widget.canvas.before:
            Color(1, 1, 1, 0.1)
            RoundedRectangle(
                            size=icon_scatter_widget.size,
                            pos=(0, 0),
                            radius=[
                                (dp(60), dp(50)),
                                (dp(50), dp(50)),
                                (dp(50), dp(50)),
                                (dp(50), dp(50)),
                            ]
                            )

        container = FloatLayout()
        container.pos = position
        container.size_hint = (None, None)
        container.size = (dp(40), dp(40))
        container.id = identity

        icon_image = Image(
                            source=image,
                            size_hint=(None, None),
                            pos=(dp(5), dp(5)),
                            size=(dp(30), dp(30)),
                          )

        toggle_button = Button(
                                on_press=on_press_toggle,
                                size_hint=(None, None),
                                size=(dp(20), dp(20)),
                                pos=(dp(10), dp(10)),
                                background_color=(0, 0, 0, 0),
                                border = (0,0,0,0)
                              )

        toggle_button.add_widget(icon_image)
        icon_scatter_widget.add_widget(toggle_button)
        container.add_widget(icon_scatter_widget)

        return container



    def make_label(self, text: str, length_per_label: float) -> Label:

        """
        Convience function to make kivy Labels with specified length.
        """

        custom_label = Label()
        custom_label.halign = "center"
        custom_label.text_size = (length_per_label, dp(30))
        custom_label.valign = "middle"
        custom_label.markup = True
        custom_label.shorten = True
        custom_label.text = text

        return custom_label



    def settings_panel_toggle(self, *button: Button) -> None:

        """
        Toggle settings menu on/off.
        """

        if self.settings_toggle_boolean == True:
            self.persistent_widget_container.remove_widget(
                self.settings_panel.settings_panel_scatter
            )
            self.settings_toggle_boolean = False

        else:
            self.persistent_widget_container.add_widget(
                self.settings_panel.settings_panel_scatter
            )
            self.settings_toggle_boolean = True



    def calculate_mercator_coordinates(self, longitude: float, latitude: float) -> tuple[float, float]:

        """
        Given global longitude and latitude return screen x and y position
        """

        if longitude == "Unresolved" or longitude ==  "Local":  # No latitude or longitude information, use a default mercator position
 
            return self.center_x / 5 - 25, 100 * randint(2, 6)

        x, y = self.projection(longitude - 11, latitude)  # x,y in meters

        px = self.center_x + x * self.x_pixels_per_meter  # x in pixels
        py = self.center_y + y * self.y_pixels_per_meter  # y in pixels


        return px, py



    def close(self) -> None:

        """
        GUI_Manager closing cleanup function.
        """

        try:
            Clock.unschedule(self.update_gui)  
            Clock.unschedule(self.update_from_sniffer)  
            Clock.unschedule(self.ip_whois_lookup)  
            Clock.unschedule(self.db_insert_ip_whois_info)
        
            self.data_socket.close() # ZMQ publish/subscribe pattern
            self.server_socket.close()

        except:
            pass


        self.config_variables_dict["position_dictionary"]["main_settings_icon_pos"] = self.main_settings_icon.children[0].pos
        self.config_variables_dict["position_dictionary"]["graph_icon_pos"] = self.graph_icon.children[0].pos
        self.config_variables_dict["position_dictionary"]["table_icon_pos"] = self.table_icon.children[0].pos
        self.config_variables_dict["position_dictionary"]["malicious_icon_pos"] = self.malicious_icon.children[0].pos
        self.config_variables_dict["position_dictionary"]["connection_label_pos"] = self.settings_panel.connection_label_scatter.pos
        self.config_variables_dict["position_dictionary"]["settings_panel_pos"] = self.settings_panel.settings_panel_scatter.pos
   
        try:
            self.config_variables_dict["stored_connections"][self.current_connection_key]["mercator_position"] = self.my_computer.mercator_position
            self.config_variables_dict["stored_connections"][self.current_connection_key]["graph_position"] = self.my_computer.graph_position
        except:
            pass

        self.config_variables_dict["country_labels"] = self.country_labels
        self.config_variables_dict["city_labels"] = self.city_labels
        self.config_variables_dict["ip_labels"] = self.ip_labels
        self.config_variables_dict["computer_label"] = self.my_computer.mylabel_bool


        self.config_variables_dict["new_packet_color_opacity"] = int(self.settings_panel.new_packet_slider.value)

        self.config_variables_dict['inactive_ip_display_state'] =  self.settings_panel.inactive_ip_display_checkbox.active
        self.config_variables_dict['inactive_ip_display_time'] = self.settings_panel.ip_display_slider.value


       
        self.config_variables_dict["auto_connect"] = True if self.settings_panel.auto_connect_checkbox.active == True else False
     


        if self.kivy_application.operating_system == "Darwin" and getattr(sys, "frozen", False): #MacOS and packaged (not terminal executed)

             # Save configuations
            with open( os.path.join( self.kivy_application.darwin_network_visualizer_dir, "visualizer_config.json"), "w" ) as configuration_file:
                json.dump(self.config_variables_dict, configuration_file)

            # Save cached IP whois information
            with open(  os.path.join( self.kivy_application.darwin_network_visualizer_dir, "whois.json"), "w") as ip_whois_info_file:
                json.dump(self.ip_whois_info_dict.copy(), ip_whois_info_file)

        else:

            # Save configuations
            with open( os.path.join(self.resource_path, "configuration/visualizer_config.json"), "w" ) as configuration_file:
                json.dump(self.config_variables_dict, configuration_file)

            # Save cached IP whois information
            with open( os.path.join(self.resource_path, "assets/database/whois.json"), "w") as ip_whois_info_file:
                json.dump(self.ip_whois_info_dict.copy(), ip_whois_info_file)