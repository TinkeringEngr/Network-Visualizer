# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.


from math import sin, cos, pi, floor
import os
import time
import sys
sys.path.append("..") 

from utilities.utils import (
                            map_to_range,
                            distance_between_points,
                            angle_between_points,
                            Country_Icon_Scatter_Override,
                            )

from kivy.graphics import Color, Line, RoundedRectangle, InstructionGroup
from kivy.metrics import sp, dp
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.scatter import Scatter
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.checkbox import CheckBox
from kivy.properties import NumericProperty


class Country_Widget(Widget):

    """
    GUI Widget for each geographic Country with member functions for displaying associated City and IP widgets.
    """

    def __init__(self, **kwargs):

        """
        Construct GUI widget and associated state.
        """

        super().__init__()

        self.screen_x = kwargs["screen_x"]
        self.screen_y = kwargs["screen_y"]

        self.window_center_x = kwargs["center_x"]
        self.center_y = kwargs["center_y"]
        self.window_x = kwargs["window_x"]
        self.window_y = kwargs["window_y"]
        self.country = kwargs["country"]
        self.country_code = kwargs["country_code"].lower()
        self.gui_manager = kwargs["gui_manager"]

        self.resource_path = kwargs["resource_path"]

        self.pos = (self.screen_x, self.screen_y)
        self.old_pos = self.pos
        self.spring_constant_k = 0.07
        self.draw_angle = 0
        self.city_total_count = 1
        self.ip_total_count = 1
        self.total_data_in = 1
        self.total_data_out = 1

        self.new_packet_timestamp = time.time()

        self.city_phase = 0
        self.city_radius = dp(50)
        self.city_angle = 60

        self.ip_phase = 0
        self.ip_radius = dp(100)
        self.ip_angle = 60

        if self.gui_manager.country_labels == True:
            self.mylabel_bool = True
        else:
            self.mylabel_bool = False

        if self.gui_manager.city_labels == True:
            self.city_labels = True
        else:
            self.city_labels = False

        if self.gui_manager.ip_labels == True:
            self.ip_labels = True
        else:
            self.ip_labels = False


        self.ip_labels = True if self.gui_manager.ip_labels == True else False

        self.show_city_widgets = True
        self.show_ip_widgets = True

        self.last_packet = "TCP"

        self.exempt = False
        self.menu_boolean = False
        self.attach = True
        self.show = True
        self.mercator_show = True
        self.new_data = True

        ##Create GUI widgets
        self.label = Label()
        self.label.text = self.country
        self.label.pos = (dp(-10), dp(13))
        self.label.font_size = sp(15)

        self.container = FloatLayout()
        self.container.pos = self.pos
        self.container.size_hint = (None, None)
        self.container.size = (dp(50), dp(50))

        self.icon_image = Image()
        self.icon_image.source = os.path.join(self.resource_path, f"assets/images/country_icons/{self.country}.png")
        self.icon_image.size_hint = (None, None)
        self.icon_image.size = (dp(20), dp(20))
        self.icon_image.pos = (dp(5), dp(5))

        self.display_menu_button = Button()
        self.display_menu_button.size_hint = (None, None)
        self.display_menu_button.background_color = (1, 1, 1, 0)
        self.display_menu_button.pos = (dp(7), dp(6))
        self.display_menu_button.size = (dp(17), dp(17))
        self.display_menu_button.on_press = self.toggle_menu


        self.icon_scatter_widget = Country_Icon_Scatter_Override()

        self.icon_scatter_widget.size = (dp(30), dp(30))
        self.icon_scatter_widget.size_hint = (None, None)
        self.icon_scatter_widget.parent_widget = self

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

    

        self.container.add_widget(self.icon_scatter_widget)
        

        self.display_menu_button.add_widget(self.icon_image)
        self.icon_scatter_widget.add_widget(self.display_menu_button)
        

        if self.mylabel_bool == True:
            self.icon_scatter_widget.add_widget(self.label)

        self.add_widget(self.container)


        # with self.icon_scatter_widget.canvas.before:
        #     Color(1, 1, 1, 0.2)
        #     RoundedRectangle(
        #                     size=(dp(30), dp(30)),
        #                     pos=(0, 0),
        #                     radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
        #                     )

        # self.default_widget_halo_instruction_group = InstructionGroup()  
        # self.default_widget_halo_instruction_group.add(Color(rgba = self.gui_manager.config_variables_dict["color_dictionary"]["Widget Halo Color"].copy()))
        # self.default_widget_halo_instruction_group.add(  RoundedRectangle(
        #                                         size=self.icon_scatter_widget.size,
        #                                         pos=(0, 0),
        #                                         radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
        #                                         )  
        #                      )

        # self.exempt_instruction_group = InstructionGroup()
        # self.exempt_instruction_group.add(Color(rgba = self.gui_manager.config_variables_dict["color_dictionary"]["Exempt Color"].copy()))
        # self.exempt_instruction_group.add(  RoundedRectangle(
        #                                         size=self.icon_scatter_widget.size,
        #                                         pos=(0, 0),
        #                                         radius=[(50, 50), (50, 50), (50, 50), (50, 50)],
        #                                         )  
        #                      )

        # Mercator view attributes
        self.intial_layout = False
        self.labels = False
        self.mercator_position = self.initalize_mercator_position(kwargs["country_index"])
        self.initial_mercator_position = self.mercator_position

        # Graph view attributes
        self.graph_state = "graph"
        self.graph_position = self.pos
        self.initial_graph_position = self.graph_position
        self.icon_scatter_widget.pos = (self.screen_x, self.screen_y)

        self.menu_popup = None #Populated by self.make_display_menu
        self.make_display_menu()

        if kwargs["graph_state"] == False:
            self.icon_scatter_widget.pos = self.mercator_position
            self.pos = self.mercator_position



    def position_cities(self, *args) -> None:

        """
        Position City Widgets when Country Scatter Widget is drag/dropped
        """

        radian_city_angle = pi # Use PI instead of 2PI for a circle because angle is calculated +/- in calculate_city_positions() 
        radian_city_phase = 0
        radian_ip_angle = pi/9
        radian_ip_phase = 0

        for i, city in enumerate(self.gui_manager.active_cities[self.country].keys()):

            city_widget = self.gui_manager.city_dictionary[self.country][city]

            if city_widget.show == False or city_widget.exempt == True:
                continue

            country_pos = self.excempt_pos if self.exempt == True else self.icon_scatter_widget.pos

            ip_draw_angle = angle_between_points( country_pos, city_widget.icon_scatter_widget.pos )
            city_total_count = len( self.gui_manager.active_cities[self.country].keys() )
            total_city_ip_count = len( self.gui_manager.active_ips[self.country][city] )

            if total_city_ip_count == 0:
                total_city_ip_count = 1 

            city_x, city_y = self.calculate_city_positions(
                                                            i,
                                                            city_total_count,
                                                            radian_city_angle,
                                                            self.city_radius,
                                                            radian_city_phase,
                                                          )

            angle_slice = radian_ip_angle / total_city_ip_count
            city_widget.pos = (country_pos[0] + city_x, country_pos[1] + city_y)
            city_widget.icon_scatter_widget.pos = city_widget.pos

            for n, ip in enumerate( self.gui_manager.country_dictionary[self.country][1][city][1:] ):

                if ip.show == False or ip.exempt == True:
                    continue

                if n % 2 == 0:
                    n *= -1

                final_position = [
                                  city_widget.pos[0] + self.ip_radius * cos(ip_draw_angle + radian_ip_phase + angle_slice * n),
                                  city_widget.pos[1] + self.ip_radius * sin(ip_draw_angle + radian_ip_phase + angle_slice * n),
                                 ]

                ip.pos = final_position
                ip.icon_scatter_widget.pos = ip.pos



    def graph_display(
                        self,
                        slider: Slider,
                        slider_value: float,
                        from_my_computer=False,
                        city=False,
                        ip=False,
                     ) -> None:

        """
        Display associated City and IP widgets in a circle.
        """

        if from_my_computer == True:

            if city == True:

                if slider.id == "radius":
                    self.city_radius = dp(slider_value)
                    self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"
                
                elif slider.id == "angle":
                    self.city_angle = slider_value
                    self.angle_label.text = f"\nAngle\n {2 * self.angle_slider.value:.0f}"
                    
                elif slider.id == "phase":
                    self.city_phase = slider_value
                    self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"

            elif ip == True:

                if slider.id == "radius":
                    self.ip_radius = dp(slider_value)
                    self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"
                    
                elif slider.id == "angle":
                    self.ip_angle = slider_value
                    self.angle_label.text = f"\nAngle\n {self.angle_slider.value:.0f}"

                elif slider.id == "phase":
                    self.ip_phase = slider_value
                    self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"

        else:

            if self.city_checkbox.active == True:

                if slider.id == "radius":
                    self.city_radius = dp(slider_value)
                    self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"

                elif slider.id == "angle":
                    self.city_angle = slider_value
                    self.angle_label.text = f"\nAngle\n {self.angle_slider.value:.0f}"

                elif slider.id == "phase":
                    self.city_phase = slider_value
                    self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"

            elif self.ip_checkbox.active == True:

                if slider.id == "radius":
                    self.ip_radius = dp(slider_value)
                    self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"
                    
                elif slider.id == "angle":
                    self.ip_angle = slider_value
                    self.angle_label.text = f"\nAngle\n {self.angle_slider.value:.0f}"

                elif slider.id == "phase":
                    self.ip_phase = slider_value
                    self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"


        radian_city_angle = self.city_angle * (pi / 180)
        radian_city_phase = self.city_phase * (pi / 180)
        radian_ip_angle = self.ip_angle * (pi / 180)
        radian_ip_phase = self.ip_phase * (pi / 180)

        country = self.country

        for i, city in enumerate(self.gui_manager.active_cities[country].keys()):

            city_widget = self.gui_manager.city_dictionary[country][city]

            if city_widget.show == False or city_widget.exempt == True:
                continue

            if self.exempt == True:
                country_pos = self.excempt_pos

            else:
                country_pos = self.icon_scatter_widget.pos

            ip_draw_angle = angle_between_points( country_pos, city_widget.icon_scatter_widget.pos)

            # We do iterate twice. Can we draw city widget pos after IP? probably not. 
            total_city_ip_count = len( self.gui_manager.active_ips[country][city].keys() )

            if total_city_ip_count == 0:
                total_city_ip_count = 1
            
            city_x, city_y = self.calculate_city_positions(
                                                            i,
                                                            self.city_total_count + 1,
                                                            radian_city_angle,
                                                            self.city_radius,
                                                            radian_city_phase,
                                                          )

            angle_slice = radian_ip_angle / total_city_ip_count
            city_widget.pos = (country_pos[0] + city_x, country_pos[1] + city_y)
            city_widget.icon_scatter_widget.pos = city_widget.pos

            #for n, ip in enumerate( self.gui_manager.country_dictionary[self.country][1][city][1:]):
            for n, ip in enumerate( self.gui_manager.active_ips[country][city].keys() ):

                ip_widget = self.gui_manager.ip_dictionary[ip]

                if ip_widget.show == False or ip_widget.exempt == True:
                    continue

                if n % 2 == 0:
                    n *= -1

                final_position = [
                                    city_widget.pos[0] + self.ip_radius * cos(ip_draw_angle + radian_ip_phase + angle_slice * n),
                                    city_widget.pos[1] + self.ip_radius * sin(ip_draw_angle + radian_ip_phase + angle_slice * n),
                                 ]

                ip_widget.pos = final_position
                ip_widget.icon_scatter_widget.pos = ip_widget.pos



    def calculate_city_positions(
                                self,
                                ip_index: int,
                                total_count: int,
                                draw_angle: float,
                                radius: float,
                                phase: float,
                                ) -> tuple[float, float]:

        """
        Determine x, y position for City Widgets.
        """

        angle_slice = draw_angle / total_count

        if ip_index % 2 == 0:  # alternate +/-  city draw angle
            ip_index *= -1

        if ( ip_index % 4 == 0 or ip_index % 4 == 1):  # every other odd/even city increase radius by 2x
            radius *= 2

        x = radius * cos(self.country_draw_angle + phase + ip_index * angle_slice)
        y = radius * sin(self.country_draw_angle + phase + ip_index * angle_slice)

        return x, y



    def toggle_city_widgets(self) -> None:

        """
        Toggle display of City widgets and associated IP widgets.
        """

        if self.show_city_widgets == True:
            self.show_city_widgets = False

            for city in self.gui_manager.country_dictionary[self.country][1]:

                if self.gui_manager.country_dictionary[self.country][1][city][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[self.country][1][city][0].show = False
                self.gui_manager.country_dictionary[self.country][1][city][0].show_ip_widgets = False

                for ip in self.gui_manager.country_dictionary[self.country][1][city][1:]:

                    if ip.exempt == True:
                        continue

                    ip.show = False

        else:  # self.show_city_widgets = False

            self.show_city_widgets = True
            for city in self.gui_manager.country_dictionary[self.country][1]:

                if self.gui_manager.country_dictionary[self.country][1][city][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[self.country][1][city][0].show = True
                self.gui_manager.country_dictionary[self.country][1][city][0].show_ip_widgets = True





    def toggle_ip_widgets(self) -> None:

        """ 
        Toggle GUI display of IP Widgets
        """

        if self.show_ip_widgets == True:

            self.show_ip_widgets = False

            for city in self.gui_manager.country_dictionary[self.country][1]:

                if self.gui_manager.country_dictionary[self.country][1][city][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[self.country][1][city][0].show_ip_widgets = False

                for ip in self.gui_manager.country_dictionary[self.country][1][city][1:]:

                    if ip.exempt == True:
                        continue

                    ip.show = False

        else:

            self.show_ip_widgets = True
            for city in self.gui_manager.country_dictionary[self.country][1]:

                if self.gui_manager.country_dictionary[self.country][1][city][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[self.country][1][city][0].show = True
                self.gui_manager.country_dictionary[self.country][1][city][0].show_ip_widgets = True

                for ip in self.gui_manager.country_dictionary[self.country][1][city][1:]:

                    if ip.exempt == True:
                        continue

                    ip.show = True



    def toggle_ip_widgets_off(self) -> None:


        """ 
        Remove GUI IP Widgets
        """

        for city in self.gui_manager.country_dictionary[self.country][1]:

                if self.gui_manager.country_dictionary[self.country][1][city][0].exempt == True:
                    continue

                for ip in self.gui_manager.country_dictionary[self.country][1][city][1:]:

                    if ip.exempt == True:
                        continue

                    ip.show = False


    
    def toggle_ip_widgets_on(self) -> None:


        """ 
        Add GUI IP Widgets
        """

        for city in self.gui_manager.country_dictionary[self.country][1]:

                if self.gui_manager.country_dictionary[self.country][1][city][0].exempt == True:
                    continue

                self.gui_manager.country_dictionary[self.country][1][city][0].show = True

                for ip in self.gui_manager.country_dictionary[self.country][1][city][1:]:

                    if ip.exempt == True:
                        continue

                    ip.show = True




    def toggle_city_labels(self) -> None:

        """
        Toggles City widget labels on/off
        """

        if self.city_labels == True:

            for city in self.gui_manager.country_dictionary[self.country][1]:

                city_widget = self.gui_manager.country_dictionary[self.country][1][city][0]

                if city_widget.exempt == True:
                    continue
                try:
                    city_widget.icon_scatter_widget.remove_widget(city_widget.label)
                except:
                    pass

                self.city_labels = False

        else:

            for city in self.gui_manager.country_dictionary[self.country][1]:

                city_widget = self.gui_manager.country_dictionary[self.country][1][city][0]

                if city_widget.exempt == True:
                    continue

                try:
                    city_widget.icon_scatter_widget.add_widget(city_widget.label)
                except:
                    pass

                self.city_labels = True



    def toggle_ip_labels(self) -> None:

        """
        Toggles IP widget labels on/off
        """

        if self.ip_labels == True:

            for city in self.gui_manager.country_dictionary[self.country][1]:

                if ( self.gui_manager.country_dictionary[self.country][1][city][0].exempt == True ):
                    continue

                for ip in self.gui_manager.country_dictionary[self.country][1][city][1:]:

                    if ip.exempt == True:
                        continue

                    try:
                        ip.icon_scatter_widget.remove_widget(ip.label)
                    except:
                        pass

                    self.ip_labels = False

        else:  # self.ip_labels = False

            for city in self.gui_manager.country_dictionary[self.country][1]:

                if ( self.gui_manager.country_dictionary[self.country][1][city][0].exempt == True ):
                    continue

                for ip in self.gui_manager.country_dictionary[self.country][1][city][1:]:

                    if ip.exempt == True:
                        continue

                    try:
                        ip.icon_scatter_widget.add_widget(ip.label)
                    except:
                        pass

                self.ip_labels = True



    def toggle_my_label(self) -> None:

        """
        Toggles self.label on/off
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



    def toggle_menu(self, *args) -> None:

        """
        Toggle menu when user clicks on Country Widget.
        """

        if self.menu_boolean == False:
            self.menu_boolean = True

            self.gui_manager.persistent_widget_container.add_widget(self.menu_popup)
            self.gui_manager.misc_update_dictionary["country"][f"{self.country}"] = self

        elif self.menu_boolean == True:
            self.menu_boolean = False

            self.gui_manager.persistent_widget_container.remove_widget(self.menu_popup)
            del self.gui_manager.misc_update_dictionary["country"][f"{self.country}"]



    def activated_checkbox(self, activated_checkbox, value) -> None:

        """
        Set active mode (country_city or country_ips) for GUI display sliders
        """

        if activated_checkbox.id == "country_city":

            self.radius_slider.value = self.city_radius
            self.angle_slider.value = self.city_angle
            self.phase_slider.value = self.city_phase

        elif activated_checkbox.id == "country_ip":

            self.radius_slider.value = self.ip_radius
            self.angle_slider.value = self.ip_angle
            self.phase_slider.value = self.ip_phase

        self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"
        self.angle_label.text = f"\nAngle\n {self.angle_slider.value:.0f}"
        self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"



    def make_display_menu(self) -> Scatter:

        """
        Construct display menu for country widgets
        """

        grid_layout = GridLayout( cols=2, size_hint=(None, None), size=(dp(300), dp(200)), pos=(dp(10), dp(0)) )
        right_col_layout = BoxLayout(orientation="vertical", size_hint_x=1.3)
        left_col_layout = BoxLayout(orientation="vertical", size_hint_y=0.5)
        slider_container = GridLayout(cols=3)

        self.menu_popup = Scatter()
        self.menu_popup.size_hint = (None, None)
        self.menu_popup.size = (dp(320), dp(205))


        self.menu_popup.pos = self.icon_scatter_widget.pos
        self.menu_popup.id = self.country

        with self.menu_popup.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)
            RoundedRectangle(
                            size=self.menu_popup.size,
                            pos=(0, 0),
                            radius=[(20, 20), (20, 20), (20, 20), (20, 20)],
                            )

        if self.menu_popup.pos[0] + dp(200) > self.window_x:
            self.menu_popup.pos = (self.window_x - dp(320), self.menu_popup.pos[1])

        if self.menu_popup.pos[1] + dp(200) > self.window_y:
            self.menu_popup.pos = (self.menu_popup.pos[0], self.window_y - dp(205))

        toggle_label = Button()
        toggle_label.on_press = self.toggle_my_label
        toggle_label.font_size = sp(15)
        toggle_label.text = self.country
        toggle_label.background_color = (0.3, 0.3, 0.3, 0.9)
        toggle_label.background_down = os.path.join(self.resource_path, "assets/images/buttons/black.png")

        self.total_cities_label = Label( text="[b][color=ff1919]0[/color][/b]", markup=True )
        self.total_ip_label = Label( text=f"[b][color=ff1919]0[/color][/b]", markup=True )

        self.data_IN_label = Label()
        self.data_IN_label.font_size = sp(12)
        self.data_IN_label.border = (0, 0, 0, 0)
        self.data_IN_label.markup = True

        self.data_OUT_label = Label()
        self.data_OUT_label.markup = True
        self.data_OUT_label.font_size = sp(12)
        self.data_OUT_label.border = (0, 0, 0, 0)

        toggle_cities = Button()
        toggle_cities.on_press = self.toggle_city_widgets
        toggle_cities.text = "Toggle Cities"
        toggle_cities.background_color = (.5, .5, .5, 0.8)
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
        toggle_ips.background_color = (.7, .7, .7, 0.8)
        toggle_ips.font_size = sp(12)
        toggle_ips.border = (0, 0, 0, 0)

        toggle_ips_label = Button()
        toggle_ips_label.on_press = self.toggle_ip_labels
        toggle_ips_label.font_size = sp(8)
        toggle_ips_label.border = (0, 0, 0, 0)
        toggle_ips_label.size_hint_x = 0.1
        toggle_ips_label.background_normal =  os.path.join(self.resource_path, "assets/images/UI/tag.png")
        toggle_ips_label.background_down =  os.path.join(self.resource_path, "assets/images/UI/tag-down.png")
        

        self.radius_slider = Slider()
        self.radius_slider.id = "radius"
        self.radius_slider.value_track = False
        self.radius_slider.min = -self.window_x / 2
        self.radius_slider.max = self.window_x / 2
        self.radius_slider.value = 100
        self.radius_slider.orientation = "vertical"
        self.radius_slider.bind(value=self.graph_display)

        self.radius_label = Label(
                                text=f"\nRadius\n {self.radius_slider.value:.0f}",
                                halign="center",
                                valign="middle",
                                )
        self.radius_label.size_hint_y = 0.2
        slider_container.add_widget(self.radius_label)

        self.angle_slider = Slider()
        self.angle_slider.id = "angle"
        self.angle_slider.value_track = False
        self.angle_slider.min = -360
        self.angle_slider.max = 360
        self.angle_slider.value = 60
        self.angle_slider.orientation = "vertical"
        self.angle_slider.bind(value=self.graph_display)

        self.angle_label = Label(
                                text=f"\nAngle\n {2 * self.angle_slider.value:.0f}",
                                halign="center",
                                valign="middle",
                                )
        self.angle_label.size_hint_y = 0.2
        slider_container.add_widget(self.angle_label)

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
        self.phase_label.size_hint_y = 0.2
        slider_container.add_widget(self.phase_label)

        self.city_checkbox = CheckBox()
        self.city_checkbox.id = f"country_city"
        self.city_checkbox.group = f"{self.country}"
        
        self.city_checkbox.allow_no_selection = False
        self.city_checkbox.active = True
        self.city_checkbox.background_radio_normal = os.path.join( self.resource_path, "assets/images/UI/white_circle.png")
        self.city_checkbox.bind(active=self.activated_checkbox)

        self.ip_checkbox = CheckBox()
        self.ip_checkbox.id = "country_ip"
        self.ip_checkbox.group = f"{self.country}"
        self.ip_checkbox.bind(active=self.activated_checkbox)
        self.ip_checkbox.allow_no_selection = False
        self.ip_checkbox.background_radio_normal = os.path.join( self.resource_path, "assets/images/UI/white_circle.png" )

        checkbox_container2 = BoxLayout(orientation="horizontal", size_hint_y=0.8)
        checkbox_container2.add_widget(self.total_cities_label)
        checkbox_container2.add_widget(Label(size_hint_x=0.2))
        checkbox_container2.add_widget(Label(text="Cities"))
        checkbox_container2.add_widget(self.city_checkbox)

        checkbox_container3 = BoxLayout(orientation="horizontal", size_hint_y=0.8)
        checkbox_container3.add_widget(self.total_ip_label)
        checkbox_container3.add_widget(Label(size_hint_x=0.2))
        checkbox_container3.add_widget(Label(text="IP's"))
        checkbox_container3.add_widget(self.ip_checkbox)

        self.exempt_button = Button()
        self.exempt_button.on_press = self.toggle_exempt
        self.exempt_button.background_normal = os.path.join( self.resource_path, "assets/images/buttons/kivy-teal-4.png")
        self.exempt_button.background_down = os.path.join( self.resource_path, "assets/images/buttons/teal_down.png")
        self.exempt_button.border = (0, 0, 0, 0)
        self.exempt_button.font_size = sp(12)

        if self.exempt:
            self.exempt_button.text = "Exempt"
        else:
            self.exempt_button.text = "Not Exempt"

        dismiss_button = Button()
        dismiss_button.text = "Dismiss"
        dismiss_button.background_color = [1, 1, 1, 0.1]
        dismiss_button.font_size = sp(12)
        dismiss_button.on_press = self.toggle_menu
        dismiss_button.size_hint_y = 0.7

        # Construct menu
        label_container = BoxLayout(orientation="horizontal", size_hint_y=1)

        label_container.add_widget(Label(size_hint_x=0.25))
        label_container.add_widget(toggle_label)
        label_container.add_widget(Label(size_hint_x=0.25))

        left_col_layout.add_widget(label_container)

        left_col_layout.add_widget(Label(size_hint_y=0.5))

        left_col_layout.add_widget(checkbox_container3)
        left_col_layout.add_widget(checkbox_container2)
        left_col_layout.add_widget(Label(size_hint_y=0.5))

        data_labels_container = BoxLayout(orientation="vertical", size_hint_y=2)
        data_labels_container.add_widget(Label(size_hint_y=0.5))
        data_labels_container.add_widget(self.data_IN_label)
        data_labels_container.add_widget(self.data_OUT_label)
        data_labels_container.add_widget(Label(size_hint_y=0.5))

        left_col_layout.add_widget(data_labels_container)
        left_col_layout.add_widget(Label(size_hint_y=0.5))

        ip_container = BoxLayout(orientation="horizontal", size_hint_y=0.7)
        ip_container.add_widget(toggle_ips)
        ip_container.add_widget(Label(size_hint_x=0.013))
        ip_container.add_widget(toggle_ips_label)
        left_col_layout.add_widget(ip_container)

        left_col_layout.add_widget(Label(size_hint_y=0.1))

        cities_container = BoxLayout(orientation="horizontal", size_hint_y=0.7)
        cities_container.add_widget(toggle_cities)
        cities_container.add_widget(Label(size_hint_x=0.01))
        cities_container.add_widget(toggle_cities_label)
        left_col_layout.add_widget(cities_container)

        left_col_layout.add_widget(Label(size_hint_y=0.1))

        exempt_container = BoxLayout(orientation="horizontal", size_hint_y=0.65)
        exempt_container.add_widget(Label(size_hint_x=0.05))
        exempt_container.add_widget(self.exempt_button)
        exempt_container.add_widget(Label(size_hint_x = 0.175))
        left_col_layout.add_widget(exempt_container)


        left_col_layout.add_widget(Label(size_hint_y=0.1))

        dismiss_container = BoxLayout( orientation="horizontal", size_hint_x=1, size_hint_y=1)
        dismiss_container.add_widget(Label(size_hint_y=0.5))
        dismiss_container.add_widget(dismiss_button)
        dismiss_container.add_widget(Label(size_hint_y=0.5))

        left_col_layout.add_widget(dismiss_container)

        left_col_layout.add_widget(Label(size_hint_y=0.3))

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

        

    def set_graph_layout(self) -> None:

        """ 
        Callable to set graph layout
        """

        self.mercator_position = self.icon_scatter_widget.pos

        self.pos = self.graph_position
        self.icon_scatter_widget.pos = self.pos



    def set_mercator_layout(self) -> None:

        """ 
        Callable to set mercator(world) layout 
        """

        self.graph_position = self.icon_scatter_widget.pos

        self.icon_scatter_widget.pos = self.mercator_position
        self.pos = self.mercator_position



    def initalize_mercator_position(self, position: int) -> tuple[float, float]:

        """
        Initalize mercator position for countries.
        """

        # BUG: mercator_final_country_position ->
        y_index = floor(position / self.gui_manager.mercator_final_country_position)

        calculated_x = self.window_center_x / 2 + floor(((position) % self.gui_manager.mercator_final_country_position)) * 65
                    
        calculated_y = dp(40) * y_index + dp(45)

        return (calculated_x, calculated_y)



    def update(self, **kwargs) -> None:

        """
        Update GUI widget. Called every cycle.
        """

        self.graph_state = kwargs["state"]
        protocol_color = kwargs["protocol_color"]

        self.canvas.before.clear()
        x_pos, y_pos = self.icon_scatter_widget.pos

        with self.canvas.before:

            # map data from # of bytes to pixel length of line
            data_in = map_to_range(self.total_data_in, 0, self.gui_manager.country_largest_data_in, 0, 30.0)
            data_out = map_to_range(self.total_data_out, 0, self.gui_manager.country_largest_data_out, 0, 30.0,)

            Color(rgba=self.gui_manager.config_variables_dict["color_dictionary"]["Data IN Color"])
            Line(points=[x_pos, y_pos, x_pos + dp(data_in), y_pos], width=1)

            Color(rgba=self.gui_manager.config_variables_dict["color_dictionary"]["Data OUT Color"])
            Line(points=[x_pos, y_pos - dp(5), x_pos + dp(data_out), y_pos - dp(5)], width=1)

        if self.graph_state == True:

            my_computer_position = self.gui_manager.my_computer.icon_scatter_widget.pos

            # Make sure Country widget doesn't go off screen
            if self.x + 50 > self.window_x:
                self.x = self.x - 150
                self.icon_scatter_widget.pos = self.pos

            if self.x < 0:
                self.x = self.x + 250
                self.icon_scatter_widget.pos = self.pos

            if self.y + 50 > self.window_y:
                self.y = self.y - 150
                self.icon_scatter_widget.pos = self.pos

            if self.y < 0:
                self.y = self.y + 50
                self.icon_scatter_widget.pos = self.pos

            if self.attach == True:  # update position if widget is attached to parent

                distance, x_distance, y_distance = distance_between_points(my_computer_position, self.pos)  # calculate time-step distance (linear interpolation)

                if distance > 500:  # greater than 500 pixels
                    self.pos[0] += x_distance * self.spring_constant_k
                    self.pos[1] += y_distance * self.spring_constant_k
                else:
                    self.attach = False

            with self.canvas.before:

                delta_time = time.time() - self.new_packet_timestamp
                opacity = map_to_range(delta_time, self.gui_manager.new_packet_color_opacity, 0, 0, 1)
                protocol_color.append(opacity)
                Color(rgba=protocol_color)

                # draw connecting lines
                Line(
                        points=(
                            my_computer_position[0] + dp(20),
                            my_computer_position[1] + dp(20),
                            self.icon_scatter_widget.pos[0] + dp(15),
                            self.icon_scatter_widget.pos[1] + dp(15),
                                ),
                        width=2,
                    )