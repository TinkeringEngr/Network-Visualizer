# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.


import atexit
from cgitb import reset
import copy
from functools import partial
import ipaddress
from multiprocessing import Array, Process
from network_sniffer import Sniffer
import os
import pyperclip
import pynng
import shutil
import sys
import time
from typing import Dict, Tuple
import webbrowser
import zmq 
import zmq.auth

from kivy.properties import ObservableReferenceList
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import sp, dp
from kivy.utils import get_color_from_hex
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider

from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle, InstructionGroup

from utilities.database_config import db
from utilities.colorwheel import ColorWheel, AutonomousColorWheel
from utilities.iconfonts import register


class Settings_Panel(AnchorLayout):

    """
    Network Visualizer settings and configuration panel.
    """

    def __init__(self, **kwargs) -> None:

        """
        Settings_Panel constructor
        """

        super().__init__()

        self.resource_path = kwargs["resource_path"]
        self.accordion = Accordion(min_space=dp(42))

        register(
                "default_font",
                os.path.join(self.resource_path, "assets/fonts/fontawesome-webfont"),
                os.path.join(self.resource_path, "assets/fonts/font-awesome.fontd"),
                )

        self.accordion.orientation = "vertical"

        size = (dp(500), dp(600))
        self.accordion.size = size
        self.size_hint_x = 1
        self.size_hint_y = 1
        self.sniffer_state = True

        self.settings_panel_scatter = Scatter()
        self.settings_panel_scatter.size_hint = (None, None)
        self.settings_panel_scatter.size = size

        self.settings_panel_scatter.add_widget(self.accordion)

        self.color_picker_popup_open = False
        self.sniffer_connect_popup = False

        self.gui_manager = None  # placeholder until gui_manager is assigned. (BUG: when gui_manager is passed in kwargs...)

        self.error_label = Label()

        self.auto_connect_checkbox = CheckBox()
        self.auto_connect_checkbox.id = "auto_connect"
        self.auto_connect_checkbox.group = "auto_connect"
        #self.auto_connect_checkbox.bind(active=self.on_sniffer_checkbox_active)
        self.auto_connect_checkbox.background_radio_normal = os.path.join( self.resource_path, "assets/images/UI/white_circle.png" )
        self.auto_connect_checkbox.size_hint_x = 0.15

        self.play_audio_checkbox = CheckBox()
        self.play_audio_checkbox.id = "play_audio"
        self.play_audio_checkbox.group = "play_audio"
        self.play_audio_checkbox.bind(active=self.malicious_sound_toggle)
        self.play_audio_checkbox.background_radio_normal = os.path.join( self.resource_path, "assets/images/UI/white_circle.png" )
        self.play_audio_checkbox.size_hint_x = 0.15

        self.largest_button_texture_size = 0



    def new_packet_slider_change(self, slider:Slider, value:float) -> None:

        """
        Callable when new_packet_slider is modified
        """

        self.new_packet_slider_label.text = f"New Packet Color Opacity (seconds): {int(value)}"
        self.gui_manager.new_packet_color_opacity = int(value)


    def malicious_sound_toggle(self, checkbox: CheckBox, value:bool) -> None:

        """ 
        Callable to toggle on/off sound when malicious IP is activated.
        """

        if value == False:
            self.gui_manager.config_variables_dict["play_audio_bool"] = False

        else:
             self.gui_manager.config_variables_dict["play_audio_bool"] = True



    def inactive_widget_display_toggle(self, checkbox: CheckBox, value:bool) -> None:

        """
        Callable that sets all inactive widgets to active when inactive_ip_display_checkbox is toggled. 
        """
    
        if value == False:

            inactive_cities_copy = copy.deepcopy(self.gui_manager.inactive_cities)
            inactive_ips_copy = copy.deepcopy(self.gui_manager.inactive_ips)

            for country in inactive_ips_copy.keys():

                for city in inactive_ips_copy[country].keys():

                    for ip in inactive_ips_copy[country][city]:

                        self.gui_manager.inactive_ips[country][city].pop(ip)
                        self.gui_manager.active_ips[country][city][ip] = True


            for country in inactive_cities_copy.keys():
            
                for city in inactive_cities_copy[country]:

                    self.gui_manager.active_cities[country][city] = True
                    self.gui_manager.inactive_cities[country].pop(city)

        else:

            inactive_ip_display_threshold = time.time() - self.ip_display_slider.value 

            for country in self.gui_manager.country_dictionary:

                for city_index, city in enumerate(self.gui_manager.country_dictionary[country][1]):

                    for ip_index, ip_widget in enumerate(self.gui_manager.country_dictionary[country][1][city]):

                        if ip_index == 0: # Skip City Widget
                            continue
                  
                        if (ip_widget.new_packet_timestamp < inactive_ip_display_threshold):

                            self.gui_manager.inactive_ips[country][city][ip_widget.id] = True
                            self.gui_manager.active_ips[country][city].pop(ip_widget.id)


                    if ( len(self.gui_manager.active_ips[country][city].keys()) == 0 ) and ( city in self.gui_manager.active_cities[country] ):

                        self.gui_manager.active_cities[country].pop(city)
                        self.gui_manager.inactive_cities[country][city] = True



    def ip_display_slider_change(self, slider:Slider, value:float) -> None:

        """
        Set threshold for removal of IP Widgets from GUI
        """
    
        self.ip_display_label.text = f"Remove Inactive IP's (seconds): {int(value)}"


        if self.inactive_ip_display_checkbox.active == True:

            inactive_ip_display_threshold = time.time() - value 

            for country in self.gui_manager.country_dictionary:

                for city in self.gui_manager.country_dictionary[country][1]:

                    inactive_ips_copy = copy.deepcopy(self.gui_manager.inactive_ips[country][city])

                    for ip in inactive_ips_copy:
                        
                        ip_widget = self.gui_manager.ip_dictionary[ip]
                        city = ip_widget.city
                        country = ip_widget.country
                    
                        if (ip_widget.new_packet_timestamp < inactive_ip_display_threshold) and (ip in self.gui_manager.active_ips[country][city] ):

                            self.gui_manager.inactive_ips[country][city][ip] = True
                            self.gui_manager.active_ips[country][city].pop(ip)

                        else:

                            self.gui_manager.active_ips[country][city][ip] = True
                            self.gui_manager.inactive_ips[country][city].pop(ip)
                

                inactive_cities_copy = copy.deepcopy(self.gui_manager.inactive_cities[country])
            
                for city in inactive_cities_copy:


                        if ( len(self.gui_manager.active_ips[country][city].keys()) > 0 ):

                            self.gui_manager.active_cities[country][city] = True
                            self.gui_manager.inactive_cities[country].pop(city)

     
    
    def increase_new_packet_slider_range(self, *args) -> None:

        """
        Callable to increase the upper bound for new packet opacity slider 
        """

        self.new_packet_slider.max += 100



    def increase_ip_display_slider_range(self, *args) -> None:

        """
        Callable to increase the upper bound for inactive IP display
        """

        self.ip_display_slider.max += 500



    def create_display_settings(self, *args) -> GridLayout:

        """
        Construct Settings Menu
        """


        grid_layout = GridLayout(cols=1, size=(sp(325), sp(125)))

        bottom_stack_container = BoxLayout(orientation="vertical")
        label_container = BoxLayout(orientation="horizontal", spacing=5)

        self.new_packet_slider  = Slider()
        self.new_packet_slider.min = 1
        self.new_packet_slider.max = 100
        self.new_packet_slider.value = self.gui_manager.new_packet_color_opacity
        self.new_packet_slider.orientation = "horizontal"
        self.new_packet_slider.bind(value=self.new_packet_slider_change)
        

        increase_new_packet_slider_range = Button(text="", size_hint_y=1)
        increase_new_packet_slider_range.on_press = self.increase_new_packet_slider_range
        increase_new_packet_slider_range.font_size = sp(15)
        increase_new_packet_slider_range.background_down = ""
        increase_new_packet_slider_range.size_hint_x = 0.027
        increase_new_packet_slider_range.size_hint_y = 1
        increase_new_packet_slider_range.border = (0,0,0,0)
        increase_new_packet_slider_range.background_normal =  os.path.join( self.resource_path, "assets/images/UI/plus.png" )

        self.new_packet_slider_label = Label()
        self.new_packet_slider_label.text = f"New Packet Color Opacity (seconds): {int(self.new_packet_slider.value)}"
        
    
        self.ip_display_slider  = Slider()
        self.ip_display_slider.min = 1
        self.ip_display_slider.max = 100
        self.ip_display_slider.value = self.gui_manager.config_variables_dict['inactive_ip_display_time']
        self.ip_display_slider.orientation = "horizontal"
        self.ip_display_slider.bind(value=self.ip_display_slider_change)

        

        self.inactive_ip_display_checkbox = CheckBox()
        self.inactive_ip_display_checkbox.size_hint_x = 0.5
        self.inactive_ip_display_checkbox.group = "inactive_display"
        self.inactive_ip_display_checkbox.bind(active=self.inactive_widget_display_toggle)
        self.inactive_ip_display_checkbox.background_radio_normal = os.path.join( self.resource_path, "assets/images/UI/white_circle.png" )
        self.inactive_ip_display_checkbox.active = self.gui_manager.config_variables_dict['inactive_ip_display_state'] 

        self.inactive_ip_display_checkbox_placeholder = CheckBox()
        self.inactive_ip_display_checkbox_placeholder.group = "inactive_display"

        increase_ip_display_slider_range = Button(text="", size_hint_y=1)
        increase_ip_display_slider_range.on_press = self.increase_ip_display_slider_range
        increase_ip_display_slider_range.font_size = sp(15)
        increase_ip_display_slider_range.background_down = ""
        increase_ip_display_slider_range.size_hint_x = 0.027
        increase_ip_display_slider_range.size_hint_y = 1.075
        increase_ip_display_slider_range.border = (0,0,0,0)
        increase_ip_display_slider_range.background_normal =  os.path.join( self.resource_path, "assets/images/UI/plus.png" )

        self.ip_display_label = Label()

        self.ip_display_label.text = f"Remove Inactive IP's (seconds): {int(self.ip_display_slider.value)}"

        self.play_audio_label = Label(text="Play warning audio on malicious IP")



        #Layout widgets
        top_container = BoxLayout(orientation="horizontal", size_hint_y=0.5)
        

        play_audio_container = BoxLayout(orientation="horizontal")
        play_audio_container.add_widget(Label(size_hint_x=1))
        play_audio_container.add_widget(self.play_audio_checkbox)
        play_audio_container.add_widget(Label(size_hint_x=0.3))
        play_audio_container.add_widget(self.play_audio_label)
        play_audio_container.add_widget(Label(size_hint_x=1))
        
        top_container.add_widget(play_audio_container)
        

        middle_container = BoxLayout(orientation="vertical")

        ip_display_label_container = BoxLayout(orientation="horizontal", spacing=5)
        ip_display_label_container.add_widget(Label(size_hint_x=0.4))
        ip_display_label_container.add_widget(self.inactive_ip_display_checkbox)
        #ip_display_label_container.add_widget(Label(size_hint_x=0.000005))
       #ip_display_label_container.add_widget(Label(size_hint_x=1))
        ip_display_label_container.add_widget(self.ip_display_label)
        ip_display_label_container.add_widget(Label())

        middle_container.add_widget(Label(size_hint_y=1))
        middle_container.add_widget(ip_display_label_container)
        middle_container.add_widget(Label(size_hint_y=0.5))

        display_slider_container = BoxLayout(orientation='horizontal', size_hint_y=0.38)
        display_slider_container.add_widget(self.ip_display_slider)
        display_slider_container.add_widget(increase_ip_display_slider_range)
        display_slider_container.add_widget(Label(size_hint_x=0.05))
        
        middle_container.add_widget(display_slider_container)
        middle_container.add_widget(Label(size_hint_y=1))


        bottom_stack_container.add_widget(Label(size_hint_y=0.5))
        bottom_stack_container.add_widget(label_container)
        bottom_stack_container.add_widget(Label(size_hint_y=0.5))
        bottom_stack_container.add_widget(self.new_packet_slider_label)
        bottom_stack_container.add_widget(Label(size_hint_y=0.2))

        slider_container = BoxLayout(orientation='horizontal', size_hint_y=0.5)
        slider_container.add_widget(self.new_packet_slider)
        slider_container.add_widget(increase_new_packet_slider_range)
        slider_container.add_widget(Label(size_hint_x=0.05))
        

        bottom_stack_container.add_widget(slider_container)
        bottom_stack_container.add_widget(Label(size_hint_y=1))

        grid_layout.add_widget(Label(size_hint_y=0.5))
        grid_layout.add_widget(middle_container)
        grid_layout.add_widget(bottom_stack_container)
        grid_layout.add_widget(Label(size_hint_y=0.25))
        grid_layout.add_widget(top_container)
        grid_layout.add_widget(Label(size_hint_y=0.5))
        

        return grid_layout



    def create_colors_panel(self):

        """
        Construct Colors panel
        """

        grid_layout = GridLayout(cols=1, size=(sp(325), sp(125)))

        bottom_stack_container = BoxLayout(orientation="vertical")
        button_container = BoxLayout(orientation="horizontal", spacing=10)
        label_container = BoxLayout(orientation="horizontal", spacing=5)

        self.features_dropdown = DropDown()

        supported_features = [
                                "Data IN",
                                "Data OUT",
                                "Summary Data",
                                "Exempt",
                                "Widget Halo",
                                "TCP Protocol",
                                "UDP Protocol",
                                "ICMP Protocol",
                                "OTHER Protocol",
                             ]  # extend to support more color features

        self.colored_buttons = {}
        for feature in supported_features:

            btn = Button(
                        text=feature,
                        size_hint=(None, None),
                        width=sp(125),
                        height=44,
                        background_color=(0, 0, 0, 1),
                        )

            btn.id = feature
            btn.bind(on_release=self.features_dropdown_color_text_change)
            btn.color = self.gui_manager.config_variables_dict["color_dictionary"][f"{feature} Color"]
            self.features_dropdown.add_widget(btn)
            self.colored_buttons[feature] = btn

        self.selected_protocol_button = Button(
                                                text="Select Feature",
                                                size_hint=(None, None),
                                                width=sp(125),
                                                height=sp(25),
                                                background_color=[0.5, 0.5, 0.5, 0.8]
                                                )

        self.selected_protocol_button.bind(on_press=self.open_features_dropdown)

        self.features_dropdown.bind( on_select=lambda instance, x: setattr( self.selected_protocol_button, "text", x ) )

        self.hex_input = TextInput()

        self.hex_input.bind(text=self.validate_color_textinput)
        self.hex_input.size_hint_y = None
        self.hex_input.size_hint_x = None
        self.hex_input.size = (sp(90), sp(27))

        self.clr_picker = AutonomousColorWheel()
        self.clr_picker.size_hint = (0.5, 1)
        self.clr_picker.bind(color=self.on_color_selection)
        self.hex_input.text = ""

        self.apply_color_button = Button(
                                        text="Apply Color",
                                        on_press=self.apply_color,
                                        size_hint=(None, None),
                                        width=sp(100),
                                        height=sp(25),
                                        background_color=[0.5, 0.5, 0.5, 0.8],
                                        )


        label_container.add_widget(Label(size_hint_x=1))
        label_container.add_widget(self.hex_input)
        label_container.add_widget(Label(size_hint_x=1))

        button_container.add_widget(Label(size_hint_x=1))
        button_container.add_widget(self.selected_protocol_button)
        button_container.add_widget(self.apply_color_button)
        button_container.add_widget(Label(size_hint_x=1))

        bottom_stack_container.add_widget(Label(size_hint_y=0.5))
        bottom_stack_container.add_widget(label_container)
        bottom_stack_container.add_widget(Label(size_hint_y=0.5))
        bottom_stack_container.add_widget(button_container)
        bottom_stack_container.add_widget(Label(size_hint_y=1))

        grid_layout.add_widget(Label(size_hint_y=0.1))
        grid_layout.add_widget(self.clr_picker)

        #Colorwheel is not correctly positioned in grid_layout for linux, so we set the origin here
        self.clr_picker._origin = (self.accordion.size[0]/2, self.accordion.size[0])
        grid_layout.add_widget(bottom_stack_container)

        return grid_layout



    def collapse_settings_panel(self, accordion_panel: AccordionItem, value: bool) -> None:

        """
        Callable to close settings panel
        """

        if value == False:
            self.gui_manager.settings_panel_toggle()
            self.about_accordion_panel.collapse = False



    def init_accordion(self) -> None:

        """
        Convience function to initalize the Accordion outside of constructor. Something to do with order of operations in things being created.
        (probably will be refactored later)
        """

        self.about_accordion_panel = AccordionItem(title="About")
        self.about_accordion_panel.id = "about"

        change_colors_panel = AccordionItem(title="Colors")
        change_colors_panel.id = "colors"

        sniffer_settings_panel = AccordionItem(title="Sniffer Settings")
        sniffer_settings_panel.id = "sniffer"

        save_session_panel = AccordionItem(title="Save Session Data")
        save_session_panel.id = "save"

        display_settings_panel = AccordionItem(title="Display Settings")
        display_settings_panel.id = "display"
    

        dismiss_panel = AccordionItem(title="Dismiss")
        dismiss_panel.id = "dismiss"
        dismiss_panel.bind(collapse=self.collapse_settings_panel)
        dismiss_panel.background_normal = os.path.join( self.gui_manager.resource_path, "assets/images/buttons/black.png" )

        self.about_accordion_panel.add_widget(self.create_about_panel())
        change_colors_panel.add_widget(self.create_colors_panel())
        sniffer_settings_panel.add_widget(self.create_sniffer_settings_panel())
        save_session_panel.add_widget(self.create_save_session_panel())
        display_settings_panel.add_widget(self.create_display_settings())

        self.accordion.add_widget(self.about_accordion_panel)
        self.accordion.add_widget(change_colors_panel)
        self.accordion.add_widget(save_session_panel)
        self.accordion.add_widget(display_settings_panel)
        self.accordion.add_widget(sniffer_settings_panel)
        

        self.accordion.add_widget(dismiss_panel)

        if self.gui_manager.first_time_starting == True:
            self.settings_panel_scatter.pos = (0, dp(50))

        else:
            self.settings_panel_scatter.pos = self.gui_manager.config_variables_dict["position_dictionary"]["settings_panel_pos"]

        with self.settings_panel_scatter.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)
            RoundedRectangle(
                            size=self.settings_panel_scatter.size,
                            pos=(0, 0),
                            radius=[(20, 20), (20, 20), (20, 20), (20, 20)],
                            )

        self.about_accordion_panel.collapse = False

        self.init_data_summary_labels()





    def init_data_summary_labels(self) -> None:

        """
        Initalize data summary popup labels.
        """

        self.connection_label = Label(text="", pos=(dp(165), dp(-13)), markup=True)

        reset_sniffer_button = Button()
        reset_sniffer_button.on_press = self.reset_session
        reset_sniffer_button.font_size = sp(8)
        reset_sniffer_button.border = (0,0,0,0)
        reset_sniffer_button.size = (dp(20), dp(20))
        reset_sniffer_button.pos = (dp(0),dp(3))
        reset_sniffer_button.size_hint_x = 1
        reset_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/reset.png")
        reset_sniffer_button.background_down = os.path.join(self.resource_path, "assets/images/UI/reset-down.png")

        self.switch_sniffer_button = Button()
        self.switch_sniffer_button.font_size = sp(8)
        self.switch_sniffer_button.border = (0,0,0,0)
        self.switch_sniffer_button.size = (dp(20), dp(20))
        self.switch_sniffer_button.pos = (dp(23),dp(3))
        self.switch_sniffer_button.bind(on_press=self.open_remote_connect_dropdown_short)
        self.switch_sniffer_button.size_hint_x = 1
        self.switch_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/computer_icon.png")
        self.switch_sniffer_button.background_down = os.path.join(self.resource_path, "assets/images/UI/computer_icon-down.png")

        self.connection_label_scatter = Scatter()
        self.connection_label_scatter.size = (dp(360), dp(25))



        if self.gui_manager.first_time_starting:

            connection_label_pos = (self.gui_manager.config_variables_dict["position_dictionary"]["connection_label_pos"] )
            connection_label_pos = (dp(connection_label_pos[0]), dp(connection_label_pos[1]))
        else:
            connection_label_pos = (self.gui_manager.config_variables_dict["position_dictionary"]["connection_label_pos"] )

        self.connection_label_scatter.pos = (connection_label_pos[0], connection_label_pos[1])


        self.connection_label_scatter.add_widget(reset_sniffer_button)
        self.connection_label_scatter.add_widget(self.switch_sniffer_button)
        self.connection_label_scatter.add_widget(self.connection_label)
        
        self.connection_label_layout = FloatLayout()
        self.connection_label_layout.size_hint = (None, None)
        self.connection_label_layout.size = (dp(300), dp(25))

        self.connection_label_layout.add_widget(self.connection_label_scatter)

        with self.connection_label_scatter.canvas:
            Color(1, 1, 1, 0.1)

            RoundedRectangle(
                            size=self.connection_label_scatter.size,
                            pos=(0, 0),
                            radius=[(0, 0), (dp(10), dp(10)), (dp(10), dp(10)), (0, 0)],
                            )

        self.play_audio_checkbox.active = True if self.gui_manager.config_variables_dict["play_audio_bool"] else False
            
       

        if self.gui_manager.connected_to_sniffer == True:

            connection_key = self.gui_manager.config_variables_dict["last_connection"]

            connected_port = self.gui_manager.config_variables_dict["stored_connections"][connection_key]["connection_info"][1]

            self.connection_label.text = f"[color=#00ff00][b]Connected[/b][/color] to [color=#00ff00][b]{connection_key}[/color][/b] on port [color=#00ff00][b]{connected_port}[/color][/b]"

        else:  # self.gui_manager.connected_to_sniffer == False

            self.connection_label.text = "[color=FF0000][b]Not Connected[/color][/b]"



    def select_interface(self, calling_button: Button) -> None:

        """
        Send a msg to network_sniffer.py to listen on a particular interface
        """

        msg = bytes( f"interface {calling_button.text}".encode("utf-8"))

        self.gui_manager.server_socket.send(msg)
                                                    #zmq=NOBLOCK
        return_msg = self.gui_manager.server_socket.recv()

        if return_msg.startswith(b"listening on"):

            self.interface_label.text = f"Interface: [color=#00ff00][b]{calling_button.text}[/b][/color]"

            try:
                    self.gui_manager.server_socket.send(b'activate')
                                                            #zmq=NOBLOCK
                    return_msg = self.gui_manager.server_socket.recv()

                    if return_msg == b"True":
                        self.activate_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/green_button.png")
                        self.activate_sniffer_button.text = "Sniffer Activated"

            except:

                self.activate_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/red_button.png")
                self.activate_sniffer_button.text = "Sniffer Deactivated"

        elif return_msg.startswith(b"unsupported"):

            self.interface_label.text = f"[color=#00ff00][b]Error[/b][/color]"

        self.connect_to_interface_dropdown.dismiss()


    def dynamic_dropdown_resize(self, btn, text) -> None:

        """
        Hack to dynamically change dropdown button size based on button texture_size
        """
            
        if btn.texture_size[0] > self.largest_button_texture_size:
            self.largest_button_texture_size = btn.texture_size[0]

            for buttons in self.connect_to_interface_dropdown.children[0].children:
                buttons.width = sp(btn.texture_size[0]) + sp(20)
     

            


    def initalize_interface_dropdown(self):
        
        """
        Populate Dropdown with Network Interfaces from Sniffer
        """

        for key in self.gui_manager.interface_dictionary.keys():

            if key  == "OS":
                pass

            else:
            
                btn = Button(text = key, font_size = sp(12))
                btn.background_color = (.7, .7, .7, 1)
                btn.border = (0,0,0,0)
                btn.size_hint = (None, None)
                btn.height=sp(22)
                btn.bind(texture_size= self.dynamic_dropdown_resize)
                btn.bind(on_press = self.select_interface)

                self.connect_to_interface_dropdown.add_widget(btn)

      


    def create_settings_accordian_panel(self) -> AnchorLayout:

        """
        Construct Settings accordian panel and return layout
        """

        dismiss_settings_panel = Button(
            text="Dismiss",
            background_color=[0, 0, 0, 0.5],
            on_press=self.gui_manager.settings_panel_toggle,
            size_hint_x=0.2,
        )

        box_layout_buttons = BoxLayout()
        box_layout_buttons.size_hint = (1, 1)
        box_layout_buttons.orientation = "vertical"

        box_layout_buttons.add_widget(Label())

        box_layout_buttons.add_widget(Label())

        box_layout_buttons.add_widget(Label())

        container_6 = BoxLayout(orientation="horizontal")
        container_6.add_widget(Label(size_hint_x=0.3))
        container_6.add_widget(dismiss_settings_panel)
        container_6.add_widget(Label(size_hint_x=0.3))
        box_layout_buttons.add_widget(container_6)

        box_layout_buttons.add_widget(Label())

        return box_layout_buttons



    def create_about_panel(self) -> RelativeLayout:

        """
        Construct About accordian panel
        """

        self.web_button = Button(
            text="Website",
            size_hint=(1, 0.08),
            on_press=self.go_to_web,
            background_color=[0.5, 0.5, 0.5, 0.8],
            border = (0,0,0,0)
        )

        label = Label()
        label.text = """This tool is built for the people. With your support, I will continue to build and integrate with other open-source technologies. In time, this tool could become invaluable public infrastructure. Consider supporting this project with donations, code, feedback, or showing others.\n\nThank you!\n\nTinkeringEngr\nTinkeringEngr@protonmail.com"""
        label.halign = "center"
        label.valign = "center"

        label.text_size = (dp(335), None)

        layout = RelativeLayout()
        layout.add_widget(label)
        webbutton_container = BoxLayout(orientation="horizontal")

        webbutton_container.add_widget(Label(size_hint_x=0.5))
        webbutton_container.add_widget(self.web_button)
        webbutton_container.add_widget(Label(size_hint_x=0.5))
        webbutton_container.pos = (dp(0), dp(15))
        layout.add_widget(webbutton_container)

        return layout



    def go_to_web(self, go_to_web_button: Button):

        """
        Function to take user to Network Visualizer website
        """

        self.web_button.text = "http://www.tinkeringengr.life/"
        webbrowser.open("http://www.tinkeringengr.life/", new=2, autoraise=True)



    def reset_session(self, *reset_session_button: Button) -> None:

        """
        Reset the Network Sniffer -- Delete database  entry and assosciated data structures
        Send reset signal to network sniffer server to reset on both ends
        """

        try:
            self.gui_manager.server_socket.send(b"reset")
            msg = self.gui_manager.server_socket.recv()

            if msg == b"received reset":
                self.gui_manager.transition.direction = "down"
                self.gui_manager.current = "loading"
                Clock.schedule_once(partial(self.gui_manager.kivy_application.switch_sniffer, self.gui_manager.config_variables_dict["last_connection"]), 1)

        except:
            pass



    def create_save_session_panel(self):

        """
        Popup message displayed when save session data button clicked.
        """

        save_session_content = BoxLayout(orientation="vertical")

        self.session_popup_description = Label(
                                                text=f"Session data is saved to a sqlite database\n (alphanumeric characters only)",
                                                halign="center",
                                                valign="center",
                                                text_size=(self.accordion.width - sp(50), None),
                                            )

        self.save_session_textinput = TextInput(
                                                on_text_validate=self.save_session_into_database,
                                                multiline=False
                                                )

        save_button = Button(text="Save", on_press=self.save_session_into_database, size_hint_x=0.5)
        save_button.background_color = [0.5, 0.5, 0.5, 0.8]

        copy_database_location_button = Button( text="Copy Database Location",
                                                on_press=self.copy_database_location,
                                                background_color=[0.5, 0.5, 0.5, 0.8],
                                                border = (0,0,0,0)
                                                )

        save_session_content.add_widget(Label(size_hint_y=1))

        save_session_content.add_widget(self.session_popup_description)

        save_session_content.add_widget(Label(size_hint_y=0.2))

        horizontal_container = BoxLayout(orientation="horizontal", size_hint_y=0.4)
        horizontal_container.add_widget(Label(size_hint_x=0.3))
        horizontal_container.add_widget(self.save_session_textinput)
        horizontal_container.add_widget(Label(size_hint_x=0.3))

        save_session_content.add_widget(horizontal_container)

        save_session_content.add_widget(Label(size_hint_y=0.2))

        horizontal_container2 = BoxLayout(orientation="horizontal", size_hint_y=0.4)
        horizontal_container2.add_widget(Label(size_hint_x=0.1))
        horizontal_container2.add_widget(save_button)
        horizontal_container2.add_widget(copy_database_location_button)
        horizontal_container2.add_widget(Label(size_hint_x=0.1))

        save_session_content.add_widget(horizontal_container2)

        save_session_content.add_widget(Label(size_hint_y=1))

        return save_session_content


    # def use_date_time(self, *args):

    #     """
    #     Set text input for save_session_textinput to date-time
    #     """

    #     time_stamp = time.time()
    #     date_timestamp = datetime.datetime.fromtimestamp(time_stamp).strftime("%d-%m-%Y-%H:%M:%S")
    #     self.save_session_textinput.text =  date_timestamp


    def copy_database_location(self, calling_button: Button) -> None:

        """
        Copy database location to clipboard using pyperclip
        """

        if self.gui_manager.kivy_application.operating_system == "Darwin" and getattr(sys, "frozen", False):
            database_location = os.path.join( self.gui_manager.kivy_application.darwin_network_visualizer_dir, "data.sqlite")

        else:
            database_location = os.path.join(self.gui_manager.resource_path, "assets/database/data.sqlite")
        
        try: #Some OS's may not have clipboard functionality
            pyperclip.copy(database_location)
        except:
            pass
        



    def save_session_into_database(self, save_session_button: Button):

        """
        Validate and insert session data (sniffer dictionary) into sqlite database
        """
 
        session_to_save = self.save_session_textinput.text

        if session_to_save.isalnum():  # check alphanumeric condition

            if session_to_save[0].isnumeric():  # Can't start with a number (sqlite) condition 
                self.session_popup_description.color = (1, 0, 0, 1)
                self.session_popup_description.text = ("Can't start with a number..blame sqlite.")

            else:

                json_session_data = self.gui_manager.sniffer_dictionary # JSON serialization faciliated by sqlite registration on insertion (see database_config.py)

                try:
                    cursor = db.cursor()
                    cursor.execute(f"""INSERT OR IGNORE INTO sessions (session_name, session_data) VALUES ("{session_to_save}", "{json_session_data}")""")
                    db.commit()

                    self.session_popup_description.color = (0, 1, 0, 1)
                    self.session_popup_description.text = f"Success!"
                    self.save_session_textinput.text = ""

                except Exception as e:
                    self.session_popup_description.color = (1, 0, 0, 1)
                    self.session_popup_description.text = f"Error: {e}"
                    return

        else:
            self.session_popup_description.color = (1, 0, 0, 1)
            self.session_popup_description.text = f"Session name isn't alphanumeric"



    def generate_keys(self, *args) -> None:

        """
        Generate new cryptographic keys
        """

        if self.gui_manager.kivy_application.operating_system == "Darwin" and getattr(sys, "frozen", False):

            keys_dir = os.path.join(self.gui_manager.kivy_application.darwin_network_visualizer_dir, "keys/")

        else:
            keys_dir = os.path.join(self.resource_path, "configuration/keys/")
  

        if os.path.exists(keys_dir):
            shutil.rmtree(keys_dir)
            os.mkdir(keys_dir)
            
        else:
            os.mkdir(keys_dir)
            


        server_public_file, server_secret_file = zmq.auth.create_certificates(keys_dir, "server")
        client_public_file, client_secret_file = zmq.auth.create_certificates(keys_dir, "client")



    def connect_to_network_sniffer(self, connect_to_remote_server_button: Button) -> None:

        """
        Connect to sniffer at remote location. (phone, webserver, etc)
        """

        
        ip = connect_to_remote_server_button.ip
        req_port = connect_to_remote_server_button.port
        sub_port = req_port + 1
        
 
        if self.gui_manager.sniffer_process == None and ip == "localhost":

                try:
                    keywords = {"port": req_port}
                    self.gui_manager.sniffer_process = Process(name="sniffer", target=Sniffer, kwargs=keywords)
                    self.gui_manager.sniffer_process.start()

                    #BUG: remove atexit and switch to multiexit 
                    atexit.register(self.gui_manager.sniffer_process.terminate)  # kill sniffer

                except:
                    # TODO: proper error handling
                    self.gui_manager.sniffer_process == None


        if self.gui_manager.server_socket == None:

            self.gui_manager.current_connection_key = connect_to_remote_server_button.text

            if self.gui_manager.kivy_application.operating_system == "Darwin" and getattr(sys, "frozen", False): #MacOS and packaged (not terminal executed)
            
                    keys = zmq.auth.load_certificate( os.path.join(self.gui_manager.kivy_application.darwin_network_visualizer_dir, "keys/client.key_secret") )
                    server_key, _ = zmq.auth.load_certificate( os.path.join(self.gui_manager.kivy_application.darwin_network_visualizer_dir, "keys/server.key") )

            else:

                keys = zmq.auth.load_certificate(os.path.join(self.resource_path, "configuration/keys/client.key_secret"))
                server_key, _ = zmq.auth.load_certificate( os.path.join(self.resource_path, "configuration/keys/server.key"))

            try:

                connect_string_req = f"tcp://{ip}:{req_port}"
                connect_string_sub = f"tcp://{ip}:{sub_port}"

                context = zmq.Context()
                # self.gui_manager.server_socket = context.socket(zmq.REQ)  # client/server pattern for guaranteed messages
                # self.gui_manager.server_socket.setsockopt(zmq.CURVE_PUBLICKEY, keys[0])
                # self.gui_manager.server_socket.setsockopt(zmq.CURVE_SECRETKEY, keys[1])
                # self.gui_manager.server_socket.setsockopt(zmq.CURVE_SERVERKEY, server_key)
                # self.gui_manager.server_socket.connect(connect_string_req)

                self.gui_manager.server_socket = pynng.Req0()
                self.gui_manager.server_socket.dial(connect_string_req)

                self.gui_manager.data_socket = context.socket(zmq.SUB)  # PUB/SUB pattern for sniffer data
                self.gui_manager.data_socket.setsockopt(zmq.CURVE_PUBLICKEY, keys[0])
                self.gui_manager.data_socket.setsockopt(zmq.CURVE_SECRETKEY, keys[1])
                self.gui_manager.data_socket.setsockopt(zmq.CURVE_SERVERKEY, server_key)
                self.gui_manager.data_socket.connect(connect_string_sub)

                self.gui_manager.data_socket.setsockopt_string(zmq.SUBSCRIBE, "")

                self.gui_manager.config_variables_dict["last_connection"] = self.gui_manager.current_connection_key

            except Exception as e:

                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)


            self.gui_manager.populate_malicious_table()

            self.connection_label.text = f"[color=#00ff00][b]Connected[/b][/color] to [color=#00ff00][b]{self.gui_manager.current_connection_key}[/color][/b] on port [color=#00ff00][b]{req_port}[/color][/b]"

            self.gui_manager.request_sniffer_state()
            self.gui_manager.set_sniffer_state()
            self.initalize_interface_dropdown()


        else:
            
            self.gui_manager.transition.direction = "down"
            self.gui_manager.current = "loading"
            Clock.schedule_once(partial(self.gui_manager.kivy_application.switch_sniffer, connect_to_remote_server_button.text), 0.75)

  
        self.remote_connect_dropdown.dismiss()
        self.remote_connect_dropdown_short.dismiss()



    def copy_encryption_key_directory(self, *args) -> None:

        """
        Copies path of encryption keys to clipboard
        """

        if self.gui_manager.kivy_application.operating_system == "Darwin" and getattr(sys, "frozen", False): #MacOS and packaged (not terminal executed)
            crypto_key_location = os.path.join(self.gui_manager.kivy_application.darwin_network_visualizer_dir, "keys/")
    
        else:

            crypto_key_location = os.path.join(self.resource_path, "configuration/keys/")

        try: #Some OS's may not have clipboard functionality
            pyperclip.copy(crypto_key_location)
        except:
            pass



    def more_info(self, moreinfo_button: Button) -> None:

        """
        Displays a popup giving a brief explanation of how networkv_isualizer.py and network_sniffer.py communicate.
        """

        grid_layout = GridLayout(cols=1)

        popup = Popup(
                            title="",
                            content=grid_layout,
                            size_hint=(None, None),
                            size=(sp(750), sp(275)),
                            auto_dismiss=True,
                        )


        text_description = Label(halign="center", valign="middle", markup=True, text_size = (sp(725), None))

        text_description.size = text_description.texture_size

        text_description.text = f"""[b]Network Visualizer[/b] uses the ZMQ library to handle the communication between the [b][color=19a8ffff]Network Sniffer[/color][/b] and the [b][color=00FF00]Visualizer[/color][/b]. This communication is encrypted using CurveZMQ. In order for this encryption to occur, private and public keys are generated the first time the software runs or when new keys are generated by the user. \n\n If the [b][color=19a8ffff]Network Sniffer[/color][/b] is running on a remote computer (like a webserver in a distant land), these keys need to be securely transfered by the user. The [b][color=00FF00]Visualizer[/color][/b] requires the "[b][color=00FF00]client.key_secret[/color][/b]" and "[b][color=00FF00]server.key[/color][/b]" in the key directory. The [color=19a8ffff][b]Network Sniffer[/color][/b] requires the "[color=19a8ffff][b]server.key_secret[/color][/b]" in the key directory. The button below copies the directory path of the generated cryptographic keys."""


        copy_path_to_keys_boxlayout = BoxLayout(orientation="horizontal", size_hint_y=0.2)
        copy_path_to_keys = Button(text="Copy Path to Encryption Keys Directory",on_press = self.copy_encryption_key_directory)

        copy_path_to_keys_boxlayout.add_widget(Label(size_hint_x=0.5))
        copy_path_to_keys_boxlayout.add_widget(copy_path_to_keys)
        copy_path_to_keys_boxlayout.add_widget(Label(size_hint_x=0.5))

        grid_layout.add_widget(Label(size_hint_y=0.5))
        grid_layout.add_widget(text_description)
        grid_layout.add_widget(Label(size_hint_y=0.5))
        grid_layout.add_widget(copy_path_to_keys_boxlayout)
        grid_layout.add_widget(Label(size_hint_y=0.1))
        popup.open()



    def add_remote_connection(self, calling_button: Button) -> None:

        """ 
        Callable to add remote sniffer connection
        """

        servername = self.server_name_textinput.text.strip()
        ip = self.server_ip_textinput.text.strip()
        port_input = self.server_port_textinput.text.strip()

        try:
            var = ipaddress.ip_address(ip) #validate IPv4 or IPv6 address
        except:
            self.server_ip_textinput.text = "Invalid IP Address"
            self.server_ip_textinput.foreground_color = (1, 0, 0, 1)
            return

        try:
            port = int(port_input)
            if port > 65534 or port < 1023:
                raise Exception

        except:
            self.server_port_textinput.text = "Invalid Port"
            self.server_port_textinput.foreground_color = (1, 0, 0, 1)
            return

        self.server_name_textinput.text = "Sucess!"
        self.server_name_textinput.foreground_color = (0, 0, 0, 1)

    
        self.server_port_textinput.text = ""
        self.server_ip_textinput.text = ""

        self.remote_connect_dropdown.children[0].clear_widgets()
        self.remote_connect_dropdown_short.children[0].clear_widgets()

        self.gui_manager.config_variables_dict["stored_connections"][servername] = { "connection_info": [ip, port],
                                                                                     "graph_position": None,
                                                                                     "mercator_position": None
                                                                                   }
 

        for server_name in self.gui_manager.config_variables_dict["stored_connections"].keys():

            ip = self.gui_manager.config_variables_dict["stored_connections"][server_name]["connection_info"][0]
            port = self.gui_manager.config_variables_dict["stored_connections"][server_name]["connection_info"][1]

            btn = Button(text=server_name)
            btn.ip = ip
            btn.port = port
            btn.size_hint = (None, None)
            btn.width = dp(190)
            btn.height = dp(20)
            btn.background_color = (.8, .8, .8, 0.8)

            btn.bind(on_press=self.connect_to_network_sniffer)

            self.remote_connect_dropdown.add_widget(btn)

     
            btn = Button(text=server_name)
            btn.ip = ip
            btn.port = port
            btn.size_hint = (None, None)
            btn.width = dp(190)
            btn.height = dp(20)
            btn.background_color = (.8, .8, .8, 0.8)

            btn.bind(on_press=self.connect_to_network_sniffer)
            self.remote_connect_dropdown_short.add_widget(btn)

        server_name = server_name.replace(" ", "")
        malicious_ips_database_name = server_name +"_malicious_ips"
        cursor = db.cursor()
        cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {malicious_ips_database_name} (ip TEXT PRIMARY KEY, description TEXT DEFAULT 'NONE', ban_lists INTEGER DEFAULT 0, time_stamp TEXT DEFAULT 'NONE', location_country TEXT DEFAULT 'NONE', packet_count INTEGER DEFAULT 0, data_in INTEGER DEFAULT 0, data_out INTEGER DEFAULT 0,  ip_data dictionary, abuse_email TEXT DEFAULT 'NONE', whois_info TEXT DEFAULT 'NONE')"
                )

        db.commit()




    def activate_sniffer(self, calling_button:Button) -> None:
        
        """
        Callable to activate or deactivate sniffer 
        """

        if self.activate_sniffer_button.text == "Sniffer Deactivated":

            try:
                self.gui_manager.server_socket.send(b'activate')
                                                        #zmq=NOBLOCK
                return_msg = self.gui_manager.server_socket.recv()

                if return_msg == b"True":
                    self.activate_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/green_button.png")
                    self.activate_sniffer_button.text = "Sniffer Activated"

            except:

                self.activate_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/red_button.png")
                self.activate_sniffer_button.text = "Sniffer Deactivated"
                

        elif self.activate_sniffer_button.text == "Sniffer Activated":

            try:
                self.gui_manager.server_socket.send(b'deactivate')
                return_msg = self.gui_manager.server_socket.recv()

                if return_msg == b"False":
                    self.activate_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/red_button.png")
                    self.activate_sniffer_button.text = "Sniffer Deactivated"
        
            except:
                
                self.activate_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/green_button.png")
                self.activate_sniffer_button.text = "Sniffer Activated"




    def create_sniffer_settings_panel(self):

        """
        Popup menu for configuring and connecting to Sniffer
        """

        size = (dp(390), dp(290))

        base = BoxLayout(orientation="vertical", size=size)
        section = BoxLayout(orientation="horizontal")

        generate_keys_button = Button(
                                    text="Generate New Encryption Keys",
                                    on_press=self.generate_keys,
                                    size_hint=(1, 1),
                                    background_color=[0.5, 0.5, 0.5, 0.8],
                                    border = (0,0,0,0)
                                    )

        moreinfo_button = Button(text="Encryption Information", on_press=self.more_info, size_hint=(1, 1), background_color=[0.5, 0.5, 0.5, 0.8], border = (0,0,0,0))


        self.remote_connect_dropdown = DropDown()

        self.remote_connect_dropdown_short = DropDown()
        self.remote_connect_dropdown_short.auto_width = False
        self.remote_connect_dropdown_short.size = (dp(300), dp(50))


        for connection in self.gui_manager.config_variables_dict["stored_connections"].keys():
            

            btn = Button(text=connection)
            btn.ip = self.gui_manager.config_variables_dict["stored_connections"][connection]["connection_info"][0]
            btn.port = self.gui_manager.config_variables_dict["stored_connections"][connection]["connection_info"][1]
            btn.size_hint = (None, None)
            btn.width = dp(190)
            btn.height = dp(20)
            btn.background_color = (.8, .8, .8, 0.8)
            btn.border = (0,0,0,0) 
            btn.bind(on_press=self.connect_to_network_sniffer)

            self.remote_connect_dropdown.add_widget(btn)


            btn = Button(text=connection)
            btn.ip = self.gui_manager.config_variables_dict["stored_connections"][connection]["connection_info"][0]
            btn.port = self.gui_manager.config_variables_dict["stored_connections"][connection]["connection_info"][1]
            btn.size_hint = (None, None)
            btn.width = dp(190)
            btn.height = dp(20)
            btn.background_color = (.8, .8, .8, 0.8)
            btn.border = (0,0,0,0) 
            btn.bind(on_press=self.connect_to_network_sniffer)

            self.remote_connect_dropdown_short.add_widget(btn)


        reset_button = Button(
                            text="Reset",
                            on_press=self.reset_session,
                            size_hint_x=0.5,
                            background_color=[0.5, 0.5, 0.5, 0.8],
                            border = (0,0,0,0)
                            )

        self.connect_to_network = Button(text="Connect to Network Sniffer", size_hint_x=2, background_color=[0.5, 0.5, 0.5, 0.8], border = (0,0,0,0))
        self.connect_to_network.bind(on_press=self.open_remote_connect_dropdown)

        # connect_to_network_relative = BoxLayout(orientation="horizontal")
        

        # connect_to_network_image = Image()
        # connect_to_network_image.source = os.path.join( self.resource_path, "assets/images/UI/computer_icon.png")
        # connect_to_network_image.size_hint = (None, None)
        # connect_to_network_image.size = (dp(200), dp(200))
        # #connect_to_network_image.pos = self.connect_to_network.pos
        
        # self.connect_to_network.add_widget(connect_to_network_relative)
        # connect_to_network_relative.add_widget(connect_to_network_image)



        add_remote_connection_button = Button(text="Add Remote Connection", 
                                              on_press=self.add_remote_connection, 
                                              background_color=[0.5, 0.5, 0.5, 0.8],
                                              border = (0,0,0,0)
                                             )

        self.server_name_textinput = TextInput(text="Name")
        self.server_ip_textinput = TextInput(text="IP Address")
        self.server_port_textinput = TextInput(text="Port")

        def on_focus(instance: TextInput, value) -> None:

            """
            Used to clear text input on focus
            """

            if value:
                instance.text = ""
   


        self.server_name_textinput.bind(focus=on_focus)
        self.server_ip_textinput.bind(focus=on_focus)
        self.server_port_textinput.bind(focus=on_focus)



        self.interface_label = Label(text="Interface: ", markup=True)

        self.set_default_port_button = Button(text="Set Default Port", background_color=[0.5, 0.5, 0.5, 0.8], border = (0,0,0,0))
        self.set_default_port_button.bind(on_press=self.set_default_port)

        self.default_port_textinput = TextInput(text="", size_hint_x=0.5)

        self.connect_to_interface_dropdown  = DropDown()


        self.connect_to_interface = Button(text="Select Interface", background_color=[0.5, 0.5, 0.5, 0.8], border = (0,0,0,0))
        self.connect_to_interface.bind(on_press=self.open_connect_to_interface_dropdown)


        self.activate_sniffer_button = Button()
        self.activate_sniffer_button.bind(on_press=self.activate_sniffer)
        self.activate_sniffer_button.color = (0, 0, 0, 1)
        self.activate_sniffer_button.text = "Sniffer Deactivated"
        self.activate_sniffer_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/red_button.png")
        

        
        # Layout Widgets

        base.add_widget(Label(size_hint_y=0.5))

        remote_connect_button_content = BoxLayout(orientation="horizontal")
        remote_connect_button_content.add_widget(Label(size_hint_x=0.5))
        remote_connect_button_content.add_widget(self.connect_to_network)
        remote_connect_button_content.add_widget(Label(size_hint_x=0.2))
        remote_connect_button_content.add_widget(reset_button)
        remote_connect_button_content.add_widget(Label(size_hint_x=0.5))
        base.add_widget(remote_connect_button_content)

        base.add_widget(Label(size_hint_y=0.5))

        radio_container = BoxLayout(orientation="horizontal")
        radio_container.add_widget(Label(size_hint_x=.8))
        radio_container.add_widget(self.activate_sniffer_button)
        radio_container.add_widget(Label(size_hint_x=.8))

        base.add_widget(radio_container)
        base.add_widget(Label(size_hint_y=0.5))


        section.add_widget(Label(size_hint_x=1))
        section.add_widget(Label(text="Automatically Connect on Startup"))
        section.add_widget(Label(size_hint_x=0.3))
        section.add_widget(self.auto_connect_checkbox)
        section.add_widget(Label(size_hint_x=1))
        base.add_widget(section)

        base.add_widget(Label(size_hint_y=0.5))



        connection_information_container = BoxLayout(orientation="horizontal")
        connection_information_container.add_widget(self.interface_label)

        base.add_widget(connection_information_container)
        base.add_widget(Label())
        base.add_widget(Label())

        stacked_container = BoxLayout(orientation="vertical", size_hint_y=2)
        horizontal_container = BoxLayout(orientation="horizontal")

        horizontal_container.add_widget(Label(size_hint_x=.2))
        horizontal_container.add_widget(self.default_port_textinput)
        horizontal_container.add_widget(Label(size_hint_x=.2))

        stacked_container.add_widget(horizontal_container)
        stacked_container.add_widget(self.set_default_port_button)

        stacked_container_2 = BoxLayout(orientation="vertical", size_hint_y=2)
        stacked_container_2.add_widget(Label(size_hint_y=.5))
        stacked_container_2.add_widget(self.connect_to_interface)
        stacked_container_2.add_widget(Label(size_hint_y=.5))

        set_default_port_container = BoxLayout(orientation="horizontal")
        set_default_port_container.add_widget(Label(size_hint_x=0.1))
        set_default_port_container.add_widget(stacked_container_2)
        set_default_port_container.add_widget(Label(size_hint_x=0.1))
        set_default_port_container.add_widget(stacked_container)
        set_default_port_container.add_widget(Label(size_hint_x=0.1))
        base.add_widget(set_default_port_container)


        base.add_widget(Label())

        server_ip_textinput_content = BoxLayout(orientation="horizontal", size_hint_y=1.2)
        server_ip_textinput_content.add_widget(Label(size_hint_x=0.1))
        server_ip_textinput_content.add_widget(self.server_name_textinput)
        server_ip_textinput_content.add_widget(Label(size_hint_x=0.1))
        server_ip_textinput_content.add_widget(self.server_ip_textinput)
        server_ip_textinput_content.add_widget(Label(size_hint_x=0.1))
        server_ip_textinput_content.add_widget(self.server_port_textinput)
        server_ip_textinput_content.add_widget(Label(size_hint_x=0.1))
        base.add_widget(server_ip_textinput_content)

        base.add_widget(Label(size_hint_y=0.5))

        store_remote_sniffer_content = BoxLayout(orientation="horizontal")
        store_remote_sniffer_content.add_widget(Label(size_hint_x=0.5))
        store_remote_sniffer_content.add_widget(add_remote_connection_button)
        store_remote_sniffer_content.add_widget(Label(size_hint_x=0.5))
        base.add_widget(store_remote_sniffer_content)

        base.add_widget(Label())

        moreinfo_button_content = BoxLayout(orientation="horizontal")
        moreinfo_button_content.add_widget(Label(size_hint_x=0.5))
        moreinfo_button_content.add_widget(moreinfo_button)
        moreinfo_button_content.add_widget(Label(size_hint_x=0.5))
        base.add_widget(moreinfo_button_content)

        base.add_widget(Label(size_hint_y=0.2))

        moreinfo_button_content2 = BoxLayout(orientation="horizontal")
        moreinfo_button_content2.add_widget(Label(size_hint_x=0.25))
        moreinfo_button_content2.add_widget(generate_keys_button)
        moreinfo_button_content2.add_widget(Label(size_hint_x=0.25))
        base.add_widget(moreinfo_button_content2)

        base.add_widget(Label(size_hint_y=0.5))

        return base



    def apply_color(self, apply_color_button: Button):

        """
        Takes color input and sets the color in config_variables_dict
        """

        try:
            color_value = get_color_from_hex( self.hex_input.text )  # e.g. FFFFFFFF to [1,1,1,1] (RGBA)

            if len(color_value) == 4 or len(color_value) == 3:
                pass
            else:
                return
        except:
            return  # unable to get hex value so don't proceed

        for child in self.features_dropdown.children[0].children:
            if child.id == self.selected_protocol_button.text:
                child.color = color_value


        if self.selected_protocol_button.text == "TCP Protocol":
            self.gui_manager.config_variables_dict["color_dictionary"]["TCP Protocol Color"] = color_value

        elif self.selected_protocol_button.text == "UDP Protocol":
            self.gui_manager.config_variables_dict["color_dictionary"]["UDP Protocol Color"] = color_value


        elif self.selected_protocol_button.text == "Other Protocol":
            self.gui_manager.config_variables_dict["color_dictionary"]["OTHER Protocol Color"] = color_value

        elif self.selected_protocol_button.text == "Data IN":
            self.gui_manager.config_variables_dict["color_dictionary"]["Data IN Color"] = color_value

        elif self.selected_protocol_button.text == "Data OUT":
            self.gui_manager.config_variables_dict["color_dictionary"]["Data OUT Color"] = color_value

        elif self.selected_protocol_button.text == "Summary Data":
            self.gui_manager.config_variables_dict["color_dictionary"]["Summary Data Color"] = color_value

        elif self.selected_protocol_button.text == "Exempt":
            self.gui_manager.config_variables_dict["color_dictionary"]["Exempt Color"] = color_value

        elif self.selected_protocol_button.text == "Widget Halo":
            self.gui_manager.config_variables_dict["color_dictionary"]["Widget Halo Color"] = color_value

            self.gui_manager.my_computer.set_widget_halo_color()

            for country in self.gui_manager.country_dictionary:

                country_widget = self.gui_manager.country_dictionary[country][0]
                country_widget.set_widget_halo_color()

                for city in self.gui_manager.country_dictionary[country][1]:

                    city_widget = self.gui_manager.country_dictionary[country][1][city][0]
                    city_widget.set_widget_halo_color()

                    for ip_widget in self.gui_manager.country_dictionary[country][1][city][1:]:  # access relevant IP widgets

                        ip_widget.set_widget_halo_color()

            



        self.selected_protocol_button.text = "Select Feature"
        self.selected_protocol_button.color = (1, 1, 1, 1)



    def open_remote_connect_dropdown(self, *call_button) -> None:

        """
        Kivy dropdown bug fix -- occasionally the dropdown menu will hang when using a lambda function so do this instead.
        """

        self.remote_connect_dropdown.open(self.connect_to_network)



    def open_remote_connect_dropdown_short(self, *call_button) -> None:

        """
        Kivy dropdown bug fix -- occasionally the dropdown menu will hang when using a lambda function so do this instead.
        """

        self.remote_connect_dropdown_short.open(self.switch_sniffer_button)



    def open_connect_to_interface_dropdown(self, *call_button) -> None:

        """
        Kivy dropdown bug fix -- occasionally the dropdown menu will hang when using a lambda function so do this instead. 
        """

        self.connect_to_interface_dropdown.open(call_button[0])


   
    def open_features_dropdown(self, call_button) -> None:

        """
        Kivy dropdown bug fix -- occasionally the dropdown menu will hang when using a lambda function so do this instead.
        """

        self.features_dropdown.open(call_button)



    def features_dropdown_color_text_change(self, *btn) -> None:

        """
        Select text color for each button in the features dropdown 
        """

        self.features_dropdown.select(btn[0].text)
        self.selected_protocol_button.color = self.gui_manager.config_variables_dict["color_dictionary"][f"{btn[0].text} Color"]



    def validate_color_textinput(self, text_input: TextInput, text: str):

        """
        Validate input color from user
        """

        try:
            self.apply_color_button.color = get_color_from_hex(text)
        except:
            pass



    def on_color_selection(self, colorwheel: ColorWheel, value: ObservableReferenceList) -> None:

        """
        Called on ColorWheel selection.
        """

        self.hex_input.text = str(self.clr_picker.hex_color)
        self.apply_color_button.color = self.clr_picker.color

        

    def set_default_port(self, button: Button) -> None:

        """
        Sets the default port network_sniffer.py process
        """

        port_input = self.default_port_textinput.text.strip()

        try:
            port = int(port_input)

            if port > 65534 or port < 1023:
                raise Exception

        except:
            self.default_port_textinput.foreground_color = (1, 0, 0, 1)
            self.default_port_textinput.text = "Error"          
            return

    

        self.gui_manager.config_variables_dict["stored_connections"][self.gui_manager.current_connection_key]["connection_info"][1] = port

        self.default_port_textinput.text = "Success!"
        self.default_port_textinput.foreground_color = (0, 0, 0, 1)
                


        msg = bytes( f"default_port {port_input}".encode("utf-8"))

        try:
            self.gui_manager.server_socket.send(msg)
            return_msg = self.gui_manager.server_socket.recv() #set no blocking?

            if return_msg == b"default port set":

                self.default_port_textinput.text = "Success!"
                self.default_port_textinput.foreground_color = (0, 0, 0, 1)
        except:
            pass

             
            
