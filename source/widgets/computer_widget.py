# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.


from math import sin, cos, pi
import os
# sys.path.append("..")

from utilities.database_config import db
from utilities.utils import (
                                map_to_range,
                                angle_between_points,
                                Computer_Icon_Scatter_Override,
                            )

from kivy.graphics import Color, RoundedRectangle, Line, InstructionGroup
from kivy.metrics import sp, dp
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty


class My_Computer(Widget):

    """
    GUI Widget for representing the users computer with member functions for displaying Country, City, and IP widgets.
    """

    def __init__(self, **kwargs) -> None:

        """
        Construct GUI widget and associated state.
        """

        super().__init__()

        self.pos = kwargs["center_position"]
        self.window_x = kwargs["window_x"]
        self.window_y = kwargs["window_y"]
        self.gui_manager = kwargs["gui_manager"]
        self.resource_path = kwargs["resource_path"]
        self.current_connection_key = kwargs["current_connection_key"]

        self.interface_dictionary = self.gui_manager.interface_dictionary
        self.my_mac_address = self.gui_manager.my_mac_address

        self.menu_boolean = False
        self.exempt = False
        
        self.attach = False
        self.mercator_layout_finished = False
        self.show_country_widgets = True
        self.show_city_widgets = True
        self.show_ip_widgets = True
        self.graph_layout_finished = True

        self.mylabel_bool = True if (self.gui_manager.config_variables_dict["computer_label"] == True) else False

        self.country_labels = True
        self.city_labels = True
        self.ip_labels = False

        self.country_phase = 0
        self.country_radius = dp(75)
        self.country_angle = 360

        self.city_phase = 0
        self.city_radius = dp(50)
        self.city_angle = 60

        self.ip_phase = 0
        self.ip_radius = 200
        self.ip_angle = 60

        self.total_data_out = 1
        self.total_data_in = 1


        # Set GUI widget position if connection to sniffer otherwise default position
        if self.current_connection_key and self.gui_manager.config_variables_dict["stored_connections"][self.current_connection_key]["graph_position"]:
            self.graph_position = self.initial_graph_position = self.gui_manager.config_variables_dict["stored_connections"][self.current_connection_key]["graph_position"]
            self.mercator_position = self.initial_mercator_position = self.gui_manager.config_variables_dict["stored_connections"][self.current_connection_key]["mercator_position"]

        else:
            self.graph_position = self.initial_graph_position = self.mercator_position = self.initial_mercator_position = ( self.window_x/2 - dp(17), self.window_y/2  - dp(17) )


        ##Create GUI widgets
        self.label = Label()
        self.label.text = "My Computer"
        self.label.font_size = sp(15)
        self.label.pos = (-dp(10), dp(17))

        self.container = FloatLayout()
        self.container.pos = (self.window_x/2 - dp(17), self.window_y/2  - dp(17))
        self.container.size_hint = (None, None)
        #TODO:dp(50)?
        self.container.size = (50, 50)
        

        self.icon_image = Image()
        self.icon_image.source = os.path.join( self.resource_path, "assets/images/UI/computer_icon.png")
        self.icon_image.size_hint = (None, None)
        self.icon_image.size = (dp(25), dp(25))
        self.icon_image.pos = (dp(5), dp(6))

        self.display_menu_button = Button()
        self.display_menu_button.size_hint = (None, None)
        self.display_menu_button.background_color = (0, 0, 0, 0)
        self.display_menu_button.size = (dp(20), dp(20))
        self.display_menu_button.pos = (dp(8), dp(8))
        self.display_menu_button.on_press = self.toggle_menu


        self.icon_scatter_widget = Computer_Icon_Scatter_Override()

        self.icon_scatter_widget.size_hint = (None, None)
        self.icon_scatter_widget.gui_manager = self
        self.icon_scatter_widget.pos = self.graph_position
        self.icon_scatter_widget.size = (dp(35), dp(35))

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

        self.icon_scatter_widget.canvas.add(self.default_widget_halo_instruction_group)
        
        self.display_menu_button.add_widget(self.icon_image)
        
        self.icon_scatter_widget.add_widget(self.display_menu_button)

        if self.mylabel_bool == True:
            self.icon_scatter_widget.add_widget(self.label)
            
        self.container.add_widget(self.icon_scatter_widget)

        self.add_widget(self.container)

        # with self.icon_scatter_widget.canvas.before:
        #     Color(1, 1, 1, 0.2)
        #     RoundedRectangle(
        #                     size=(dp(35), dp(35)),
        #                     pos=(0, 0),
        #                     radius=[
        #                             (dp(60), dp(50)),
        #                             (dp(50), dp(50)),
        #                             (dp(50), dp(50)),
        #                             (dp(50), dp(50)),
        #                            ]
        #                     )

        self.menu_popup = None #Populated by self.make_display_menu
        self.make_display_menu()

        self.city_labels = True



    # def set_widget_halo_color(self) -> None:

    #     """
    #     Sets the halo around (canvas instruction) of the associated Widget
    #     """

    #     try:
    #         self.icon_scatter_widget.canvas.remove(self.default_widget_halo_instruction_group)
    #     except:
    #         pass

    #     self.default_widget_halo_instruction_group = InstructionGroup()  
    #     self.default_widget_halo_instruction_group.add(Color(rgba =  self.gui_manager.config_variables_dict["color_dictionary"]["Default Halo Color"].copy()))
    #     self.default_widget_halo_instruction_group.add(  RoundedRectangle(
    #                                             size=self.icon_scatter_widget.size,
    #                                             pos=(0, 0),
    #                                             radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
    #                                             )  
    #                                       )

    #     self.icon_scatter_widget.canvas.insert(-1, self.default_widget_halo_instruction_group)


    #     self.icon_scatter_widget.remove_widget(self.display_menu_button)
    #     self.icon_scatter_widget.add_widget(self.display_menu_button)


    def set_position(self, my_ip_info: dict):

        """
        Callable to set GUI widget position
        """

        #position My_Computer widget here once we have sniffer IP
        if not self.gui_manager.config_variables_dict["stored_connections"][self.gui_manager.current_connection_key]["graph_position"]:

            screen_x, screen_y = self.gui_manager.calculate_mercator_coordinates( my_ip_info["longitude"], my_ip_info["latitude"] )
            self.mercator_position = self.initial_mercator_position = (screen_x, screen_y)
            self.graph_position = self.initial_graph_position = (self.window_x/2 - dp(17), self.window_y/2  - dp(17)) 

        else:

            self.graph_position = self.initial_graph_position = self.gui_manager.config_variables_dict["stored_connections"][self.current_connection_key]["graph_position"]
            self.mercator_position = self.initial_mercator_position = self.gui_manager.config_variables_dict["stored_connections"][self.current_connection_key]["mercator_position"]



            
        if self.gui_manager.graph:
            self.my_computer.icon_scatter_widget.pos = self.my_computer.graph_position
        else:
            self.my_computer.icon_scatter_widget.pos = self.my_computer.mercator_position



    def graph_display(self, slider: Slider, slider_value: float) -> None:

        """
        Display Country, City and IP widgets in graph view using sliders.
        """


        if self.country_checkbox.active == True:
            
            # Get value from GUI slider and store value for calculation
            if slider.id == "radius":
                self.country_radius = dp(slider_value)
                self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"

            elif slider.id == "angle":
                self.country_angle = slider_value
                self.angle_label.text = f"\nAngle\n {self.angle_slider.value:.0f}"

            elif slider.id == "phase":
                self.country_phase = slider_value
                self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"


            # Convert to radians
            radian_country_angle = self.country_angle * (pi / 180)
            radian_country_phase = self.country_phase * (pi / 180)
            
            # Prevent division by zero error
            if self.gui_manager.country_total_count == 0: 
                angle_slice = radian_country_angle / 1 
            else:
                angle_slice = radian_country_angle / self.gui_manager.country_total_count


            for n, country in enumerate(self.gui_manager.country_dictionary):

                country_widget = self.gui_manager.country_dictionary[country][0]

                if country_widget.exempt == True or country_widget.show == False:
                    continue

                country_angle_x = cos( angle_slice * (n + 1) + radian_country_phase)
                country_angle_y = sin(angle_slice * (n + 1) + radian_country_phase)

                if self.exempt == True:

                    new_country_pos = [
                                        self.excempt_pos[0] + self.country_radius * country_angle_x,
                                        self.excempt_pos[1] + self.country_radius * country_angle_y,
                                      ]

                    my_computer_pos = self.excempt_pos

                else:

                    new_country_pos = [
                                        self.icon_scatter_widget.pos[0] + self.country_radius * country_angle_x,
                                        self.icon_scatter_widget.pos[1] + self.country_radius * country_angle_y,
                                      ]

                    my_computer_pos = self.icon_scatter_widget.pos

                if country_widget.exempt == True:
                    pass

                else:
                    # TODO TEST: Do I need to set position for both country widget icon and self.pos?
                    country_widget.pos = new_country_pos
                    country_widget.icon_scatter_widget.pos = new_country_pos

                    country_draw_angle = angle_between_points( my_computer_pos, country_widget.icon_scatter_widget.pos)

                country_widget.country_draw_angle = country_draw_angle

                country_widget.graph_display( slider, slider_value, from_my_computer=True)


        elif self.city_checkbox.active == True:

            if slider.id == "radius":
                self.city_radius = slider_value
                self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"

            elif slider.id == "angle":
                self.city_angle = slider_value
                self.angle_label.text = f"\nAngle\n {2*self.angle_slider.value:.0f}"

            elif slider.id == "phase":
                self.city_phase = slider_value
                self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"

            for n, country in enumerate(self.gui_manager.country_dictionary):

                country_widget = self.gui_manager.country_dictionary[country][0]

                if country_widget.exempt == True or country_widget.show == False:
                    continue

                country_widget.graph_display( slider, slider_value, from_my_computer=True, city=True)


        elif self.ip_checkbox.active == True:

            if slider.id == "radius":
                self.ip_radius = slider_value
                self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"

            elif slider.id == "angle":
                self.ip_angle = slider_value
                self.angle_label.text = f"\nAngle\n {2 * self.angle_slider.value:.0f}"

            elif slider.id == "phase":
                self.ip_phase = slider_value
                self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"

            for n, country in enumerate(self.gui_manager.country_dictionary):

                country_widget = self.gui_manager.country_dictionary[country][0]

                if country_widget.exempt == True or country_widget.show == False:
                    continue

                country_widget.graph_display(slider, slider_value, from_my_computer=True, ip=True)



    def toggle_country_widgets(self) -> None:

        """
        Toggle display of all Country widgets.
        """

        if self.show_country_widgets == True:

            self.show_country_widgets = False

            for country in self.gui_manager.country_dictionary:

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[country][0].show = False  # set toggle for country

                for city in self.gui_manager.country_dictionary[country][1]:

                    if ( self.gui_manager.country_dictionary[country][1][city][0].exempt == True ):
                        continue

                    self.gui_manager.country_dictionary[country][1][city][0].show_ip_widgets = False  # set toggle for citys

                    for ip in self.gui_manager.country_dictionary[country][1][city]:
                        if ip.exempt == True:
                            continue

                        ip.show = False

        else:  # self.show_country_widgets == False

            self.show_country_widgets = True

            for country in self.gui_manager.country_dictionary:

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[country][0].show = True



    def toggle_city_widgets(self) -> None:

        """
        Toggle display of all City widgets.
        """

        if self.show_city_widgets == True:

            self.show_city_widgets = False

            for country in self.gui_manager.country_dictionary:

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[country][0].show = True
                self.gui_manager.country_dictionary[country][0].show_city_widgets = True

                for city in self.gui_manager.country_dictionary[country][1]:

                    if (self.gui_manager.country_dictionary[country][1][city][0].exempt == True):
                        continue

                    self.gui_manager.country_dictionary[country][1][city][0].show = True

        else:  # self.show_city_widgets == False

            self.show_city_widgets = True

            for country in self.gui_manager.country_dictionary:

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[country][0].show_city_widgets = False

                for city in self.gui_manager.country_dictionary[country][1]:

                    if (self.gui_manager.country_dictionary[country][1][city][0].exempt == True):
                        continue

                    self.gui_manager.country_dictionary[country][1][city][0].show = False

                    for ip in self.gui_manager.country_dictionary[country][1][city]:

                        if ip.exempt == True:
                            continue

                        ip.show = False



    def toggle_ip_widgets(self) -> None:

        """
        Toggle display of Country, City and IP widgets.
        """

        if self.show_ip_widgets == True:

            self.show_ip_widgets = False
            for country in self.gui_manager.country_dictionary:

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[country][0].show_ip_widgets = False  # set toggle for country

                for city in self.gui_manager.country_dictionary[country][1]:

                    if (self.gui_manager.country_dictionary[country][1][city][0].exempt == True):
                        continue

                    self.gui_manager.country_dictionary[country][1][city][0].show_ip_widgets = False  # set toggle for city

                    for ip in self.gui_manager.country_dictionary[country][1][city][1:]:

                        if ip.exempt == True:
                            continue

                        ip.show = False

        else:

            self.show_ip_widgets = True
            for country in self.gui_manager.country_dictionary:

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

        
                self.gui_manager.country_dictionary[country][0].show = True
                self.gui_manager.country_dictionary[country][0].show_city_widgets = True  # set toggle for country
                self.gui_manager.country_dictionary[country][0].show_ip_widgets = True  # set toggle for country

                for city in self.gui_manager.country_dictionary[country][1]:

                    if (self.gui_manager.country_dictionary[country][1][city][0].exempt == True ):
                        continue

                    self.gui_manager.country_dictionary[country][1][city][0].show_ip_widgets = True  # set toggle for city

                    for ip in self.gui_manager.country_dictionary[country][1][city]:

                        if ip.exempt == True:
                            continue

                        ip.show = True



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



    def toggle_country_labels(self) -> None:

        """
        Toggles Country Widget labels on/off
        """

        if self.country_labels == False:

            for country in self.gui_manager.country_dictionary.keys():

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                try:
                    self.gui_manager.country_dictionary[country][0].icon_scatter_widget.add_widget( self.gui_manager.country_dictionary[country][0].label )
                except:
                    pass

            self.country_labels = True
            self.gui_manager.country_labels = True

            

        else:  # self.country_labels == True

            for country in self.gui_manager.country_dictionary.keys():

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                try:
                    self.gui_manager.country_dictionary[country][0].icon_scatter_widget.remove_widget( self.gui_manager.country_dictionary[country][0].label )
                except:
                    pass

            self.country_labels = False
            self.gui_manager.country_labels = False

            



    def toggle_city_labels(self) -> None:

        """
        Toggles City widget labels on/off
        """

        if self.city_labels == False:

            for country in self.gui_manager.country_dictionary.keys():

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                for city in self.gui_manager.country_dictionary[country][1]:

                    if ( self.gui_manager.country_dictionary[country][1][city][0].exempt == True ):
                        continue

                    city_widget = self.gui_manager.country_dictionary[country][1][city][0]

                    if city_widget.exempt == True:
                        continue

                    try:
                        city_widget.icon_scatter_widget.add_widget(city_widget.label)
                    except:
                        pass

            self.city_labels = True
            self.gui_manager.city_labels = True

        else:  # self.city_labels == True

            for country in self.gui_manager.country_dictionary.keys():

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                for city in self.gui_manager.country_dictionary[country][1]:

                    if ( self.gui_manager.country_dictionary[country][1][city][0].exempt == True ):
                        continue

                    city_widget = self.gui_manager.country_dictionary[country][1][city][0]

                    if city_widget.exempt == True:
                        continue

                    try:
                        city_widget.icon_scatter_widget.remove_widget(city_widget.label)
                    except:
                        pass

            self.city_labels = False
            self.gui_manager.city_labels = False


            



    def toggle_ip_labels(self) -> None:

        """
        Toggles IP Widget labels on/off
        """

        if self.ip_labels == False:

            for country in self.gui_manager.country_dictionary.keys():

                if (self.gui_manager.country_dictionary[country][0].exempt == True):
                    continue

                for city in self.gui_manager.country_dictionary[country][1]:

                    if ( self.gui_manager.country_dictionary[country][1][city][0].exempt == True):
                        continue

                    for ip in self.gui_manager.country_dictionary[country][1][city][1:]:

                        if ip.exempt == True:
                            continue

                        try:
                            ip.icon_scatter_widget.add_widget(ip.label)
                        except:
                            pass

            self.ip_labels = True
            self.gui_manager.ip_labels = True

            

        else:  # self.ip_labels == True

            for country in self.gui_manager.country_dictionary.keys():

                if self.gui_manager.country_dictionary[country][0].exempt == True:
                    continue

                for city in self.gui_manager.country_dictionary[country][1]:

                    if ( self.gui_manager.country_dictionary[country][1][city][0].exempt == True ):
                        continue

                    for ip in self.gui_manager.country_dictionary[country][1][city][1:]:

                        if ip.exempt == True:
                            continue

                        try:
                            ip.icon_scatter_widget.remove_widget(ip.label)
                        except:
                            pass

            self.ip_labels = False
            self.gui_manager.ip_labels = False

            



    def activated_checkbox(self, activated_checkbox, value) -> None:

        """
        Set active mode (country, city, or ip) for GUI display sliders
        """

        if activated_checkbox.id == "country":

            self.radius_slider.value = self.country_radius
            self.angle_slider.value = self.country_angle
            self.phase_slider.value = self.country_phase

        elif activated_checkbox.id == "city":

            self.radius_slider.value = self.city_radius
            self.angle_slider.value = self.city_angle
            self.phase_slider.value = self.city_phase

        elif activated_checkbox.id == "ip":

            self.radius_slider.value = self.ip_radius
            self.angle_slider.value = self.ip_angle
            self.phase_slider.value = self.ip_phase

        self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"
        self.angle_label.text = f"\nAngle\n {self.angle_slider.value:.0f}"
        self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"



    def modify_slider_bounds(self, key) -> None:

        """
        Modify slider max values for GUI display
        """

        if key == "radius":
            self.radius_slider.max *= 2

            for country in self.gui_manager.country_dictionary.keys():
                self.gui_manager.country_dictionary[country][0].radius_slider.max *= 2

                for city in self.gui_manager.country_dictionary[country][1]:
                    self.gui_manager.country_dictionary[country][1][city][0].radius_slider.max *= 2

        elif key == "angle":
            self.angle_slider.max *= 2

            for country in self.gui_manager.country_dictionary.keys():
                self.gui_manager.country_dictionary[country][0].angle_slider.max *= 2

                for city in self.gui_manager.country_dictionary[country][1]:
                    self.gui_manager.country_dictionary[country][1][city][0].angle_slider.max *= 2

        elif key == "phase":
            self.phase_slider.max *= 2

            for country in self.gui_manager.country_dictionary.keys():
                self.gui_manager.country_dictionary[country][0].phase_slider.max *= 2

                for city in self.gui_manager.country_dictionary[country][1]:
                    self.gui_manager.country_dictionary[country][1][city][0].phase_slider.max *= 2


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
        Convience function to create display menu
        """

        grid_layout = GridLayout(cols=2, size_hint=(None, None), size=(dp(300), dp(220)), pos=(dp(10), dp(0)))
        right_col_layout = BoxLayout(orientation="vertical", size_hint_x=1)
        left_col_layout = BoxLayout(orientation="vertical", size_hint_y=1, size_hint_x=1)
        slider_container = GridLayout(cols=3)

        self.menu_popup = Scatter()
        self.menu_popup.size_hint = (None, None)
        self.menu_popup.size = (dp(320), dp(225))
        self.menu_popup.id = "myComputer"

        self.menu_popup.pos = self.icon_scatter_widget.pos

        with self.menu_popup.canvas.before:

            Color(0.1, 0.1, 0.1, 0.8)
            RoundedRectangle(
                            size=self.menu_popup.size,
                            pos=(0, 0),
                            radius=[(20, 20), (20, 20), (20, 20), (20, 20)],
                            )

        if self.menu_popup.pos[0] + dp(300) > self.window_x:
            self.menu_popup.pos = (self.window_x - dp(350), self.menu_popup.pos[1])

        if self.menu_popup.pos[1] + dp(250) > self.window_y:
            self.menu_popup.pos = (self.menu_popup.pos[0], self.window_y - dp(280))

        increase_radius_button = Button(text="+", size_hint_y=1)
        increase_radius_button.on_press = (lambda key="radius": self.modify_slider_bounds(key))
        increase_radius_button.font_size = sp(10)
        increase_radius_button.background_color = (0.3, 0.3, 0.3, 0.9)
        increase_radius_button.background_down = ""
        increase_radius_button.size_hint_x = 0.2
        increase_radius_button.size_hint_y = 0.3

        increase_angle_button = Button(text="+", size_hint_y=1)
        increase_angle_button.on_press = lambda key="angle": self.modify_slider_bounds(key)
        increase_angle_button.font_size = sp(10)
        increase_angle_button.background_color = (0.3, 0.3, 0.3, 0.9)
        increase_angle_button.background_down = ""
        increase_angle_button.size_hint_x = 0.2
        increase_angle_button.size_hint_y = 0.3

        increase_phase_button = Button(text="+", size_hint_y=1)
        increase_phase_button.on_press = lambda key="phase": self.modify_slider_bounds(key)
        increase_phase_button.font_size = sp(10)
        increase_phase_button.background_color = (0.3, 0.3, 0.3, 0.9)
        increase_phase_button.background_down = ""
        increase_phase_button.size_hint_x = 0.2
        increase_phase_button.size_hint_y = 0.3

        self.radius_slider = Slider()
        self.radius_slider.id = "radius"
        self.radius_slider.value_track = False
        self.radius_slider.min = -self.window_x / 2
        self.radius_slider.max = self.window_x / 2
        self.radius_slider.value = 200
        self.radius_slider.orientation = "vertical"
        self.radius_slider.bind(value=self.graph_display)

        self.radius_label = Label(
                                text=f"\nRadius\n {self.radius_slider.value:.0f}",
                                halign="center",
                                valign="middle",
                                )
        self.radius_label.size_hint_y = 1
        self.radius_label.size_hint_x = 0.8

        radius_label_container = BoxLayout(orientation="horizontal", size_hint_y=0.2)

        radius_label_container.add_widget(self.radius_label)
        radius_label_container.add_widget(increase_radius_button)
        radius_label_container.add_widget(Label(size_hint_x=0.3))

        slider_container.add_widget(radius_label_container)

        self.angle_slider = Slider()
        self.angle_slider.id = "angle"
        self.angle_slider.value_track = False
        self.angle_slider.min = -360
        self.angle_slider.max = 360
        self.angle_slider.value = 360
        self.angle_slider.orientation = "vertical"
        self.angle_slider.bind(value=self.graph_display)

        self.angle_label = Label(
                                text=f"\nAngle\n {self.angle_slider.value:.0f}",
                                halign="center",
                                valign="middle",
                                )
        self.angle_label.size_hint_y = 1
        self.angle_label.size_hint_x = 0.8

        angle_label_container = BoxLayout(orientation="horizontal", size_hint_y=0.2)
        angle_label_container.add_widget(self.angle_label)
        angle_label_container.add_widget(increase_angle_button)
        angle_label_container.add_widget(Label(size_hint_x=0.3))
        slider_container.add_widget(angle_label_container)

        self.phase_slider = Slider()
        self.phase_slider.id = "phase"
        self.phase_slider.value_track = False
        self.phase_slider.min = -720
        self.phase_slider.max = 720
        self.phase_slider.value = 0
        self.phase_slider.orientation = "vertical"
        self.phase_slider.bind(value=self.graph_display)

        self.phase_label = Label(
                                text=f"\nSpin\n {self.phase_slider.value:.0f}",
                                halign="center",
                                valign="middle",
                                )
        self.phase_label.size_hint_y = 1
        self.phase_label.size_hint_x = 0.8

        phase_label_container = BoxLayout(orientation="horizontal", size_hint_y=0.2)
        phase_label_container.add_widget(self.phase_label)
        phase_label_container.add_widget(increase_phase_button)
        phase_label_container.add_widget(Label(size_hint_x=0.3))
        slider_container.add_widget(phase_label_container)

        self.country_checkbox = CheckBox()
        self.country_checkbox.id = "country"
        self.country_checkbox.group = "my_computer"
        self.country_checkbox.bind(active=self.activated_checkbox)
        self.country_checkbox.allow_no_selection = False
        self.country_checkbox.active = True
        self.country_checkbox.background_radio_normal = os.path.join( self.resource_path, "assets/images/UI/white_circle.png")

        self.city_checkbox = CheckBox()
        self.city_checkbox.id = "city"
        self.city_checkbox.group = "my_computer"
        self.city_checkbox.bind(active=self.activated_checkbox)
        self.city_checkbox.allow_no_selection = False
        self.city_checkbox.background_radio_normal = os.path.join(self.resource_path, "assets/images/UI/white_circle.png")

        self.ip_checkbox = CheckBox()
        self.ip_checkbox.id = "ip"
        self.ip_checkbox.group = "my_computer"
        self.ip_checkbox.bind(active=self.activated_checkbox)
        self.ip_checkbox.allow_no_selection = False
        self.ip_checkbox.background_radio_normal = os.path.join(self.resource_path, "assets/images/UI/white_circle.png")

        checkbox_container1 = BoxLayout(orientation="horizontal", size_hint_y=0.8)
        checkbox_container2 = BoxLayout(orientation="horizontal", size_hint_y=0.8)
        checkbox_container3 = BoxLayout(orientation="horizontal", size_hint_y=0.8)

        self.total_cities_label = Label(
                                        text="[b][color=ff1919]0[/color][/b]",
                                        markup=True,
                                        )
        self.total_ip_label = Label(
                                    text=f"[b][color=ff1919]0[/color][/b]",
                                    markup=True,
                                   )

        self.total_countries_label = Label(
                                            text="[b][color=ff1919]0[/color][/b]",
                                            markup=True,
                                            )


        self.malicious_ip_count = Label(
                                        text=f"[color=FF0000] Detected Malicious IP's: [b]0[/b]",
                                        markup=True,
                                        font_size=sp(12),
                                        )

        self.total_data_out_label = Label(
                                        text="Data OUT (GB): [b][color=ff1919]0[/color][/b]",
                                        markup=True,
                                        font_size=sp(12),
                                        )

        self.total_data_in_label = Label(
                                        text="Data IN (GB): [b][color=ff1919]0[/color][/b]",
                                        markup=True,
                                        font_size=sp(12),
                                        )

        checkbox_container1.add_widget(self.total_countries_label)
        checkbox_container1.add_widget(Label(size_hint_x=0.2))
        checkbox_container1.add_widget(Label(text="Countries"))
        checkbox_container1.add_widget(self.country_checkbox)

        checkbox_container2.add_widget(self.total_cities_label)
        checkbox_container2.add_widget(Label(size_hint_x=0.2))
        checkbox_container2.add_widget(Label(text="Cities"))
        checkbox_container2.add_widget(self.city_checkbox)

        checkbox_container3.add_widget(self.total_ip_label)
        checkbox_container3.add_widget(Label(size_hint_x=0.2))
        checkbox_container3.add_widget(Label(text="IP's"))
        checkbox_container3.add_widget(self.ip_checkbox)

        toggle_countries = Button()
        toggle_countries.on_press = self.toggle_country_widgets
        toggle_countries.text = "Toggle Countries"
        toggle_countries.background_color = (.5, .5, .5, 0.8)
        toggle_countries.font_size = sp(12)
        toggle_countries.border = (0, 0, 0, 0)

        toggle_countries_label = Button()
        toggle_countries_label.on_press = self.toggle_country_labels
        toggle_countries_label.font_size = sp(8)
        toggle_countries_label.border = (0, 0, 0, 0)
        toggle_countries_label.size_hint_x = 0.1
        toggle_countries_label.background_normal =  os.path.join(self.resource_path, "assets/images/UI/tag.png")
        toggle_countries_label.background_down =  os.path.join(self.resource_path, "assets/images/UI/tag-down.png")

        toggle_cities = Button()
        toggle_cities.on_press = self.toggle_city_widgets
        toggle_cities.text = "Toggle Cities"
        toggle_cities.background_color = (.7, .7, .7, 0.8)
        toggle_cities.font_size = sp(12)
        toggle_cities.border = (0, 0, 0, 0)

        toggle_cities_label = Button()
        toggle_cities_label.on_press = self.toggle_city_labels

        toggle_cities_label.font_size = sp(8)
        toggle_cities_label.border = (0, 0, 0, 0)
        toggle_cities_label.size_hint_x = 0.1
        toggle_cities_label.background_normal =  os.path.join(self.resource_path, "assets/images/UI/tag.png")
        toggle_cities_label.background_down =  os.path.join(self.resource_path, "assets/images/UI/tag-down.png")

        toggle_ips = Button()
        toggle_ips.text = "Toggle IP's"
        toggle_ips.on_press = self.toggle_ip_widgets
        toggle_ips.background_color = (.9, .9, .9, 0.8) 
        toggle_ips.font_size = sp(12)
        toggle_ips.border = (0, 0, 0, 0)

        toggle_ips_label = Button()
        toggle_ips_label.on_press = self.toggle_ip_labels
        toggle_ips_label.font_size = sp(8)
        toggle_ips_label.border = (0, 0, 0, 0)
        toggle_ips_label.size_hint_x = 0.1
        toggle_ips_label.background_normal =  os.path.join(self.resource_path, "assets/images/UI/tag.png")
        toggle_ips_label.background_down =  os.path.join(self.resource_path, "assets/images/UI/tag-down.png")

        toggle_label = Button()
        toggle_label.on_press = self.toggle_my_label
        toggle_label.font_size = sp(15)
        toggle_label.text = "My Computer"
        toggle_label.background_color = (0.3, 0.3, 0.3, 0.8)
        toggle_label.background_down = os.path.join(self.resource_path, "assets/images/buttons/black.png")

        self.exempt_button = Button()
        self.exempt_button.on_press = self.toggle_exempt
        self.exempt_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/kivy-teal-4.png")
        self.exempt_button.background_down = os.path.join(self.resource_path, "assets/images/buttons/teal_down.png")
        self.exempt_button.size_hint_x = 1.1
        self.exempt_button.border = (0, 0, 0, 0)
        self.exempt_button.font_size = sp(12)

        self.exempt_button.text = "Exempt" if self.exempt else "Not Exempt"

        self.mercator_button = Button()
        self.mercator_button.text = "World"
        self.mercator_button.on_press = self.toggle_mercator
        self.mercator_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/mercator-opacity.png")
        self.mercator_button.background_down = os.path.join(self.resource_path, "assets/images/buttons/mercator-opacity.png")
        self.mercator_button.size_hint_x = 1.1
        self.mercator_button.border = (0, 0, 0, 0)
        self.mercator_button.font_size = sp(12)

        reset_position_button = Button()
        reset_position_button.on_press = self.reset_position
        reset_position_button.font_size = sp(8)
        reset_position_button.border = (0,0,0,0)
        reset_position_button.size_hint_x = 0.12
        reset_position_button.background_normal = os.path.join(self.resource_path, "assets/images/UI/reset.png")
        reset_position_button.background_down = os.path.join(self.resource_path, "assets/images/UI/reset-down.png")


        dismiss_button = Button()
        dismiss_button.text = "Dismiss"
        dismiss_button.background_color = [0.3, 0.3, 0.3, 0.8]
        dismiss_button.font_size = sp(12)
        dismiss_button.bind(on_press=self.toggle_menu)
        dismiss_button.size_hint_y = 0.8
        dismiss_button.border = (0, 0, 0, 0)

        label_container = BoxLayout(orientation="horizontal", size_hint_x=1, size_hint_y=1)

        # Construct Menu
        label_container.add_widget(Label(size_hint_x=0.25))
        label_container.add_widget(toggle_label)
        label_container.add_widget(Label(size_hint_x=0.25))

        left_col_layout.add_widget(label_container)
        left_col_layout.add_widget(Label(size_hint_y=0.3))
        left_col_layout.add_widget(checkbox_container3)
        left_col_layout.add_widget(checkbox_container2)
        left_col_layout.add_widget(checkbox_container1)
        left_col_layout.add_widget(Label(size_hint_y=0.3))

        sum_data_container = BoxLayout(orientation="vertical", size_hint_y=2.2)
        sum_data_container.add_widget(self.malicious_ip_count)
        sum_data_container.add_widget(Label(size_hint_y=0.5))
        sum_data_container.add_widget(self.total_data_in_label)
        sum_data_container.add_widget(self.total_data_out_label)

        left_col_layout.add_widget(sum_data_container)
        left_col_layout.add_widget(Label(size_hint_y=0.3))

        ip_container = BoxLayout(orientation="horizontal", size_hint_y=0.8)
        ip_container.add_widget(toggle_ips)
        ip_container.add_widget(toggle_ips_label)

        left_col_layout.add_widget(ip_container)
        left_col_layout.add_widget(Label(size_hint_y=0.1))

        cities_container = BoxLayout(orientation="horizontal", size_hint_y=0.8)
        cities_container.add_widget(toggle_cities)
        cities_container.add_widget(toggle_cities_label)

        left_col_layout.add_widget(cities_container)
        left_col_layout.add_widget(Label(size_hint_y=0.1))

        countries_container = BoxLayout(orientation="horizontal", size_hint_y=0.8)
        countries_container.add_widget(toggle_countries)
        countries_container.add_widget(toggle_countries_label)

        left_col_layout.add_widget(countries_container)
        left_col_layout.add_widget(Label(size_hint_y=0.1))

        mercator_container = BoxLayout(orientation="horizontal", size_hint_y=0.75)
        mercator_container.add_widget(Label(size_hint_x=0.04))
        mercator_container.add_widget(self.mercator_button)
        mercator_container.add_widget(Label(size_hint_x=0.05))
        mercator_container.add_widget(reset_position_button)

        left_col_layout.add_widget(mercator_container)
        left_col_layout.add_widget(Label(size_hint_y=0.1))
        left_col_layout.add_widget(Label(size_hint_y=0.1))

        exempt_container = BoxLayout(orientation="horizontal", size_hint_y=0.75)
        exempt_container.add_widget(Label(size_hint_x=0.05))
        exempt_container.add_widget(self.exempt_button)
        exempt_container.add_widget(Label(size_hint_x = 0.175))

        left_col_layout.add_widget(exempt_container)

        dismiss_container = BoxLayout(orientation="horizontal", size_hint_x=1, size_hint_y=1)
        dismiss_container.add_widget(Label(size_hint_y=0.5))
        dismiss_container.add_widget(dismiss_button)
        dismiss_container.add_widget(Label(size_hint_y=0.5))

        left_col_layout.add_widget(dismiss_container)
        left_col_layout.add_widget(Label(size_hint_y=0.1))

        slider_container.add_widget(Label(size_hint_y=0.05))
        slider_container.add_widget(Label(size_hint_y=0.05))
        slider_container.add_widget(Label(size_hint_y=0.05))
        slider_container.add_widget(self.radius_slider)
        slider_container.add_widget(self.angle_slider)
        slider_container.add_widget(self.phase_slider)

        right_col_layout.add_widget(slider_container)

        grid_layout.add_widget(left_col_layout)
        grid_layout.add_widget(right_col_layout)
        self.menu_popup.add_widget(grid_layout)


    


    def reset_position(self) -> None:

        """
        Reset position for graph/mercator widgets
        """

        if self.gui_manager.graph == True:

            if not self.exempt:
                self.icon_scatter_widget.pos = self.initial_graph_position

            for country in self.gui_manager.country_dictionary:

                country_widget = self.gui_manager.country_dictionary[country][0]

                if country_widget.exempt:
                    continue

                country_widget.icon_scatter_widget.pos = country_widget.initial_graph_position

                for city in self.gui_manager.country_dictionary[country][1]:

                    city_widget = self.gui_manager.country_dictionary[country][1][city][0]

                    if city_widget.exempt:
                        continue

                    city_widget.icon_scatter_widget.pos = city_widget.initial_graph_position

                    # TODO:
                    # city_widget.set_graph_inital_position()

        else:  # self.gui_manager.graph == False

            if not self.exempt:
                self.icon_scatter_widget.pos = self.initial_mercator_position

            for country in self.gui_manager.country_dictionary:

                country_widget = self.gui_manager.country_dictionary[country][0]

                if country_widget.exempt:
                    continue

                country_widget.icon_scatter_widget.pos = country_widget.initial_mercator_position
                

                for city in self.gui_manager.country_dictionary[country][1]:
                    city_widget = self.gui_manager.country_dictionary[country][1][city][0]

                    if city_widget.exempt:
                        continue

                    city_widget.icon_scatter_widget.pos = city_widget.initial_mercator_position
                    city_widget.position_ips()



    def toggle_mercator(self, *args) -> None:

        if self.gui_manager.graph == False:

            self.mercator_button.text = "World"
            self.mercator_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/mercator-opacity.png")

            Clock.unschedule(self.gui_manager.update_mercator_particles)

            self.set_graph_layout()

            self.gui_manager.graph_view.remove_widget(self.gui_manager.mercator_container)

            for country in self.gui_manager.country_dictionary:

                country_widget = self.gui_manager.country_dictionary[country][0]

                if country_widget.exempt:
                    continue

                country_widget.set_graph_layout()
                country_widget.toggle_ip_widgets_on()

                for city in self.gui_manager.country_dictionary[country][1]:

                    city_widget = self.gui_manager.country_dictionary[country][1][city][0]

                    if city_widget.exempt:
                        continue

                    city_widget.set_graph_layout()

                    for ip_widget in self.gui_manager.country_dictionary[country][1][city][1:]:

                        if ip_widget.exempt == True:
                            continue

                        ip_widget.set_graph_layout()

            self.gui_manager.graph = True

        else: #self.gui_manager.graph == True

            if not self.exempt:
                self.set_mercator_layout()

            self.mercator_button.text = "Graph"
            self.mercator_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/black.png")

            Clock.schedule_interval(self.gui_manager.update_mercator_particles, 1)

            self.gui_manager.graph_view.add_widget(self.gui_manager.mercator_container, len(self.gui_manager.graph_view.children) + 1)

            for country in self.gui_manager.country_dictionary:

                country_widget = self.gui_manager.country_dictionary[country][0]

                if country_widget.exempt:
                    continue

                country_widget.set_mercator_layout()
                country_widget.toggle_ip_widgets_off()


                for city in self.gui_manager.country_dictionary[country][1]:
                    city_widget = self.gui_manager.country_dictionary[country][1][city][0]

                    if city_widget.exempt:
                        continue

                    city_widget.set_mercator_layout()

                    for n, ip_widget in enumerate(self.gui_manager.country_dictionary[country][1][city][1:]):  # access relevant IP widgets

                        if ip_widget.exempt == True:
                            continue

                        ip_widget.set_mercator_layout()

            self.gui_manager.graph = False
 



    def toggle_menu(self, *args):

        """
        Toggle menu when user clicks on Computer Widget.
        """

        if self.menu_boolean == False:

            self.gui_manager.persistent_widget_container.add_widget(self.menu_popup)
            self.gui_manager.misc_update_dictionary["my_computer"] = self
            self.menu_boolean = True

        elif self.menu_boolean == True:

            self.gui_manager.persistent_widget_container.remove_widget(self.menu_popup)
            self.gui_manager.misc_update_dictionary["my_computer"] = None
            self.menu_boolean = False



    def set_mercator_layout(self) -> None:

        """ 
        Called on transition to mercator view (world map)
        """

        self.graph_position = self.icon_scatter_widget.pos

        self.icon_scatter_widget.pos = self.mercator_position

        self.icon_image.size = (dp(15), dp(15))
        self.icon_image.pos = (dp(10), dp(10))

        self.display_menu_button.size = (dp(12), dp(12))
        self.display_menu_button.pos = (dp(10), dp(10))

        with self.icon_scatter_widget.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)
            RoundedRectangle(
                                size=(dp(35), dp(35)),
                                pos=(0, 0),
                                radius=[
                                    (dp(60), dp(50)),
                                    (dp(50), dp(50)),
                                    (dp(50), dp(50)),
                                    (dp(50), dp(50)),
                                    ]
                            )

        

    def set_graph_layout(self) -> None:

        """
        Called on transition to graph view (black background with nodes and edges)
        """

        self.mercator_position = self.icon_scatter_widget.pos

        self.icon_scatter_widget.pos = self.graph_position
        self.icon_scatter_widget.size = (dp(35), dp(35))

        self.icon_image.size = (dp(25), dp(25))
        self.icon_image.pos = (dp(5), dp(6))

        self.display_menu_button.size = (dp(20), dp(20))
        self.display_menu_button.pos = (dp(8), dp(8))



    def update(self, **kwargs) -> None:

        """
        Update Computer Widget. Called every cycle.
        """
        
        pass