# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.


from math import sin, pi, cos, sqrt
import os
from random import random, randrange, randint
import sys

sys.path.append("..")  # Adds higher directory to python modules path.
import time


from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatter import Scatter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.graphics import Color, Line, Bezier, RoundedRectangle, InstructionGroup
#from kivy.graohics.instructions import InstructionGroup
from kivy.metrics import sp, dp
from kivy.properties import ListProperty




from utilities.utils import map_to_range, City_Icon_Scatter_Override, distance


class City_Widget(Widget):

    """
    GUI Widget for each geographic city with member functions for displaying associated IP widgets.
    """

    anim_pt = ListProperty([])

    def __init__(self, **kwargs) -> None:

        """
        Construct GUI widget and associated state.
        """

        super().__init__()

        self.gui_manager = kwargs["gui_manager"]
        self.center_x = kwargs["center_x"]
        self.center_y = kwargs["center_y"]
        self.window_x = kwargs["window_x"]
        self.window_y = kwargs["window_y"]
        self.country = kwargs["country"]
        self.city = kwargs["city"]
        self.city_label = "Unresolved" if self.city == None else self.city
        self.latitude = kwargs["latitude"]
        self.longitude = kwargs["longitude"]
        self.longitude_x = kwargs["longitude_x"]
        self.latitude_y = kwargs["latitude_y"]
        self.resource_path = kwargs["resource_path"]
        #self.protocol_color_dict = kwargs["protocol_dict"]

        self.random_radius = randrange(dp(300), dp(500))
        self.new_packet_timestamp = time.time()

        self.attach = True
        self.exempt = False
        self.show = True
        #self.do_layout = True
        self.menu_boolean = False
        self.show_ip_widgets = True
        self.ip_labels = False

        self.mylabel_bool = True if self.gui_manager.city_labels == True  else  False
           
        self.last_packet = "TCP"
        self.total_data_out = 0
        self.total_data_in = 0
        self.draw_angle = 0
        self.spring_constant_1 = 0.1
        self.ip_total_count = 1
        self.ip_phase = 0
        self.ip_radius = dp(100)
        self.ip_angle = 60
        self.graph_state = "graph"
        self.x_, self.y_ = self.set_position()
        self.pos = (self.x_, self.y_)
        self.old_pos = self.pos

        ##Create GUI widget
        self.label = Label()
        self.label.text = self.city_label
        self.label.font_size = sp(15)
        self.label.font_blended = False
        self.label.pos = (dp(-18), dp(1))
        self.label.font_hinting = "normal"

        self.container = FloatLayout()
        self.container.pos = self.pos
        self.container.size_hint = (None, None)
        self.container.size = ("50sp", "50sp")

        self.icon_image = Image()
        self.icon_image.source = os.path.join(self.resource_path, f"assets/images/country_icons/{self.country}.png")

        self.icon_image.size_hint = (None, None)
        self.icon_image.size = (dp(10), dp(10))
        self.icon_image.pos = (dp(4), dp(4))

        self.display_menu_button = Button()
        self.display_menu_button.on_press = self.toggle_menu
        self.display_menu_button.size_hint = (None, None)
        self.display_menu_button.pos = (dp(5), dp(5))
        self.display_menu_button.size = (dp(8), dp(8))
        self.display_menu_button.background_color = (1, 1, 1, 0)

        self.icon_scatter_widget = City_Icon_Scatter_Override()


        self.icon_scatter_widget.size_hint = (None, None)
        self.icon_scatter_widget.pos = self.pos
        self.icon_scatter_widget.size = (dp(18), dp(18))
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

        self.display_menu_button.add_widget(self.icon_image)
        self.icon_scatter_widget.add_widget(self.display_menu_button)
        if self.mylabel_bool == True:
            self.icon_scatter_widget.add_widget(self.label)

        self.container.add_widget(self.icon_scatter_widget)
        self.add_widget(self.container)
        self.icon_scatter_widget.pos = (self.x_, self.y_)

        self.particle_image = Image()
        self.particle_image.source = os.path.join(self.resource_path, "assets/images/UI/particle.png")

        self.animating_bez = False

        # Mercator view state
        self.intial_layout = False
        self.mercator_position = (self.longitude_x, self.latitude_y)
        self.initial_mercator_position = (self.longitude_x, self.latitude_y)
        self.mercator_show = True
        self.is_city = True
        #self.ip_do_layout = False
        self.animating_particle = False
        #

        # Graph view state
        self.graph_position = self.icon_scatter_widget.pos
        self.initial_graph_position = self.graph_position

        self.menu_popup = None #Populated by self.make_display_menu
        self.make_display_menu()

        if kwargs["graph_state"] == False:
            self.icon_scatter_widget.pos = self.mercator_position



    def graph_display( self, slider: Slider, slider_value: float, from_my_computer=False) -> None:

        """
        Display associated IP widgets in a circle.
        """

        if slider.id == "radius":
            self.ip_radius = dp(slider_value)
            self.radius_label.text = f"\nRadius\n {self.radius_slider.value:.0f}"

        elif slider.id == "angle":
            self.ip_angle = slider_value
            self.angle_label.text = f"\nAngle\n {self.angle_slider.value:.0f}"

        elif slider.id == "phase":
            self.ip_phase = slider_value
            self.phase_label.text = f"\nSpin\n {self.phase_slider.value:.0f}"

        radian_ip_angle = self.ip_angle * (pi / 180)
        radian_ip_phase = self.ip_phase * (pi / 180)

        if self.exempt:
            city_pos = self.excempt_pos

        else:
            city_pos = self.icon_scatter_widget.pos


        for n, ip in enumerate(self.gui_manager.active_ips[self.country][self.city]):
            ip_widget = self.gui_manager.ip_dictionary[ip]

            if ip_widget.exempt == True:
                continue

            self.x_, self.y_ = self.set_position_for_ip_widgets( n, self.ip_total_count, radian_ip_angle, self.ip_radius, radian_ip_phase)
            ip_widget.new_pos = (self.x_, self.y_)
            ip_widget.pos = (city_pos[0] + self.x_, city_pos[1] + self.y_)
            ip_widget.icon_scatter_widget.pos = ip_widget.pos



    def position_ips(self, *args):

        """
        Callable to position associated IP Widgets
        """

        for n, ip in enumerate(self.gui_manager.active_ips[self.country][self.city]):
            ip_widget = self.gui_manager.ip_dictionary[ip]

            if ip_widget.exempt == True:
                continue

            active_ip_count  = len(self.gui_manager.active_ips[self.country][self.city])

            screen_x, screen_y = self.set_position_for_ip_widgets(n, active_ip_count, 2 * pi, self.ip_radius, 0)
            ip_widget.new_pos = (screen_x, screen_y)
            ip_widget.pos = (
                                self.icon_scatter_widget.pos[0] + screen_x,
                                self.icon_scatter_widget.pos[1] + screen_y,
                            )
            ip_widget.icon_scatter_widget.pos = ip_widget.pos



    def set_ips_mercator_inital_position(self, *args) -> None:

        """
        Initalize mercator position for ips on creation 
        """

        for n, ip in enumerate(self.gui_manager.country_dictionary[self.country][1][self.city]):  # access relevant IP widgets

            if n == 0: #skip city widget
                continue

            if ip.init_position == True:
                continue
            
            active_ip_count  = len( self.gui_manager.active_ips[self.country][self.city].keys() )

            screen_x, screen_y = self.set_position_for_ip_widgets( n, active_ip_count, 180, 100, 0 )

            ip.inital_mercator_position = ( self.initial_mercator_position[0] + screen_x, self.initial_mercator_position[1] + screen_y, )

            ip.mercator_position = (self.initial_mercator_position[0] + screen_x, self.initial_mercator_position[1] + screen_y,)
                                
            ip.init_position = True



    def toggle_ip_widgets(self) -> None:

        """
        Toggle display of all associated City widgets.
        """

        if self.show_ip_widgets == False:

            self.show_ip_widgets = True
            
            for ip in self.gui_manager.country_dictionary[self.country][1][self.city][1:]:

                if ip.exempt == True:
                    continue

                ip.show = True

        else:

            self.show_ip_widgets = False
            for ip in self.gui_manager.country_dictionary[self.country][1][self.city][1:]:

                if ip.exempt == True:
                    continue

                ip.show = False

            



    def set_position(self) -> tuple[float, float]:

        """
        Calculate random x and y screen position for city widget.
        """

        x = self.gui_manager.country_dictionary[self.country][0].pos[0] + dp(150) * sin( 2 * pi * random() )
        y = self.gui_manager.country_dictionary[self.country][0].pos[1] + dp(150) * cos( 2 * pi * random() )

        return x, y



    def set_position_for_ip_widgets(
                                    self, ip_index: int,
                                    total_count: int,
                                    draw_angle: int, 
                                    radius: int, 
                                    phase: int
                                    ) -> tuple[float, float]:

        """
        Calculate x, y position using slider radius for associated IP widgets.
        """

        if total_count == 0:
            total_count = 1

        pi_slice = draw_angle / total_count

        x = radius * sin(pi_slice * ip_index + phase)
        y = radius * cos(pi_slice * ip_index + phase)

        return x, y



    def distance_between_points(
                                self,
                                destination: tuple[float, float],
                                source: tuple[float, float]
                                ) -> tuple[float, float, float]:

        """
        Find the distance between two points.
        """

        x_distance = destination[0] - source[0]
        y_distance = destination[1] - source[1]
        distance = sqrt(x_distance * x_distance + y_distance * y_distance)

        return distance, x_distance, y_distance



    def toggle_menu(self, *args) -> None:

        """
        Toggle menu when user clicks on City Widget.
        """

        if self.menu_boolean == False:
            self.menu_boolean = True

            self.gui_manager.persistent_widget_container.add_widget(self.menu_popup)
            self.gui_manager.misc_update_dictionary["city"][f"{self.city}"] = self

        elif self.menu_boolean == True:
            self.menu_boolean = False

            self.gui_manager.persistent_widget_container.remove_widget(self.menu_popup)
            del self.gui_manager.misc_update_dictionary["city"][f"{self.city}"]



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



    def toggle_ip_labels(self) -> None:

        """
        Toggles IP widget labels on/off
        """

        if self.ip_labels == True:

            for ip in self.gui_manager.country_dictionary[self.country][1][self.city][1:]:
                if ip.exempt == True:
                    continue

                try:
                    ip.icon_scatter_widget.remove_widget(ip.label)
                except:
                    pass

                self.ip_labels = False

        else:  # self.ip_labels = False

            for ip in self.gui_manager.country_dictionary[self.country][1][self.city][1:]:

                if ip.exempt == True:
                    continue

                try:
                    ip.icon_scatter_widget.add_widget(ip.label)
                except:
                    pass

            self.ip_labels = True



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

        else:  # self.mylabel_bool == False

            try:
                self.icon_scatter_widget.add_widget(self.label)
            except:
                pass

            self.mylabel_bool = True



    def make_display_menu(self) -> Scatter:

        """
        Create popup menu when user clicks on the City widget.
        """

        self.menu_popup = Scatter()
        self.menu_popup.size_hint = (None, None)
        self.menu_popup.size = (dp(320), dp(170))
        self.menu_popup.pos = ( self.icon_scatter_widget.pos[0], self.icon_scatter_widget.pos[1] + 50 )
        self.menu_popup.id = self.country

        with self.menu_popup.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)
            RoundedRectangle(
                            size=self.menu_popup.size,
                            pos=(0, 0),
                            radius=[(20, 20), (20, 20), (20, 20), (20, 20)],
                            )

        if self.menu_popup.pos[0] + dp(175) > self.window_x:
            self.menu_popup.pos = (self.window_x - dp(175), self.menu_popup.pos[1])

        if self.menu_popup.pos[1] + dp(150) > self.window_y:
            self.menu_popup.pos = (self.menu_popup.pos[0], self.window_y - dp(160))

        grid_layout = GridLayout(
                                cols=2,
                                size_hint=(None, None),
                                size=(dp(300), dp(150)),
                                pos=(dp(10), dp(0))
                                )
        right_col_layout = BoxLayout(orientation="vertical", size_hint_x=1.3)
        left_col_layout = BoxLayout(orientation="vertical", size_hint_y=0.5)
        slider_container = GridLayout(cols=3)

        city_label = Label()
        city_label.text = self.city_label
        city_label.font_size = sp(15)
        city_label.font_blended = False
        city_label.font_hinting = None

        self.data_IN_label = Label()
        # self.data_IN_label.text = f"Data IN (MB): [b][color={data_in_color}]{self.total_data_in/1000000.0:.6f}[/color][/b]"
        self.data_IN_label.font_size = sp(12)
        self.data_IN_label.font_blended = False
        self.data_IN_label.font_hinting = None
        self.data_IN_label.markup = True

        self.data_OUT_label = Label()
        # self.data_OUT_label.text = f"Data OUT (MB): [b][color={data_out_color}]{self.total_data_out/1000000.0:.6f}[/color][/b]"
        self.data_OUT_label.font_size = sp(12)
        self.data_OUT_label.font_blended = False
        self.data_OUT_label.font_hinting = None
        self.data_OUT_label.markup = True

        toggle_ips = Button()
        toggle_ips.text = "Toggle IP's"
        toggle_ips.on_press = self.toggle_ip_widgets
        toggle_ips.background_color = (.5, .5, .5, 0.8) 
        toggle_ips.font_size = sp(12)
        toggle_ips.border = (0, 0, 0, 0)

        toggle_ips_label = Button()
        toggle_ips_label.on_press = self.toggle_ip_labels
        toggle_ips_label.font_size = sp(8)
        toggle_ips_label.border = (0, 0, 0, 0)
        toggle_ips_label.size_hint_x = 0.1
        toggle_ips_label.background_normal =  os.path.join(self.resource_path, "assets/images/UI/tag.png")
        toggle_ips_label.background_down =  os.path.join(self.resource_path, "assets/images/UI/tag-down.png")

        toggle_ips_label.size_hint_x = 0.1

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
        self.radius_label.size_hint_y = 0.01
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
                                text=f"\nAngle\n {self.angle_slider.value:.0f}",
                                halign="center",
                                valign="middle",
                                )
        self.angle_label.size_hint_y = 0.01
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
        self.phase_label.size_hint_y = 0.01
        slider_container.add_widget(self.phase_label)

        self.total_ip_label = Label( text=f"[b][color=ff1919]0[/color][/b]", markup=True)

        checkbox_container3 = BoxLayout(orientation="horizontal", size_hint_y=0.8)

        checkbox_container3.add_widget(Label())
        checkbox_container3.add_widget(self.total_ip_label)
        checkbox_container3.add_widget(Label(text="IP's"))
        checkbox_container3.add_widget(Label())


        toggle_label = Button()
        toggle_label.on_press = self.toggle_my_label
        toggle_label.font_size = sp(15)
        toggle_label.text = self.city_label
        toggle_label.background_color = (0.3, 0.3, 0.3, 0.9)
        toggle_label.background_down = os.path.join(self.resource_path, "assets/images/buttons/black.png")
        toggle_label.size_hint_y = 1
        toggle_label.size_hint_x = 1

        self.exempt_button = Button()
        self.exempt_button.on_press = self.toggle_exempt
        self.exempt_button.background_normal = os.path.join(self.resource_path, "assets/images/buttons/kivy-teal-4.png")
        self.exempt_button.background_down = os.path.join(self.resource_path, "assets/images/buttons/teal_down.png")
        self.exempt_button.border = (0, 0, 0, 0)
        self.exempt_button.font_size = sp(12)

        if self.exempt:
            self.exempt_button.text = "Non-Exempt"
        else:
            self.exempt_button.text = "Exempt"

        dismiss_button = Button()
        dismiss_button.text = "Dismiss"
        dismiss_button.background_color = [1, 1, 1, 0.1]
        dismiss_button.border = (1, 1, 1, 0)
        dismiss_button.font_size = sp(12)
        dismiss_button.on_press = self.toggle_menu

        label_container = BoxLayout(orientation="horizontal", size_hint_y=1)
        label_container.add_widget(Label(size_hint_x=0.3))
        label_container.add_widget(toggle_label)
        label_container.add_widget(Label(size_hint_x=0.3))
        left_col_layout.add_widget(label_container)

        left_col_layout.add_widget(Label(size_hint_y=1))
        left_col_layout.add_widget(checkbox_container3)
        left_col_layout.add_widget(Label(size_hint_y=0.7))
        left_col_layout.add_widget(self.data_IN_label)

        left_col_layout.add_widget(self.data_OUT_label)
        left_col_layout.add_widget(Label(size_hint_y=0.8))

        ip_container = BoxLayout(orientation="horizontal", size_hint_y=1)
        ip_container.add_widget(toggle_ips)
        ip_container.add_widget(Label(size_hint_x=0.013))
        ip_container.add_widget(toggle_ips_label)

        left_col_layout.add_widget(ip_container)
        left_col_layout.add_widget(Label(size_hint_y=0.1))

        exempt_container = BoxLayout(orientation="horizontal", size_hint_y=0.75)
        exempt_container.add_widget(Label(size_hint_x=0.05))
        exempt_container.add_widget(self.exempt_button)
        exempt_container.add_widget(Label(size_hint_x = 0.175))
        left_col_layout.add_widget(exempt_container)

        dismiss_container = BoxLayout( orientation="horizontal", size_hint_x=1, size_hint_y=1)
        dismiss_container.add_widget(Label(size_hint_y=0.5))
        dismiss_container.add_widget(dismiss_button)
        dismiss_container.add_widget(Label(size_hint_y=0.5))

        left_col_layout.add_widget(dismiss_container)

        left_col_layout.add_widget(Label(size_hint_y=0.3))

        slider_container.add_widget(Label(size_hint_y=0.2))
        slider_container.add_widget(Label(size_hint_y=0.2))
        slider_container.add_widget(Label(size_hint_y=0.2))
        slider_container.add_widget(self.radius_slider)
        slider_container.add_widget(self.angle_slider)
        slider_container.add_widget(self.phase_slider)

        right_col_layout.add_widget(slider_container)

        grid_layout.add_widget(left_col_layout)
        grid_layout.add_widget(right_col_layout)

        self.menu_popup.add_widget(grid_layout)

        

    def animate_mercator(self, data_in) -> None:

        """
        Animate particle on mercator world
        """

        if self.animating_particle == False:
            self.animating_particle = True
            particle_image_size = map_to_range(data_in, 0, 5000000, 20, 100.0)

            self.particle_image.size = (particle_image_size, particle_image_size)
            self.particle_image.pos = ( self.icon_scatter_widget.pos[0] - particle_image_size / 2, self.icon_scatter_widget.pos[1] - particle_image_size / 2 )
            self.add_widget(self.particle_image)

            if distance(self.particle_image.pos, self.gui_manager.my_computer.icon_scatter_widget.pos) > (self.window_x/2):
                animation_time = 2

            else:
                animation_time = 1.5


            self.anim = Animation(
                                pos=(
                                    self.gui_manager.my_computer.icon_scatter_widget.pos[0] - particle_image_size / 2 + dp(15),
                                    self.gui_manager.my_computer.icon_scatter_widget.pos[1] - particle_image_size / 2 + dp(12),
                                    ),
                                d=animation_time,
                                t="linear",
                                )

            self.anim.repeat = False
            self.anim.start(self.particle_image)
    

            self.anim.bind(on_complete=lambda x, y: self.animateComplete(x, y))



    def animateComplete(self, *arg) -> None:

        """
        Particle Animation cleanup
        """

        self.remove_widget(self.particle_image)
        self.animating_particle = False



    def set_mercator_layout(self) -> None:

        """
        Saves graph position and restores mercator position
        """

        # Store graph position
        self.graph_position = self.icon_scatter_widget.pos

        # Set world position
        self.icon_scatter_widget.pos = self.mercator_position
        self.pos = self.mercator_position



    def set_graph_layout(self) -> None:

        """ 
        Saves mercator position and restores graph position
        """

        self.mercator_position = self.icon_scatter_widget.pos

        self.pos = self.graph_position
        self.icon_scatter_widget.pos = self.pos



    def update(self, **kwargs) -> None:

        """
        Update GUI widget. Called every cycle.
        """

        self.graph_state = kwargs["state"]
        protocol_color = kwargs["protocol_color"]

        self.canvas.before.clear()

        x_pos, y_pos = self.icon_scatter_widget.pos

        # map data from bytes to pixel length of a line segment
        data_in = map_to_range( self.total_data_in, 0, self.gui_manager.city_largest_data_in, 0, 30.0 )
        data_out = map_to_range( self.total_data_out, 0, self.gui_manager.city_largest_data_out, 0, 30.0 )

        with self.canvas.before:

            Color(rgba=self.gui_manager.config_variables_dict["color_dictionary"]["Data IN Color"])
            Line(points=[x_pos, y_pos, x_pos + dp(data_in), y_pos], width=1)

            Color(rgba=self.gui_manager.config_variables_dict["color_dictionary"]["Data OUT Color"])
            Line(points=[x_pos, y_pos - dp(5), x_pos + dp(data_out), y_pos - dp(5)], width=1)

        if self.graph_state  == True:

            country_position = self.gui_manager.country_dictionary[self.country][0].icon_scatter_widget.pos

            ##### So city widget doesn't go off screen
            if self.x + 50 > self.window_x:
                self.x = self.x - 100
                self.icon_scatter_widget.pos = self.pos

            if self.x < 0:
                self.x = self.x + 100
                self.icon_scatter_widget.pos = self.pos

            if self.y + 50 > self.window_y:
                self.y = self.y - 100
                self.icon_scatter_widget.pos = self.pos

            if self.y < 0:
                self.y = self.y + 100
                self.icon_scatter_widget.pos = self.pos
            #####

            if self.attach == True:

                distance_to_country, x_distance, y_distance = self.distance_between_points( country_position, self.pos )  # calculate time-step distance for linear interpolation

                if (distance_to_country > 300):  # if widget is more than 300 pixels away from country
                    self.pos[0] += x_distance * self.spring_constant_1
                    self.pos[1] += y_distance * self.spring_constant_1
                    self.icon_scatter_widget.pos = self.pos

                else:
                    self.attach = False

            with self.canvas.before:

                delta_time = time.time() - self.new_packet_timestamp
                opacity = map_to_range(delta_time, self.gui_manager.new_packet_color_opacity, 0, 0, 1)

                if opacity < 0:
                    Color(1, 1, 1, 0.1)

                else:
                    protocol_color.append(opacity)
                    Color(rgba=protocol_color)

                Line(
                    points=(
                            country_position[0] + dp(15),
                            country_position[1] + dp(15),
                            self.icon_scatter_widget.pos[0] + dp(9),
                            self.icon_scatter_widget.pos[1] + dp(9),
                            ),
                    width=1.3
                    )
