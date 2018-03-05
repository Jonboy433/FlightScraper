import json
import requests
import FlightHelper as fh

# Commented out to save time while testing...
#res = requests.get('https://skiplagged.com/api/search.php?from=EWR&to=CHS&depart=2018-10-12&return=2018-10-14&format=v2&_=1519778653193',
#                   headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36'})
#flightData = json.loads(res.text)


#Below works if we ever want to read json from file instead
with open('flightData.json') as json_file:
    flightData = json.load(json_file)


# BELOW WORKS
#flightData = json.loads(res.text)


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


#Now sanitize the in/outbound by removing all inbound and outbound flights that are too long or have too many connections
filteredInbound, filteredOutbound = fh.sanitizeInOutbound(flightsInbound, flightsOutbound, flightsDontMatchQuery)


#At this point sanitizedFlights, filteredInbound, and filteredOutbound have the flight data we want to work with

#print(str(fh.getCheapestRoundTripFlight(flightsOutbound, flightsInbound, flights)))

roundTripResults = fh.getCheapestRoundTripFlights(filteredOutbound, filteredInbound)

fh.displayTrips(roundTripResults)

fh.addFlights(roundTripResults)




