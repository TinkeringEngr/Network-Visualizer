# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.


import datetime
from math import sin, cos, pi
import os
from pyperclip import copy
from random import random, randrange
import time


from kivy.core.audio import SoundLoader
from kivy.metrics import sp, dp
from kivy.graphics import Color, Line, RoundedRectangle, InstructionGroup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.dropdown import DropDown
#from kivy.uix.gridlayout import GridLayout
#from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout

from utilities.database_config import db
from utilities.utils import map_to_range, distance_between_points, remove_inline_quotes, IP_Icon_Scatter_Override






class IP_Widget(Widget):

    """
    GUI Widget for each IP address with member functions for various IP logic.
    """

    def __init__(self, **kwargs):

        """
        Construct GUI widget and associated state.
        """

        super().__init__()

        self.size_hint = (None, None)
        self.id = kwargs["ip"]  # ip address used as unique idenifier
        self.window_x = kwargs["window_x"]
        self.window_y = kwargs["window_y"]
        self.center_X = self.window_x / 2
        self.center_Y = self.window_y / 2
        self.latitude = kwargs["ip_latitude"]
        self.longitude = kwargs["ip_longitude"]
        self.longitude_x = kwargs["ip_longitude_x"]
        self.latitude_y = kwargs["ip_latitude_y"]
        self.ip_data = kwargs["ip_data"]
        self.resource_path = kwargs["resource_path"]
        self.gui_manager = kwargs["gui_manager"]

        self.country = kwargs["country"]  # issue with Nonetype
        self.country_label = "Unresolved" if self.country == None else self.country

        self.city = kwargs["city"]  # issue with Nonetype
        self.city_label = "Unresolved" if self.city == None else self.city

        self.whois_description = Label()

        self.whois_description.text = "Local" if self.country == "Local" else "Waiting on update.."

        self.size = ("50sp", "50sp")
        self.x_position = self.pos[0]
        self.y_position = self.pos[1]

        self.random_radius = randrange(sp(100), sp(200))
        self.pos = (random() * self.window_x, random() * self.window_y)
        self.old_pos = self.pos

        self.spring_constant_1 = 0.04
        self.spring_constant_2 = 0.08
        self.colision = 0
        self.delta_new_packet = 0
        self.new_pos = (0, 0)
        self.banlist_count = 0
        self.connection_opacity = 0
        self.new_packet_timestamp = time.time()
        self.time_stamp = datetime.datetime.fromtimestamp(self.new_packet_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        self.display_stamp = datetime.datetime.fromtimestamp(self.new_packet_timestamp).strftime("%H:%M:%S %d-%m-%Y ")

        self.malicious_sound = SoundLoader.load(os.path.join(self.resource_path, "assets/audio/alert.wav"))
        #self.sound.play()


        self.protocol_color = None
        self.banned_color_opacity = (1, 1, 1, 0.3)

        self.data_in_delta = 0
        self.data_out_delta = 0
        self.new_data = True
        self.show = True
        self.data = True
        self.menu_boolean = False
        #self.do_layout = False
        self.malicious_ip = False
        self.attach = True
        self.init_position = False


        self.mylabel_bool = True if self.gui_manager.ip_labels == True else False

        self.exempt = False

        

        #Populated after constructor
        self.menu_popup = None
        self.whois_popup = None
        self.whois_information = None
        self.city_widget = None
        self.country_widget = None

        # Graph view
        self.graph_position = self.pos
        self.initial_graph_position = self.graph_position
        #

        # Mercator view
        self.mercator_position = None
        self.initial_mercator_position = None
        self.resize = False
        self.packet_display = False
        #

        # GUI

        self.label = Label()
        self.label.text = self.id
        self.label.font_size = sp(15)
        self.label.font_blended = False
        self.label.font_hinting = "normal"
        self.label.pos = (dp(-18), dp(1))
        self.label.color = [1, 1, 1, 1]

        self.container = FloatLayout()
        self.container.pos = self.pos
        self.container.size_hint = (None, None)
        self.container.size = (dp(50), dp(50))

        self.icon_image = Image()
        self.icon_image.source = os.path.join(self.resource_path, "assets/images/UI/ip.png")
        self.icon_image.size_hint = (None, None)
        self.icon_image.size = (dp(10), dp(10))
        self.icon_image.pos = (dp(4), dp(4))

        self.display_menu_button = Button()
        self.display_menu_button.size_hint = (None, None)
        self.display_menu_button.pos_hint = (None, None)
        self.display_menu_button.pos = (dp(5), dp(5))
        self.display_menu_button.size = (dp(8), dp(8))
        self.display_menu_button.background_color = (0, 0, 1, 0)
        self.display_menu_button.on_press = self.toggle_menu

        self.icon_scatter_widget = IP_Icon_Scatter_Override()
        self.icon_scatter_widget.size_hint = (None, None)
        self.icon_scatter_widget.pos = self.pos
        self.icon_scatter_widget.size = (dp(18), dp(18))

        self.default_widget_halo_instruction_group = InstructionGroup()  
        self.default_widget_halo_instruction_group.add(Color(rgba = self.gui_manager.config_variables_dict["color_dictionary"]["Widget Halo Color"].copy()))
        self.default_widget_halo_instruction_group.add(  RoundedRectangle(
                                                                        size=self.icon_scatter_widget.size,
                                                                        pos=(0, 0),
                                                                        radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
                                                                        )  
                                                      )

        self.exempt_instruction_group = InstructionGroup()
        self.exempt_instruction_group.add(Color(rgba = self.gui_manager.config_variables_dict["color_dictionary"]["Exempt Color"].copy()))
        self.exempt_instruction_group.add(  RoundedRectangle(
                                                            size=self.icon_scatter_widget.size,
                                                            pos=(0, 0),
                                                            radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
                                                            )  
                                          )

       # self.icon_scatter_widget.canvas.add(self.default_widget_halo_instruction_group)

        self.ip_dropdown = DropDown()


        if self.malicious_ip:
            tag_button_text = "Untag"
            tag_button_color = (0,1,0,1)
            
        else:
            tag_button_text = "Tag"
            tag_button_color = (1,0,0,1)


        self.dropdown_tag_button = Button(
                                            text=tag_button_text,
                                            size_hint=(None, None),
                                            width=sp(125),
                                            height=sp(22),
                                            color=tag_button_color,
                                            background_color=(0, 0, 0, .8)
                                        )

        self.dropdown_tag_button.bind(on_release=self.tag)

        self.ip_dropdown.add_widget(self.dropdown_tag_button)


        btn = Button(
                    text="Copy IP Address",
                    size_hint=(None, None),
                    width=sp(125),
                    height=sp(22),
                    color=(1, 1, 1, 1),
                    background_color=(0, 0, 0, .8),
                    )
        btn.bind(on_release=self.copy_ip_address)
        self.ip_dropdown.add_widget(btn)


        btn = Button(
                    text="Copy Abuse Email",
                    size_hint=(None, None),
                    width=sp(125),
                    height=sp(22),
                    color=(1, 1, 1, 1),
                    background_color=(0, 0, 0, .8),
                    )

        btn.bind(on_release=self.copy_abuse_emails)
        self.ip_dropdown.add_widget(btn)

        btn = Button(
                    text="Copy Whois Info",
                    size_hint=(None, None),
                    width=sp(125),
                    height=sp(22),
                    color=(1, 1, 1, 1),
                    background_color=(0, 0, 0, .8),
                    )
        btn.bind(on_release=self.copy_whois_information)
        self.ip_dropdown.add_widget(btn)
        




        self.display_menu_button.add_widget(self.icon_image)
        self.icon_scatter_widget.add_widget(self.display_menu_button)

        if self.mylabel_bool == True:
            self.icon_scatter_widget.add_widget(self.label)

        self.container.add_widget(self.icon_scatter_widget)
        self.add_widget(self.container)

        self.icon_scatter_widget.pos = self.pos


        cursor = db.cursor()
        cursor.execute(
                        f"""INSERT INTO Live (ip, location_city, location_country,  longitude, latitude, description, total_packets, data_in, data_out, blocked) VALUES ( '{self.id}', '{self.city}', '{self.country}', '{self.longitude}', '{self.latitude}', "{self.whois_description}", '{self.gui_manager.sniffer_dictionary[self.id]['packet_count']}', '{self.gui_manager.sniffer_dictionary[self.id]['data_in']}', '{self.gui_manager.sniffer_dictionary[self.id]['data_out']}', '{self.malicious_ip}' )"""
                      )

        db.commit()

        table_row = self.generate_table_row()
        self.gui_manager.live_table_dictionary[self.id] = table_row
        self.gui_manager.live_table.add_widget(table_row)

        self.menu_popup = None #Populated by self.make_display_menu
        self.make_display_menu()

    

    def set_widget_halo_color(self) -> None:

        """
        Sets the halo around (canvas instruction) of the associated Widget
        """

        try:
            self.icon_scatter_widget.canvas.remove(self.exempt_instruction_group)
        except:
            pass

        self.default_instruction_group = InstructionGroup()  
        self.default_instruction_group.add(Color(rgba =  self.gui_manager.config_variables_dict["color_dictionary"]["Default Halo Color"].copy()))
        self.default_instruction_group.add(  RoundedRectangle(
                                                size=self.icon_scatter_widget.size,
                                                pos=(0, 0),
                                                radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
                                                )  
                                          )

        self.icon_scatter_widget.canvas.insert(-1, self.default_instruction_group)


        self.icon_scatter_widget.remove_widget(self.display_menu_button)
        self.icon_scatter_widget.add_widget(self.display_menu_button)



    def copy_ip_address(self, *args) -> None:
        
        """
        Copy the IP address to the clipboard
        """

        copy(str(self.id))
        self.ip_dropdown.dismiss()



    def generate_table_row(self) -> BoxLayout:

        """
        Construct a row for Table view
        """

        length_per_label = self.gui_manager.window_x / 7

        box_layout = BoxLayout(
                                orientation="horizontal",
                                size_hint=(None, None),
                                pos=(0, 0),
                                padding=1,
                                size=(self.gui_manager.window_x, dp(30)),
                              )

        ip_button = Button()
        ip_button.text = self.id
        ip_button.id = self.id
        ip_button.bind(on_press=self.live_table_menu)

        if self.malicious_ip == True:

            text_color = (1, 0, 0, 1)
            ip_button.background_color = (0.3, 0.3, 0.3, 1)
            ip_button.color = (1, 0, 0, 1)

        else:

            if self.gui_manager.table_count % 2 == 0:
                ip_button.background_color = (0, 1, 0, 0.8)
                ip_button.border = (0,0,0,0)
                ip_button.color = (1, 1, 1, 1)
                text_color = (1, 1, 1, 1)


            else:
                ip_button.background_color = (0, 1, 0, 0.3)
                ip_button.color = (1, 1, 1, 1)
                ip_button.border = (0,0,0,0)
                text_color = (1, 1, 1, 0.7)


            self.gui_manager.table_count += 1

        description_label = self.make_label(self.whois_description.text, length_per_label)
        description_label.color = text_color

        city_label = self.make_label(self.city_label, length_per_label)
        city_label.color = text_color

        country_label = self.make_label(self.country_label, length_per_label)
        country_label.color = text_color


        delta_time = time.time() - self.new_packet_timestamp
        opacity = map_to_range(delta_time, self.gui_manager.new_packet_color_opacity, 0, 0.6, 1)
            


        if opacity < 0.6:
            protocol_color = (1, 1, 1, 0.3)

        else:
            protocol_color  = self.gui_manager.config_variables_dict["color_dictionary"][self.ip_data["last_packet"] + " Protocol Color"].copy()
            protocol_color.append(opacity)

        
        self.protocol_color = protocol_color

        

        new_packet_date_time = self.make_label(self.display_stamp, length_per_label)
        new_packet_date_time.color = protocol_color

        packet_label = self.make_label(str(self.ip_data["packet_count"]), length_per_label)
        packet_label.color = protocol_color

        data_in_label = self.make_label(f"{self.ip_data['data_in']/1000000:.6f}", length_per_label)
        data_in_label.color = protocol_color

        data_out_label = self.make_label(f"{self.ip_data['data_out']/1000000:.6f}", length_per_label)
        data_out_label.color = protocol_color

        ip_button_container = BoxLayout(orientation="horizontal")
        ip_button_container.add_widget(Label(size_hint_x=0.1))
        ip_button_container.add_widget(ip_button)
        ip_button_container.add_widget(Label(size_hint_x=0.1))

        box_layout.add_widget(ip_button_container)
        box_layout.add_widget(description_label)
        box_layout.add_widget(city_label)
        box_layout.add_widget(country_label)
        box_layout.add_widget(new_packet_date_time)
        box_layout.add_widget(packet_label)
        box_layout.add_widget(data_in_label)
        box_layout.add_widget(data_out_label)

        return box_layout




    def generate_malicious_table_row(self) -> BoxLayout:

        """
        Construct a row for Malicious view
        """

        length_per_label = self.gui_manager.window_x / 6

        box_layout = BoxLayout(
                                orientation="horizontal",
                                size_hint=(None, None),
                                pos=(0, 0),
                                padding=1,
                                size=(self.gui_manager.window_x, dp(30)),
                              )

        ip_button = Button()
        ip_button.text = self.id
        ip_button.id = self.id
        ip_button.bind(on_press=self.live_table_menu)

        if self.gui_manager.malicious_table_count % 2 == 0:
            ip_button.background_color = (0.3, 0.3, 0.3, 1)
            ip_button.color = (1, 0, 0, 1)
            text_color = (1, 1, 1, 1)

        else:
            ip_button.background_color = (0.15, 0.15, 0.15, 1)
            ip_button.color = (1, 0, 0, 1)
            text_color = (1, 1, 1, 0.7)

        self.gui_manager.malicious_table_count += 1

        description_label = self.make_label(self.whois_description.text, length_per_label)
        description_label.color = text_color

        banlist_count_label = self.make_label(str(self.banlist_count), length_per_label)
        banlist_count_label.color = text_color

        country_label = self.make_label(self.country_label, length_per_label)
        country_label.color = text_color

        timestamp_label = self.make_label(self.malicious_displaystamp, length_per_label)
        timestamp_label.color = (1, 1, 1, 0.3)

        packet_label = self.make_label(str(self.ip_data["packet_count"]), length_per_label)
        packet_label.color = (1, 1, 1, 0.3)

        data_in_label = self.make_label(f"{self.ip_data['data_in']/1000000:.6f}", length_per_label)
        data_in_label.color = (1, 1, 1, 0.3)

        data_out_label = self.make_label(f"{self.ip_data['data_out']/1000000:.6f}", length_per_label)
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


    
    def tag(self, *args) -> None:

        """
        Add the IP to the malicious table view and add a sqlite entry
        """

        if self.malicious_ip == False:  # check to see if already malciious

            if self.gui_manager.config_variables_dict["play_audio_bool"] == True:
                self.malicious_sound.play()

            time_stamp = time.time()
            self.malicious_timestamp = datetime.datetime.fromtimestamp(time_stamp).strftime("%Y-%m-%d %H:%M:%S")
            self.malicious_displaystamp = datetime.datetime.fromtimestamp(time_stamp).strftime("%H:%M:%S %d-%m-%Y")


            self.icon_image.source = os.path.join(self.resource_path, "assets/images/UI/malicious.png")

            if self.id in self.gui_manager.malicious_ips_dictionary:
                self.banlist_count = self.gui_manager.malicious_ips_dictionary[self.id]

            if self.id not in self.gui_manager.malicious_ips_local_database:

                
                emails_string = "["            

                try:
                    for email in self.gui_manager.ip_whois_info_dict[self.id]["nets"][0]["emails"]:
                        emails_string += " " + email
                except:
                    emails_string = "None"

                emails_string += "]"

                whois_info = f"""{self.whois_information}"""

                cursor = db.cursor()

                current_connection_key = self.gui_manager.current_connection_key.replace(" ", "")
                malicious_ips_database_name = current_connection_key + "_malicious_ips"

                try:
                    ip_who_is = self.gui_manager.ip_whois_info_dict[self.id]

                    for item in ip_who_is['nets']: #bug where address has inline quote -- sql is fragile in python
                        ip_who_is['nets'][item]['address'] = remove_inline_quotes(ip_who_is['nets'][item]['address'])
                except:
                    ip_who_is = {}

                sql = f"""INSERT OR IGNORE INTO {malicious_ips_database_name} (ip, description, ban_lists, time_stamp, display_stamp, location_country,  packet_count, data_in, data_out, abuse_email, whois_info ) VALUES ( "{self.id}", "{self.whois_description.text}", {self.banlist_count}, "{self.malicious_timestamp}", "{self.malicious_displaystamp}", "{self.country}", {self.ip_data['packet_count']}, {self.ip_data['data_in']}, {self.ip_data['data_out']}, "{emails_string}", '{ip_who_is}'  ) """



                cursor.execute(sql)

                db.commit()

            for n, child_widget in enumerate(self.gui_manager.live_table_dictionary[self.id].children):
      
                if isinstance(child_widget, BoxLayout):

                    child_widget.children[1].background_color = (0.3, 0.3, 0.3, 1)
                    child_widget.children[1].color = (1, 0, 0, 1)

                elif n in (0, 1, 2, 3):
                    child_widget.color = (1, 1, 1, 0.3)

                else:
                    child_widget.color = (1, 0, 0, 1)


            if self.id not in self.gui_manager.malicious_table_dictionary:
                malicous_row = self.generate_malicious_table_row()
                self.gui_manager.malicious_table_dictionary[self.id] = malicous_row
                self.gui_manager.malicious_table.add_widget(malicous_row)


            self.tag_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/green.png")
            self.tag_button.background_down = os.path.join(self.resource_path, "assets/images/buttons/green_down.png")
            self.tag_button.text = "Untag"
            self.dropdown_tag_button.text = "Untag"
            self.dropdown_tag_button.color = (0,1,0,1)

            self.malicious_ip = True

  
        else: #self.malicious_ip == True

            self.icon_image.source = os.path.join(self.resource_path, "assets/images/UI/ip.png")

            malicious_row = self.gui_manager.malicious_table_dictionary[self.id]
            self.gui_manager.malicious_table.remove_widget(malicious_row)
            del self.gui_manager.malicious_table_dictionary[self.id]

            for child_widget in self.gui_manager.live_table_dictionary[self.id].children:

                if isinstance(child_widget, BoxLayout):

                    child_widget.children[1].background_color = (0, 1, 0, 1)
                    child_widget.children[1].color = (1, 1, 1, 1)

                else:
                    child_widget.color = (1, 1, 1, 1)

            if self.id in self.gui_manager.malicious_ips_local_database:
                del self.gui_manager.malicious_ips_local_database[self.id]

            cursor = db.cursor()
            
            current_connection_key = self.gui_manager.current_connection_key.replace(" ", "")

            malicious_ips_database_name = current_connection_key + "_malicious_ips"
            sql = f"""DELETE FROM {malicious_ips_database_name} WHERE ip="{self.id}" """
            cursor.execute(sql)
            db.commit()

            self.tag_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/red.png")
            self.tag_button.background_down = os.path.join(self.resource_path, "assets/images/buttons/red_down.png")
            self.tag_button.text = "Tag"
            self.dropdown_tag_button.text = "Tag"
            self.dropdown_tag_button.color = (1,0,0,1)

            self.malicious_ip = False
            

        try:
            self.ip_dropdown.dismiss()
        except:
            pass



    def remove_whois_popup(self, button: Button) -> None:

        """
        Remove whois popup for associated IP
        """

        self.gui_manager.persistent_widget_container.remove_widget(self.whois_popup)
        self.whois_popup = None
        self.display_whois_popup = False



    def copy_abuse_emails(self, calling_button:Button) -> None:
        
        """
        Copy whois abuse email to clipboard
        """

        try:
            abuse_email = self.gui_manager.ip_whois_info_dict[self.id]["nets"][0]["emails"]
            copy(str(abuse_email))

        except:
            copy("Error")

        self.ip_dropdown.dismiss()



    def copy_whois_information(self, calling_button:Button) -> None:
        
        """
        Copy whois information to clipboard
        """

        try:
            whois_information = self.gui_manager.ip_whois_info_dict[self.id]
            copy(str(whois_information))

        except:
            copy("Error")

        self.ip_dropdown.dismiss()



    def toggle_my_label(self) -> None:

        """
        Toggles My_Computer widget label on/off
        """

        if self.mylabel_bool == True:
            try:
                self.icon_scatter_widget.remove_widget(self.label)
            except:
                pass

            self.mylabel_bool = False

        else:
            try:
                self.icon_scatter_widget.add_widget(self.label)
            except:
                pass

            self.mylabel_bool = True



    def live_table_menu(self, button) -> None:

        """
        Kivy dropdown bug hack
        """

        self.ip_dropdown.open(button)



    def toggle_menu(self, *args) -> None:

        """
        Toggle menu when user clicks on IP Widget.
        """

        if self.menu_boolean == False:
            self.menu_boolean = True

            self.gui_manager.persistent_widget_container.add_widget(self.menu_popup)
            self.gui_manager.misc_update_dictionary["ip"][f"{self.id}"] = self

        elif self.menu_boolean == True:
            self.menu_boolean = False

            self.gui_manager.persistent_widget_container.remove_widget(self.menu_popup)
            del self.gui_manager.misc_update_dictionary["ip"][f"{self.id}"]



    # def make_exempt(self) -> None:

    #     """
    #     Toggle exempt status for Widget to be affected by graph display.
    #     """

    #     if self.exempt == True:
    #         self.exempt_button.text = "Not Exempt"
    #         #self.small_exempt_button.text = "NE"
    #         self.exempt = False

    #     else:
    #         self.exempt_button.text = "Exempt"
    #         #self.small_exempt_button.text = "E"
    #         self.exempt = True



    def set_widget_halo_color(self) -> None:

        """
        Sets the halo around (canvas instruction) of the associated Widget
        """

        try:
            self.icon_scatter_widget.canvas.remove(self.default_widget_halo_instruction_group)
        except:
            pass


        self.default_widget_halo_instruction_group = InstructionGroup()  
        self.default_widget_halo_instruction_group.add(Color(rgba =  self.gui_manager.config_variables_dict["color_dictionary"]["Widget Halo Color"].copy()))
        self.default_widget_halo_instruction_group.add(  RoundedRectangle(
                                                                        size=self.icon_scatter_widget.size,
                                                                        pos=(0, 0),
                                                                        radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
                                                                        )  
                                                      )

        self.icon_scatter_widget.canvas.insert(-1, self.default_widget_halo_instruction_group)


        self.icon_scatter_widget.remove_widget(self.display_menu_button)
        self.icon_scatter_widget.add_widget(self.display_menu_button)




    def toggle_exempt(self) -> None:

        """
        Toggle exempt status for Widget to be affected/unaffected by graph display.
        """

     
        if self.exempt == True:

            self.exempt_button.text = "Not-Exempt"

            self.exempt_button.color = (1,1,1,1)
            self.exempt_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/kivy-teal-4.png")
            self.exempt_button.background_down = os.path.join(self.resource_path,  "assets/images/buttons/kivy-teal-4.png")

            try:
                self.icon_scatter_widget.canvas.remove(self.exempt_instruction_group)
            except:
                pass

            self.default_widget_halo_instruction_group = InstructionGroup()  
            self.default_widget_halo_instruction_group.add(Color(rgba =  self.gui_manager.config_variables_dict["color_dictionary"]["Widget Halo Color"].copy()))
            self.default_widget_halo_instruction_group.add(  RoundedRectangle(
                                                                            size=self.icon_scatter_widget.size,
                                                                            pos=(0, 0),
                                                                            radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
                                                                            )  
                                                          )

            self.icon_scatter_widget.canvas.insert(-1, self.default_widget_halo_instruction_group)


            self.icon_scatter_widget.remove_widget(self.display_menu_button)
            self.icon_scatter_widget.add_widget(self.display_menu_button)

            self.exempt = False


        else:

            exempt_color = self.gui_manager.config_variables_dict["color_dictionary"]["Exempt Color"].copy()
            
            self.exempt_button.text = "Exempt"
            self.exempt_button.color = exempt_color
            self.excempt_pos = self.icon_scatter_widget.pos
            self.exempt_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/black.png")
            self.exempt_button.background_down = os.path.join(self.resource_path, "assets/images/buttons/black.png")

            try:
                    self.icon_scatter_widget.canvas.remove(self.default_widget_halo_instruction_group)
            except:
                    pass

            self.exempt_instruction_group = InstructionGroup()   
            exempt_color[3] = 0.5
            self.exempt_instruction_group.add(Color(rgba= exempt_color))
            self.exempt_instruction_group.add(  RoundedRectangle(
                                                                size=self.icon_scatter_widget.size,
                                                                pos=(0, 0),
                                                                radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
                                                                )  
                                              )

            self.icon_scatter_widget.canvas.insert(-1, self.exempt_instruction_group)
            self.icon_scatter_widget.remove_widget(self.display_menu_button)
            self.icon_scatter_widget.add_widget(self.display_menu_button)
            
            self.exempt = True



    def make_display_menu(self) -> Scatter:

        """
        Create popup menu when user clicks on IP widget.
        """

        packet_count = self.ip_data["packet_count"]
        data_in = self.ip_data["data_in"]
        data_out = self.ip_data["data_out"]

        size = (dp(155), dp(180))

        self.menu_popup = Scatter()
        self.menu_popup.size_hint = (None, None)
        self.menu_popup.size = size
        self.menu_popup.pos = ( self.icon_scatter_widget.pos[0] + 25, self.icon_scatter_widget.pos[1] + 25)
        self.menu_popup.id = self.id + "p"

        with self.menu_popup.canvas.before:
            Color(1, 1, 1, 0.1)
            RoundedRectangle(
                size=self.menu_popup.size,
                pos=(0, 0),
                radius=[(20, 20), (20, 20), (20, 20), (20, 20)],
            )

        if self.menu_popup.pos[0] + sp(350) > self.window_x:
            self.menu_popup.pos = (self.window_x - sp(375), self.menu_popup.pos[1])

        if self.menu_popup.pos[1] + sp(155) > self.window_y:
            self.menu_popup.pos = (self.menu_popup.pos[0], self.window_y - sp(150))

        grid_layout = BoxLayout(orientation="vertical")
        grid_layout.size_hint = (None, None)
        grid_layout.size = (size[0], size[1]-dp(10))
        grid_layout.pos = (sp(3), sp(5))

        ip_label = Label()
        ip_label.text = self.id

        self.packet_label = Label()
        self.packet_label.text = "Packet Count: " + str(packet_count)
        self.packet_label.markup = True
        self.packet_label.font_size = sp(12)

        self.data_IN_label = Label()
        self.data_IN_label.text = f"Data IN (MB): {data_in/1000000.0:.6f}"
        self.data_IN_label.markup = True
        self.data_IN_label.font_size = sp(12)

        self.data_OUT_label = Label()
        self.data_OUT_label.text = f"Data OUT (MB): {data_out/1000000.0:.6f}"
        self.data_OUT_label.markup = True
        self.data_OUT_label.font_size = sp(12)

        self.exempt_button = Button()
        self.exempt_button.on_press = self.toggle_exempt
        self.exempt_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/kivy-teal-4.png")
        self.exempt_button.background_down = os.path.join(self.resource_path, "assets/images/buttons/teal_down.png")
        self.exempt_button.border = (0, 0, 0, 0)
        self.exempt_button.font_size = sp(12)


        self.exempt_button.text = "Exempt" if self.exempt else "Not Exempt"

        copy_abuse_email_button = Button()
        copy_abuse_email_button.text = "Copy Abuse Email"
        copy_abuse_email_button.background_color = (.6, .6, .6, 0.8)
        copy_abuse_email_button.bind(on_press=self.copy_abuse_emails)
        copy_abuse_email_button.font_size = sp(12)
        copy_abuse_email_button.border = (0, 0, 0, 0)

        copy_ip_address_button = Button()
        copy_ip_address_button.text = "Copy IP Address"
        copy_ip_address_button.background_color = (.4, .4, .4, 0.8)
        copy_ip_address_button.bind(on_press=self.copy_ip_address)
        copy_ip_address_button.font_size = sp(12)
        copy_ip_address_button.border = (0, 0, 0, 0)

        copy_whois_info_button = Button()
        copy_whois_info_button.text = "Copy Whois Info"
        copy_whois_info_button.background_color = (.9, .9, .9, 0.8)
        copy_whois_info_button.bind(on_press=self.copy_whois_information)
        copy_whois_info_button.font_size = sp(12)
        copy_whois_info_button.border = (0, 0, 0, 0)

        self.tag_button = Button()
        self.tag_button.text = "Tag"
        self.tag_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/red.png")
        self.tag_button.background_down = os.path.join(self.resource_path, "assets/images/buttons/red_down.png")
        self.tag_button.bind(on_press=self.tag)
        self.tag_button.font_size = sp(12)
        self.tag_button.border = (0, 0, 0, 0)

        dismiss_button = Button()
        dismiss_button.text = "Dismiss"
        dismiss_button.background_color = [1, 1, 1, 0.1]
        dismiss_button.on_press = self.toggle_menu
        dismiss_button.font_size = sp(12)
        dismiss_button.border = (0, 0, 0, 0)

        toggle_label = Button()
        toggle_label.on_press = self.toggle_my_label
        toggle_label.font_size = sp(15)
        toggle_label.text = self.id
        toggle_label.background_color = (0.3, 0.3, 0.3, 0.9)
        toggle_label.background_down = os.path.join(self.resource_path, "assets/images/buttons/black.png")

        label_container = BoxLayout(orientation="horizontal", size_hint_x=1, size_hint_y=1)

        # self.collect_stream_data_button = Button()
        # self.collect_stream_data_button.text = "Collect Stream Data"
        # self.collect_stream_data_button.bind(on_press=self.collect_stream_data)
        # self.collect_stream_data_button.font_size = sp(12)
        # self.collect_stream_data_button.border = (0, 0, 0, 0)


        # self.display_stream_data_button = Button()
        # self.display_stream_data_button.text = "Display Stream Data"
        # self.display_stream_data_button.bind(on_press=self.display_stream_data)
        # self.display_stream_data_button.font_size = sp(12)
        # self.display_stream_data_button.border = (0, 0, 0, 0)

        label_container.add_widget(Label(size_hint_x=0.25))
        label_container.add_widget(toggle_label)
        label_container.add_widget(Label(size_hint_x=0.25))
        grid_layout.add_widget(label_container)
        grid_layout.add_widget(Label(size_hint_y=1))

        grid_layout.add_widget(self.whois_description)
        grid_layout.add_widget(Label(size_hint_y=1))
        grid_layout.add_widget(self.packet_label)
        grid_layout.add_widget(Label(size_hint_y=0.5))
        grid_layout.add_widget(self.data_IN_label)
        grid_layout.add_widget(Label(size_hint_y=0.25))
        grid_layout.add_widget(self.data_OUT_label)
        grid_layout.add_widget(Label(size_hint_y=1))

        copy_ip_address_container = BoxLayout(orientation="horizontal", size_hint_x=1, size_hint_y=1.1)
        copy_ip_address_container.add_widget(Label(size_hint_x=0.2))
        copy_ip_address_container.add_widget(copy_ip_address_button)
        copy_ip_address_container.add_widget(Label(size_hint_x=0.2))
        grid_layout.add_widget(copy_ip_address_container)

        grid_layout.add_widget(Label(size_hint_y=0.2))

        copy_abuse_email_button_container = BoxLayout(orientation="horizontal", size_hint_x=1, size_hint_y=1.1)
        copy_abuse_email_button_container.add_widget(Label(size_hint_x=0.2))
        copy_abuse_email_button_container.add_widget(copy_abuse_email_button)
        copy_abuse_email_button_container.add_widget(Label(size_hint_x=0.2))
        grid_layout.add_widget(copy_abuse_email_button_container)

        grid_layout.add_widget(Label(size_hint_y=0.2))

        copy_whois_info_button_container = BoxLayout(orientation="horizontal", size_hint_x=1, size_hint_y=1.1)
        copy_whois_info_button_container.add_widget(Label(size_hint_x=0.2))
        copy_whois_info_button_container.add_widget(copy_whois_info_button)
        copy_whois_info_button_container.add_widget(Label(size_hint_x=0.2))
        grid_layout.add_widget(copy_whois_info_button_container)

        grid_layout.add_widget(Label(size_hint_y=0.2))

        excempt_button_container = BoxLayout(orientation="horizontal", size_hint_x=1, size_hint_y=1)
        excempt_button_container.add_widget(Label(size_hint_x=0.2))
        excempt_button_container.add_widget(self.exempt_button)
        excempt_button_container.add_widget(Label(size_hint_x=0.2))
        grid_layout.add_widget(excempt_button_container)

        grid_layout.add_widget(Label(size_hint_y=0.2))

        tag_container = BoxLayout(orientation="horizontal", size_hint_x=1, size_hint_y=1)
        tag_container.add_widget(Label(size_hint_x=0.2))
        tag_container.add_widget(self.tag_button)
        tag_container.add_widget(Label(size_hint_x=0.2))
        grid_layout.add_widget(tag_container)

        grid_layout.add_widget(Label(size_hint_y=0.3))

        dismiss_container = BoxLayout(orientation="horizontal", size_hint_x=1, size_hint_y=1)
        dismiss_container.add_widget(Label(size_hint_x=1))
        dismiss_container.add_widget(dismiss_button)
        dismiss_container.add_widget(Label(size_hint_x=1))
        grid_layout.add_widget(dismiss_container)

        grid_layout.add_widget(Label(size_hint_y=0.1))

        # grid_layout.add_widget(self.collect_stream_data_button)
        # grid_layout.add_widget(self.display_stream_data_button)

        self.menu_popup.add_widget(grid_layout)



    # def collect_stream_data(self, *button:Button) -> None:

    #     """
    #     Trigger Sniffer to begin collecting IP stream data
    #     """

    #     server_msg = bytes(f'collect {self.id}'.encode('utf-8'))
    #     self.gui_manager.server_socket.send(server_msg)

    #     server_response = self.gui_manager.server_socket.recv()
    #     self.gui_manager.ip_data_streams[self.id] = True



    # def display_stream_data(self, *button: Button) -> None:

    #     """
    #     Display IP stream data
    #     """


    #     size = (dp(400), dp(400))
    #     scroll_view_size =  (dp(360), dp(360))

    #     self.data_flow_scatter = Scatter()
    #     self.data_flow_scatter.size_hint = (None, None)
    #     self.data_flow_scatter.size = size
    #     self.data_flow_scatter.pos = (0, 0)

    #     with self.data_flow_scatter.canvas:
    #         Color(.4, .4, .4,.2)
    #         RoundedRectangle(
    #             size=self.data_flow_scatter.size,
    #             pos=self.data_flow_scatter.pos,
    #             radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
    #         )

    #     scroll_view = ScrollView( size_hint = (1, 1), size = scroll_view_size, pos = (dp(20), dp(20)) )
   
    #     self.data_stream_text = Label(text =  self.ip_data["stream_data"], size_hint =  (None, None), size =  (scroll_view_size[0], 1000))

    #     self.data_stream_text.bind(text = self.adjust_label_dimension)

    #     scroll_view.add_widget(self.data_stream_text)
        

    #     self.data_flow_scatter.add_widget(scroll_view)

    #     self.gui_manager.persistent_widget_container.add_widget(self.data_flow_scatter)




    # def adjust_label_dimension(self, label: Label, text) -> None:

    #     """
    #     Adjust dataflow dimension
    #     """

    #     label.size[1] = label.texture_size[1]
    #     print("Triggered adjust label dimension")



    def set_position(self) -> tuple[float, float]:

        """
        Calculate x and y screen position for IP widget.
        """

        if self.gui_manager.current == "graph":

            x = self.gui_manager.country_dictionary[self.country][1][self.city][0].pos[
                0
            ] + dp(150) * sin(2 * pi * random())
            y = self.gui_manager.country_dictionary[self.country][1][self.city][0].pos[
                1
            ] + dp(150) * cos(2 * pi * random())

            self.pos = [x, y]
            self.icon_scatter_widget.pos = self.pos
            self.menu_popup.pos = self.pos



    def set_mercator_layout(self) -> None:

        """
        Called when screenmanager view is changed to mercator view.
        """

        self.graph_position = self.icon_scatter_widget.pos
        self.pos = self.mercator_position
        self.icon_scatter_widget.pos = self.mercator_position



    def set_graph_layout(self) -> None:

        """
        Called when screenmanager view is changed to graph view.
        """

        self.mercator_position = self.icon_scatter_widget.pos
        self.pos = self.graph_position
        self.icon_scatter_widget.pos = self.graph_position



    def update(self, **kwargs) -> None:

        """
        Update GUI widget. Called every cycle.
        """


        city_position = self.city_widget.icon_scatter_widget.pos

        protocol_color = kwargs["protocol_color"]

        if self.attach == True:  # check to see if we are attached to city

            distance_to_city, x_distance, y_distance = distance_between_points(
                city_position, self.pos
            )

            if distance_to_city > 200:  # if more than 200 pixels away from city

                self.pos[0] += x_distance * self.spring_constant_1
                self.pos[1] += y_distance * self.spring_constant_1
                self.icon_scatter_widget.pos = self.pos

            else:
                self.attach = False

        # map data from bytes to pixel length (green and blue lines)
        # range is mapped from 0-largest_data_from/to_IP --> 0-50 pixels (compares data relatively)
        data_in = map_to_range(self.ip_data["data_in"], 0, self.gui_manager.ip_largest_data_in, 0, 30)
        data_out = map_to_range(self.ip_data["data_out"], 0, self.gui_manager.ip_largest_data_out, 0, 30)

        # draw ip widget lines
        self.canvas.before.clear()
        with self.canvas.before:

            delta_time = time.time() - self.new_packet_timestamp
            opacity = map_to_range(delta_time, self.gui_manager.new_packet_color_opacity, 0, 0, 1)
            

            if self.malicious_ip == True:
                Color(1, 0, 0, 1)
            
            else:

                if opacity < 0:
                    Color(rgba = self.gui_manager.config_variables_dict["color_dictionary"]["Widget Halo Color"].copy())

                else:
                    protocol_color.append(opacity)
                    Color(rgba=protocol_color)


            Line(
                points=(
                    city_position[0] + dp(8),
                    city_position[1] + dp(8),
                    self.icon_scatter_widget.pos[0] + dp(8),
                    self.icon_scatter_widget.pos[1] + dp(8),
                ),
                width=1,
                )

            RoundedRectangle(
                            size=self.icon_scatter_widget.size,
                            pos=self.icon_scatter_widget.pos,
                            radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
                            )

            x, y = self.icon_scatter_widget.pos

            Color(rgba=self.gui_manager.config_variables_dict["color_dictionary"]["Data IN Color"])
            Line(points=[x, y, x + dp(data_in), y], width=1)

            Color(rgba=self.gui_manager.config_variables_dict["color_dictionary"]["Data OUT Color"])
            Line(points=[x, y - sp(5), x + dp(data_out), y - sp(5)], width=1)

            if self.menu_boolean and self.mylabel_bool == False:

                Color(1, 1, 1, 0.3)
                Line(
                    points=[
                            self.icon_scatter_widget.pos[0] + sp(10),
                            self.icon_scatter_widget.pos[1] + sp(10),
                            self.menu_popup.pos[0] + sp(77),
                            self.menu_popup.pos[1],
                           ],
                    width=sp(1)
                    )