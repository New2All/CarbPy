 #=================================================================================================================================*
 #
 # Carby  A process to roughly estimate the Carbon Dioxide Emmission in Metric Tons for a given journey.  
 #        From/to Locations are elected and resolved to coordinates, then distance in kilometers calculated using geopy utilities.
 #        GHG emissions (gCO2e/km) per transport mode are derived from 'our world in data' table extract.
 #        To note that this version serves as a prototype or proof-of-concept. It is not meant as a finished product. 
 #        Version 0.2 Beta 
 #=================================================================================================================================*
 #
 #       Copyright (c) 2021 Michael Prior 
 #
 #       Permission is hereby granted, free of charge, to any person obtaining a copy
 #       of this software and associated documentation files (the "Software"), to deal
 #       in the Software without restriction, including without limitation the rights
 #       to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 #       copies of the Software, and to permit persons to whom the Software is
 #       furnished to do so, subject to the following conditions:
 #
 #       The above copyright notice and this permission notice shall be included in all
 #       copies or substantial portions of the Software.
 #
 #       THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 #       IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 #       FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 #       AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 #       LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 #       OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 #       SOFTWARE.
 #
 #=================================================================================================================================*
 #       CHANGE LOG : V 0.2 Minor label changes, conventions adherence, result rounding; default to 3 dec. Sep 2021 MP
 #=================================================================================================================================*

import geopy
import PySimpleGUI as sg
global lcl_msgtxt
 
 #--------------------------------------------------------------------------------------------------------------------------------*
 # Given Journey From and To Locations and Transport Mode, return Estimated Co2 Emmissions in Kg.
 #--------------------------------------------------------------------------------------------------------------------------------*

def main(cby_from='',cby_to='',cby_mode='',guiprompt=True,cby_rnd=3):

    cby_co2km = 0.0
    cby_co2   = 0.0
    lcl_option = ' ' 
    lcl_msgtxt = ""
   
    while lcl_option != 'Exit' and lcl_option != None:
        
        if guiprompt: [lcl_option,vals] = cby_gui()                            # GUI if desired
        
        lcl_from   = vals[0]
        lcl_to     = vals[1]
        lcl_mode   = vals[2]    
    
        if (lcl_option == 'Submit'):

            
            [cby_dist,lcl_msgtxt]  = cby_getdist(lcl_from,lcl_to)              # Dist Km calculation

            if lcl_msgtxt == "":

                cby_co2km          = cby_getCo2Km(lcl_mode)                    # Co2e per Km / transport mode determination

                try:
                    (1 / cby_co2km)                                            # valid value?
                except:
                    lcl_msgtxt = "Error - Select Transport Mode"               # No - setup error message 
                else:                                                  
                    cby_co2 = round(((cby_dist * cby_co2km)/1000),cby_rnd)     # OK - so calculate total emmission in Co2 kg  
            
        if guiprompt: cby_popup(cby_co2,lcl_msgtxt)                            # Pop-up the result - if GUI
        return cby_co2                                                         # - or return it to caller. 

 #--------------------------------------------------------------------------------------------------------------------------------*
 # GUI prompt, where needed. 
 #--------------------------------------------------------------------------------------------------------------------------------*
def cby_gui():
    

    
    import PySimpleGUI as sg

    sg.ChangeLookAndFeel('LightBlue3')

    form = sg.FlexForm('Carby', default_element_size=(40, 1))

    combos = []
    # Build combo box list, which is simply comprised of the keys of the Co2 dictionary, further below

    for key in dict_Co2.keys(): 
        combos.append(key)
        
    
    layout = [
        [sg.Text('Carby - Travel Co2 Emission Estimator', size=(30, 1), font=("Helvetica", 25))],
        [sg.Text('Enter "From" location ....                                Enter "To" location....')],
        [sg.Multiline(default_text='', size=(35, 3)),
         sg.Multiline(default_text='', size=(35, 3))],
        [sg.Text('Select Mode of Transport')],
        [sg.InputCombo((combos), default_value="Entity", size=(80, 3))],
        [sg.Text('_'  * 80)],
        [sg.Submit(), sg.Exit()]
         ]

    button, values = form.Layout(layout).Read()
    form.close()
    print(button)
    return((button,values))


 #--------------------------------------------------------------------------------------------------------------------------------*
 # Pop up result if GUI mode
 #--------------------------------------------------------------------------------------------------------------------------------*
