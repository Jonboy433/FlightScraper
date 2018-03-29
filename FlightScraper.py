import argparse
import json
import requests
from tkinter import *

def validAirportCode(iata_code):
    airport = iata_code
    if ((len(airport) != 3)) or airport.isdigit():
        raise argparse.ArgumentTypeError('You must enter a valid 3 digit airport code')
    return airport

def validFlightDate(date):
    flight_date = date

    if (len(flight_date) != 10) or flight_date.isdigit():
        raise argparse.ArgumentTypeError('Please enter a valid date in format YYYY-MM-DD')
    # valid date: 2018-10-12
    year = flight_date[0:4]
    month = flight_date[5:7]
    day = flight_date[8:10]
    dash_one = flight_date[4]
    dash_two = flight_date[7]

    if (not year.isdigit()) or (not month.isdigit()) or (not day.isdigit()):
        raise argparse.ArgumentTypeError('Date values must be numeric')
    if(dash_one != '-') and (dash_two != '-'):
        raise argparse.ArgumentTypeError('You are missing the dashes')
    if(int(month) < 1 or int(month) > 12):
        raise argparse.ArgumentTypeError('Please enter a valid month: 1-12')
    if(int(day) < 1 or int(day) > 31):
        #We will add checking for shorter/longer months in future release
        raise argparse.ArgumentTypeError('Please enter a valid day of the month: 1-31')
    if(int(year) < 2018):
        raise argparse.ArgumentTypeError('You cannot search for flights earlier than today')

    return flight_date

# Allow caller to prevent results from being stored in DB
def boolFlag(flag):
    if flag.lower() in ('yes', 'true', 'y'):
        return True
    elif flag.lower() in ('no', 'false', 'n'):
        return False
    else:
        raise argparse.ArgumentTypeError('You must enter a boolean value')

#Set default value to false
disable_db = False

#Set default value to false
show_unfiltered_results = False

parser = argparse.ArgumentParser()
parser.add_argument('--f', metavar='From', default='EWR', help='Origin airport', type=validAirportCode)
parser.add_argument('--t', metavar='To', default='CHS', help='Destination airport', type=validAirportCode)
parser.add_argument('--dep', metavar='Departure Date', default='2018-10-12', help='Departure date e.g. 2018-09-02', type=validFlightDate)
parser.add_argument('--ret', metavar='Return Date', default='2018-10-14', help='Return date e.g. 2018-09-05', type=validFlightDate)
parser.add_argument('--d', metavar='DisableDB', default=False, type=boolFlag)
args = parser.parse_args()

#moving import here for now to prevent db connection on module load failure
import FlightHelper as fh

from_airport = args.f
to_airport = args.t
dep_date = args.dep
ret_date = args.ret
disable_db = args.d

SEARCH_URI='https://skiplagged.com/api/search.php?from={}&to={}&depart={}&return={}&format=v2'.format(from_airport, to_airport, dep_date, ret_date)

# Commented out to save time while testing...
res = requests.get(SEARCH_URI, headers = {'User-Agent':'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.84 Safari/537.36'})
flightData = json.loads(res.text)


#Below works if we ever want to read json from file instead
#with open('flightData.json') as json_file:
#    flightData = json.load(json_file)


# list of airlines found in search results
airlines = {}
# list of cities found in all itineraries
cities = {}
# list of airports found
airports = {}
#list of all one-way flights (both outbound and inbound)
flights = {}
# list of all outbound flights including the outbound price AND MIN ROUNDTRIP PRICE and flight ID
flightsOutbound = []
# list of all inbound flights including JUST the inbound price and flight ID
flightsInbound = []
# broken down into outbound and inbound flights including the one way price of the segment and flight ID
itineraries = {}

trip = {}

for key, value in flightData.items():
    if (key == 'airlines'):
        airlines = value
    if (key == 'cities'):
        cities = value
    if (key == 'airports'):
        airports = value
    if (key == 'flights'):
        flights = value
    if (key == 'itineraries'):
        flightsOutbound = value['outbound']
        flightsInbound = value['inbound']
    if (key == 'info'):
        trip = value

#A little spring cleaning... remove the data value since it clutters the display
flights = fh.removeDataKeyFromFlights(flights)
flightsInbound = fh.removeDataKeyFromFlights(flightsInbound)
flightsOutbound = fh.removeDataKeyFromFlights(flightsOutbound)

#Sanitize the flights by removing the long flights; flights value still retains original list if necessary
sanitizedFlights = fh.sanitizeMultiStopLongFlights(flights)
flightsMatchQuery = sanitizedFlights[0]
fh.setAvailableFlightList(flightsMatchQuery)

flightsDontMatchQuery = sanitizedFlights[1]


#Now sanitize the in/outbound by removing all inbound and outbound flights that are too long, have too many connections, or no one way price
filteredInbound, filteredOutbound = fh.sanitizeInOutbound(flightsInbound, flightsOutbound, flightsDontMatchQuery)

#At this point sanitizedFlights, filteredInbound, and filteredOutbound have the flight data we want to work with

#print(str(fh.getCheapestRoundTripFlight(flightsOutbound, flightsInbound, flights)))

roundTripResults = fh.getCheapestRoundTripFlights(filteredOutbound, filteredInbound)

fh.displayTrips(roundTripResults)

##################
if (show_unfiltered_results):
    fh.setAvailableFlightList(flights)
    roundTripResults = fh.getCheapestRoundTripFlights(flightsOutbound, flightsInbound)
    fh.displayTrips(roundTripResults)


alertPrice = 44000

def setAlertPrice(price):
    global alertPrice
    alertPrice = price
def getAlertPrice():
    global alertPrice
    return alertPrice

alertFlights = fh.getFlightsByAlertPrice(roundTripResults, alertPrice)

root = Tk()
root.title('Flight Results')
T = Text(root)
T.pack()
T.insert(END,fh.getTrips(alertFlights))
mainloop()

if (not disable_db):
    fh.addFlights(roundTripResults)




