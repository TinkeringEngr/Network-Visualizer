# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.


# Thanks to Keith Peters from Coding Math youtube channel, he's a real OG
# https://www.youtube.com/user/codingmath/videos


from math import sqrt, floor, pi, atan2
from random import random
from requests import get
from skimage.color import rgb2lab, lab2rgb
from uuid import getnode as get_mac

from kivy.uix.scatter import Scatter
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.metrics import sp, dp



def normalize(value, minV, maxV):
    
    """
    Returns a normalized value between 0-1
    """
      
    return (value - minV) / float(maxV - minV)


def lerp(norm_value, minV, maxV):
    
    """
    Linear interpolation for a desired range
    """  

    return norm_value * (maxV - minV) + minV


def map_to_range(value, rangeA_min, RangeA_max, RangeB_min, RangeB_max):

    """
    Maps a value from range_A to range_B
    """
    
    N_value = normalize(value, rangeA_min, RangeA_max)
    return lerp(N_value, RangeB_min, RangeB_max)
    # succint version: return lerp(normalize(value, rangeA_min, RangeA_max), RangeB_min, RangeB_max)


def clamp(value, minimum, maximum): 
    
    """
    Constrain value to min and max
    """

    return min(max(value, minimum), maximum)


def distance(point1, point2):

    """
    Calculate the distance between two points
    """

    dx = point1[0] - point2[0]
    dy = point2[1] - point2[1]
    return sqrt(dx * dx + dy * dy)


def random_range(minimum, maximum):

    """
    Return a random value betweeen a given minimum and maximum range
    """

    return minimum + random() * (maximum - minimum)


def random_int(minimum, maximum): 
    
    """
    Return a random int between minimum and maximum range
    """
    
    return floor(round(minimum + random() * (maximum - minimum + 1)))  # add 1 to range and floor to prevent bias with round


def deg_to_rad(deg):

    """
    Convert degrees to radians
    """

    return deg * pi / 180


def rad_to_deg(rad):

    """
    Convert radians to degrees
    """

    return rad * 180 / pi


def round_to_places(value, places):

    """
    Round a number to a decimal form
    """

    mult = pow(10, places)
    return round(value * mult) / mult


def round_to_nearest(value, nearest):

    """
    Round to nearest value (useful to snap to grid)
    """

    return round(value / nearest) * nearest


def remove_inline_quotes(string):

    """
    Remove inline single and dobule quotes
    """

    if string is None:
        return None

    while string.find("'") >= 0:
        string = string.replace("'", "")

    while string.find('"') >= 0:
        string = string.replace('"', "")

    return string


def angle_between_points(objectA_pos: tuple[float, float], objectB_pos: tuple[float, float]) -> float:

    """
    Calculate the angle between two points.
    """

    dx = objectB_pos[1] - objectA_pos[1]
    dy = objectB_pos[0] - objectA_pos[0]

    return atan2(dx, dy)


def distance_between_points( destination: tuple[float, float], source: tuple[float, float]) -> tuple[float, float, float]:

    """
    Calculate the distance between two points.
    """

    x_distance = destination[0] - source[0]
    y_distance = destination[1] - source[1]

    distance = sqrt(x_distance * x_distance + y_distance * y_distance)

    return distance, x_distance, y_distance


def populate_network_interfaces() -> None:

        """
        Identify network interfaces.
        """

        my_mac_address = ":".join( ("%012x" % get_mac())[i : i + 2] for i in range(0, 12, 2) )
        return my_mac_address


def retrieve_malicious_ips(malicious_ips_dictionary: dict ) -> None:

        """
        Populate Malicious_ips_dictionary from curated IP ban lists
        """

        try:
            raw_malcious_ips = get(
                "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt"
            )
            decoded_raw_malcious_ips = raw_malcious_ips.content.decode("utf-8")
            cut_comments_index = decoded_raw_malcious_ips.rindex("#") + 2

            malcious_ips = decoded_raw_malcious_ips[cut_comments_index:]

            malicious_ips_list = malcious_ips.split("\n")

            for line in malicious_ips_list[:-1]:
                ip, ban_count = line.split("\t")

                malicious_ips_dictionary[ip] = ban_count
        except:
            pass


        return malicious_ips_dictionary


class IP_Icon_Scatter_Override(Scatter):

    """
    Override kivy Scatter widget to allow for scatter widget to drag/drop without bugging its position when being updated by update()
    """

    def __init__(self, **kwargs):
        super().__init__()


    def on_pos(self, country_scatter:Scatter, position: tuple[float, float]):

        """
        Position menu if scatter moves
        """
       
        try:
            if self.parent.parent.menu_boolean == False:
                position_x, position_y = position[0]- dp(67), position[1] + dp(25)
                self.parent.parent.menu_popup.pos = (position_x, position_y) 
               
        except:
            pass



class City_Icon_Scatter_Override(Scatter):

    """
    Override kivy Scatter widget to allow for scatter widget to drag/drop without bugging its position when being updated by update()
    """

    def __init__(self, **kwargs):
        super().__init__()


    def on_touch_up(self, touch: MouseMotionEvent) -> bool:

        """
        Kivy on_touch_up callback.
        """

        response = super().on_touch_up(touch)

        if response:

            if self.parent.parent.exempt == False:
                self.parent.parent.position_ips() #parent.parent referes to City Widget

        return response


    def on_pos(self, country_scatter:Scatter, position: tuple[float, float]):

        """
        Position menu if scatter moves
        """
       
        try:
            if self.parent.parent.menu_boolean == False:
                position_x, position_y = position[0]- dp(65), position[1] + dp(20)
                self.parent.parent.menu_popup.pos = (position_x, position_y) 
               
        except:
            pass


class Computer_Icon_Scatter_Override(Scatter):

    def __init__(self, **kwargs):

        super().__init__()

    def on_touch_up(self, touch: MouseMotionEvent) -> bool:

        """
        Kivy on_touch_up callback.
        """

        response = super().on_touch_up(touch)

        if response:

            if self.parent.parent.gui_manager.graph == True: #parent.parent referes to Computer Widget
                self.parent.parent.graph_position = self.pos

                if self.parent.parent.exempt == False:
                    self.parent.parent.graph_display(self.parent.parent.phase_slider, 0)
                
            else:
                self.parent.parent.mercator_position = self.pos

        return response


    def on_pos(self, country_scatter:Scatter, position: tuple[float, float]):

        """
        Position menu if scatter moves
        """
       
        try:
            if self.parent.parent.menu_boolean == False:
                position_x, position_y = position[0]- dp(65), position[1] + dp(35)
                self.parent.parent.menu_popup.pos = (position_x, position_y) 
               
        except:
            pass


class Country_Icon_Scatter_Override(Scatter):

    def __init__(self, **kwargs):

        super().__init__()


    def on_touch_up(self, touch: MouseMotionEvent) -> bool:

        """
        Kivy on_touch_up callback.
        """

        response = super().on_touch_up(touch)

        if response:

            if self.parent.parent.exempt == False: #parent.parent referes to Country Widget
                #self.parent.parent.graph_display(self.parent.parent.angle_slider, 360)
                self.parent.parent.position_cities()
      

        return response


    def on_pos(self, country_scatter:Scatter, position: tuple[float, float]):

        """
        Position menu if scatter moves
        """
       
        try:
            if self.parent.parent.menu_boolean == False:
                position_x, position_y = position[0]- dp(60), position[1] + dp(30)
                self.parent.parent.menu_popup.pos = (position_x, position_y) 
               
        except:
            pass