def cby_popup(cby_co2,lcl_msgtxt):
    
    co2res = ""

    if (lcl_msgtxt == ""):
        co2res = "Total Co2 production for your journey is approximately: {} Metric Tonnes"
        co2res = co2res.format(cby_co2)
    else:
        co2res = lcl_msgtxt

    sg.popup(co2res, title='Results')

    return 
 #--------------------------------------------------------------------------------------------------------------------------------*
 # Calculate & return distance in kilometers from address location to address location in kilometers
 #--------------------------------------------------------------------------------------------------------------------------------*

def cby_getdist(cby_from,cby_to):

    cby_fr_latlon = ()
    cby_to_latlon = ()
    lcl_msgtxt = ""

    try:
        cby_fr_latlon = cby_getcoords(cby_from)
    except:
        lcl_msgtxt = "Error with from location"   
    try:
        cby_to_latlon = cby_getcoords(cby_to)
    except:
        lcl_msgtxt = "Error with to location"
        
    dist = cby_getgeodist(cby_fr_latlon,cby_to_latlon)
    
    return(dist,lcl_msgtxt)

 
 #--------------------------------------------------------------------------------------------------------------------------------*
 # Return Latitude and Longitude Coordinates for given address using geopy utilities
 #--------------------------------------------------------------------------------------------------------------------------------*

def cby_getcoords(inputaddr):

    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent='User-Agent')
    location = geolocator.geocode(inputaddr)
    return((location.latitude, location.longitude))

 #--------------------------------------------------------------------------------------------------------------------------------*
 # Calculate & return geodesic distance in kilometers between two lat/lon locations using geopy utilities
 #--------------------------------------------------------------------------------------------------------------------------------*

def cby_getgeodist(frcoord,tocoord):

    from geopy.distance import geodesic
    return(geodesic(frcoord, tocoord).kilometers)

 #--------------------------------------------------------------------------------------------------------------------------------*
 # Look up and return GHG emmissions (gc02e/km) for mode/entity 
 #--------------------------------------------------------------------------------------------------------------------------------*
def cby_getCo2Km(cby_mode):
     return(dict_Co2.get(cby_mode))


dict_Co2 = {'Entity': 'GHG emissions (gCO2e/km)', 'Black cab (taxi)': 0.21176, 'Bus': 0.10471, 'Coach': 0.02779, 
'Diesel car, 2 passengers': 0.085305, 'Diesel car, 4 passengers': 0.0426525, 'Domestic flight': 0.25493,
'Eurostar (international rail)': 0.00597, 'Ferry (car passenger)': 0.129518, 'Ferry (foot passenger)': 0.018738,
'Large car (diesel)': 0.20947, 'Large car (hybrid)': 0.13177, 'Large car (petrol)': 0.28295,
'Large car (plug-in hybrid electric)': 0.07731, 'Large electric vehicle (UK electricity)': 0.06688, 'Light rail and tram': 0.03508,
'London Underground': 0.03084, 'Long-haul flight (business class)': 0.43446, 'Long-haul flight (economy)': 0.14981,
'Long-haul flight (economy+)': 0.2397, 'Long-haul flight (first class)': 0.59925, 'Medium car (diesel)': 0.17061,
'Medium car (hybrid)': 0.10895, 'Medium car (petrol)': 0.19228, 'Medium car (plug-in hybrid electric)': 0.07083, 
'Medium electric vehicle (UK electricity)': 0.05317, 'Motorcycle (large)': 0.13501, 'Motorcycle (medium)': 0.10289,
'Motorcycle (small)': 0.08445, 'National rail': 0.04115, 'Petrol car, 2 passengers': 0.09614, 'Petrol car, 4 passengers': 0.04807,
'Short-haul flight (business class)': 0.2336, 'Short-haul flight (economy)': 0.15573, 'Small car (diesel)': 0.14208,
'Small car (hybrid)': 0.1052, 'Small car (petrol)': 0.15371, 'Small car (plug-in hybrid electric)': 0.02935,
'Small electric vehicle (UK electricity)': 0.04567, 'Taxi': 0.15018}


if __name__ == "__main__": 
    main()
    lcl_msgtxt = ' ' 
else: 
    # reading under parms from another source, presumably?
    main('','','',False,'')
