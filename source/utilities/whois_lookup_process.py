# Jonathan Valiente.  All rights reserved. 2022

# The software is provided "As is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.
# in no event shall the authors be liable for any claim, damages or
# other liability, whether in an action of contract, tort or otherwise,
# arising from, out of or in connection with the software or the use or
# other dealings in the software.

from ipwhois import IPWhois  # IP description and abuse emails


def ip_whois_lookup_process(connection): 

            while True:
                if connection.poll():

                    new_ip_whois_array = connection.recv()

                    whois_return_dict = {}
                    
                    for ip in new_ip_whois_array:
                        
                        try:

                            ip_whois = IPWhois(ip)
                            ip_whois_info = ip_whois.lookup_whois()
                            ip_whois_description = ip_whois_info["nets"][0]["description"]

                            if ip_whois_description == None:
                                ip_whois_description = "No Description Available"

                            while ip_whois_description.find("'") >= 0:
                                ip_whois_description = ip_whois_description.replace("'", "")

                            while ip_whois_description.find('"') >= 0:
                                ip_whois_description = ip_whois_description.replace('"', "")

                            ip_whois_info["nets"][0]["description"] = ip_whois_description

                            whois_return_dict[ip] = ip_whois_info
                        
                        except Exception as e:
                            print(e)

                    connection.send(whois_return_dict)

                else:
                    pass