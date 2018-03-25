from datetime import datetime
import math
import logging
import flightDB

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s: %(levelname)s: %(message)s')

#in order to query for flights we must have a list to go against
currentFlightList = {}

def setAvailableFlightList(availableFlights):
    global currentFlightList

    currentFlightList = availableFlights
    logging.debug('setAvailableFlight: setting new flight list')
    logging.debug('setAvailableFlight: ' + str(len(currentFlightList)) + ' outbound/inbound flights are currently available')
    logging.debug('setAvailableFlight: keys: ' + str(currentFlightList.keys()))

def __getCheapestOutboundFlight(outboundList):
    return outboundList[0]

def __getCheapestInboundFlight(inboundList):
    return inboundList[0]

def __compileFlightSegments(flightIDs):
    # flightIDs is a list
    # we need to create a new flight dict... outbound key set to any match we find and inbound the same
    flights = {
        'flights' : []
    }

    for id in flightIDs:
        newFlight = {}
        logging.debug('flightSegments: Looking for an outbound flight with id: ' + id['outbound']['id'])
        if (id['outbound']['id']) in currentFlightList.keys():
            logging.debug('found a flight matching this id... adding to flight list')
            newFlight['outbound'] = currentFlightList.get(id['outbound']['id'])
            newFlight['outbound']['one_way_price'] = id['outbound']['one_way_price']
        if (id['inbound']['id']) in currentFlightList.keys():
            logging.debug('found a flight matching this id... adding to flight list')
            newFlight['inbound'] = currentFlightList.get(id['inbound']['id'])
            newFlight['inbound']['one_way_price'] = id['inbound']['one_way_price']

        # Total the total cost for this roundtrip
        newFlight['round_trip_cost'] = newFlight['outbound']['one_way_price'] + newFlight['inbound']['one_way_price']

        flights['flights'].append(newFlight)

    return flights

def getCheapestRoundTripFlights(outboundList, inboundList, numFlights=5):
    #
    # Let's use 5 as an example. The first 5 items in the outbound list will have the 5 cheapest one-way outbounds
    # We can make a list as such: Get a list of those 5 flights and then add the first inbound to each
    # So Outbound1 + Inbound1 and then Outbound2 + Inbound2 and so on... those are the five cheapest flights
    # that match our criteria. Still - all we have are flight IDs and prices so we need the actual flight info
    #
    # numFlights = number of cheapest flights to return. Default is 5 cheapest
    #Using an OrderedDict here to preserve the order of the flights for display purposes

    outboundFlights = outboundList[:numFlights]
    inboundFlights = inboundList[0]
    global currentFlightList

    flights = []

    for flight in range(0, numFlights):
        newFlight = {}

        logging.debug('Trying to add this flight: ' + outboundFlights[flight]['flight'])
        newFlight['outbound'] = {
            'id' : outboundFlights[flight]['flight'],
            'one_way_price' : outboundFlights[flight]['one_way_price']
        }

        newFlight['inbound'] = {
            'id' : inboundFlights['flight'],
            'one_way_price' : inboundFlights['one_way_price']
        }

        logging.debug('getCheapest: adding ' + str(newFlight) + ' to final list')
        flights.append(newFlight)

    # At this stage flights is a list of dicts that only has inbound and outbound flight IDs
    # We need to write a method that will accept this list as an input and then return the full flights

    return __compileFlightSegments(flights)

def getCheapestReturnFlightID(inbound_flights):
    #Skiplagged data is already sorte by cheapest first so we can grab the first one
    return inbound_flights[0]['flight']

def getCheapestReturnFlightsID(inbound_flights, numFlights=5):
    #This method allows the caller to determine how many inbound flights to return. Default is 5
    #Returns a list of flights
    cheapestReturnFlights = []
    for flight in inbound_flights:
        cheapestReturnFlights.append(flight['flight'])
    return inbound_flights[:numFlights]

def getFlightByID(flightList, id):
    #all_flights = complete list
    #flight ID = 7 digit alpha; must be string
    return flightList[id]

def getFlightsByID(all_flights, selectedFlights):
    #selectedFlights is a list of flight IDs
    #this method should return a dict of flights
    print('getFlightsByID: processing list: ' + str(selectedFlights))
    if(not isinstance(selectedFlights, list)):
        raise ValueError('selectedFlights arg must be of type list')
    elif (not isinstance(all_flights, dict)):
        raise ValueError('all_flights arg must be of type dict')
    else:
        flightList = {}
        missingFlights = []
        flightList['foundAllFlights'] = 'true'
        for flightId in selectedFlights:
            try:
                flightList[flightId] = getFlightByID(all_flights, flightId)
            except KeyError:
                #Update flag to let user know we could not find everything
                flightList['foundAllFlights'] = 'false'
                #Add flight id to missingFlights list
                missingFlights.append(flightId)
                flightList['missingFlightIDs'] = missingFlights
        return flightList

def getTotalNumFlights(all_flights):
    return str(len(all_flights))

def sanitizeMultiStopLongFlights(flightList, maxDuration=21600):
    """This function takes a dict (all_flights) and removes extraneous data
       First, remove any flight with more than one connection flight. Second, filter out flights that total more than 6 hours of total flying time"""
    ## TODO: add type checking; this method should only accept dictionaries

    modifiedLists = []

    #Remove flights with more than 1 stop and with a total duration of 5 or more hours
    logging.debug('sanitizeMultiStopLongFlights: ' + 'Sanitizing list to remove multi-stop and long duration flights...')
    sanitizedList = {k:v for k,v in flightList.items() if v['count'] <= 2 and v['duration'] <= maxDuration }
    logging.debug('sanitizeMultiStopLongFlights: ' + 'Size of result set reduced from ' + str(len(flightList)) + ' to ' + str(len(sanitizedList)))

    #We need to use this list to filter the separate outbound/inbound lists to make sure we arent pulling them in any future queries
    discardedList = {k:v for k,v in flightList.items() if v['count'] > 2 or v['duration'] > maxDuration }
    logging.debug('sanitizeMultistopLongFlights: ' + 'Size of discarded list is ' + str(len(discardedList)))

    modifiedLists.append(sanitizedList)
    modifiedLists.append(discardedList)
    return modifiedLists

def sanitizeInOutbound(flightsInbound, flightsOutbound, flightsToRemove):

    filteredInbound = []
    filteredOutbound = []
    logging.debug('sanitizeInOutBound: Removing flights that have too many connections or are too long')
    for flight in flightsInbound:
        if flight['flight'] not in flightsToRemove.keys():
            if "one_way_price" in flight.keys():
                logging.debug('sanitizeInOutbound: flight ' + str(flight['flight']) + ' is being added to the inbound list')
                filteredInbound.append(flight)
            else:
                logging.warning('Inbound flight ' + flight[
                    'flight'] + ' does not have a price. REMOVING from list')

    for flight in flightsOutbound:
        if flight['flight'] not in flightsToRemove.keys():
            if "one_way_price" in flight.keys():
                logging.debug('sanitizeInOutbound: flight ' + str(flight['flight']) + ' is being added to the outbound list')
                filteredOutbound.append(flight)
            else:
                logging.warning('removeFlightsWithoutPrice: Inbound flight ' + flight[
                    'flight'] + ' does not have a price. REMOVING from list')

    logging.debug('sanitizeInOutBound: ' + str(len(filteredInbound)) + ' flights OK for inbound')
    logging.debug('sanitizeInOutBound: ' + str(len(filteredOutbound)) + ' flights OK for outbound')

    #return a list [filteredInboud, filteredOutbound]
    return filteredInbound, filteredOutbound


def removeDataKeyFromFlights(flightList):
    """ There is a key called "data" in the outbound flight list. It's a long value that clutters the display so we use
        this method to remove it """
    ## TODO: add type checking; this method should only accept dictionaries
    if (isinstance(flightList, dict)):
        print('removeDataKeyFromFlights: flightList is type dict: Scrubbing data...')
        for flight in flightList.items():
            #flight is a tuple. Index 1 contains the flight dict where we need to delete the data key
            del flight[1]['data']
        return flightList
    elif (isinstance(flightList, list)):
        print('RemoveDataKeyFromFlights: flightList is type list: Scrubbing data...')
        for flight in flightList:
            #flight is a dict. Simply remove the key
            del flight['data']
        return flightList

def getTripSummary(trip):
    ## TODO: this only prints atm; need to format something prettier
    print('Flight data for: ')
    print('From: ' + trip['from']['airports'][0])
    print('To: ' + trip['to']['airports'][0])

def displayTrips(roundtrips):

    flightIndex = 1
    for trip in roundtrips['flights']:
        print('')
        print('Flight #' + str(flightIndex) + '---------')
        print('OUTBOUND')
        for segment in range(0, trip['outbound']['count']):
            #print(str(trip['outbound']['segments'][segment]['airline']) + ' ' + str(trip['outbound']['segments'][segment]['flight_number']))
            leg = trip['outbound']['segments'][segment]
            displaySegmentInfo(leg)
        print('INBOUND')
        for segment in range(0, trip['inbound']['count']):
            leg = trip['inbound']['segments'][segment]
            displaySegmentInfo(leg)
        print('Total roundtrip cost: $ ' + formatFlightCost(trip['round_trip_cost']))
        flightIndex += 1
    return None

def formatFlightCost(priceInPennies):
    return '${:,.2f}'.format(priceInPennies / 100)

def formatDuration(durationInSeconds):
    # input is int
    # Example: duration = 6960 seconds = 116 mins = 1.9333 hours
    hourValue = math.floor((durationInSeconds / 60) / 60) # equals 1.933 and then floored to 1
    minuteValue = int((durationInSeconds / 60) % 60)

    formattedValue = '{}h{}m'.format(hourValue, minuteValue)

    return formattedValue

def displaySegmentInfo(segment):

    airline = segment['airline']
    flight_number = segment['flight_number']
    outboundAirport = segment['departure']['airport']
    outboundDepTime = segment['departure']['time']
    outboundDuration = segment['duration']
    inboundAirpot = segment['arrival']['airport']
    arrivalTime = segment['arrival']['time']

    #Remove timezone data from times
    outboundDepTime = outboundDepTime[:-6]
    outboundDepTime = datetime.strptime(outboundDepTime, '%Y-%m-%dT%H:%M:%S')
    outTime = outboundDepTime.strftime('%m/%d/%y - %H:%M')

    arrivalTime = arrivalTime[:-6]
    arrivalTime = datetime.strptime(arrivalTime, '%Y-%m-%dT%H:%M:%S')
    inTime = arrivalTime.strftime('%H:%M')

    #format duration to 2 decimal float
    outboundDuration = formatDuration(outboundDuration)

    # UA 1234 - EWR -> CHS - 8:00 -> 12:00 (Duration: 4)
    print ('[{} {}] {} -> {} - {} -> {} (Duration: {})'.format(airline, flight_number, outboundAirport, inboundAirpot,
                                                              outTime, inTime, outboundDuration))

def prepareFlightRecords(flightList):
    flights = flightList.get('flights')
    finalList = []

    for flight in flights:
        flightRecord = {}

        for key in flight.keys():
            if key == 'outbound':
                legCount = flight[key]['count']
                for k, v in flight[key].items():
                    if k == 'segments':
                        print('Collecting outbound segment:')
                        for idx, segment in enumerate(flight[key][k]):  # for segment in flight[key][k]:
                            # legCount = 1 for nonstop and 2 for connecting

                            # FIRST FLIGHT DATA
                            if idx == 0:
                                flightRecord['departFlightNum'] = str(
                                    segment['airline'] + ' ' + str(segment['flight_number']))
                                flightDateTime = segment['departure']['time']
                                # flightRecord['departFlightDate'] = flightDateTime[:10]
                                flightRecord['departFlightDate'] = flightDateTime[5:7] + '/' + flightDateTime[
                                                                                               8:10] + '/' + flightDateTime[
                                                                                                             2:4]
                                flightRecord['departFlightTime'] = flightDateTime[11:16]
                                if legCount == 1:
                                    flightRecord['departRoute'] = str(
                                        segment['departure']['airport'] + '-' + segment['arrival']['airport'])
                                    flightRecord['connectingFlightOut'] = ''

                                else:
                                    flightRecord['departRoute'] = str(segment['departure']['airport'] + '-')
                            # CONNECTING FLIGHT DATA
                            if idx == 1:
                                flightRecord['connectingFlightOut'] = str(
                                    segment['airline'] + ' ' + str(segment['flight_number']))
                                flightRecord['departRoute'] += str(
                                    segment['departure']['airport'] + '-' + segment['arrival']['airport'])

            if key == 'inbound':
                legCount = flight[key]['count']
                for k, v in flight[key].items():
                    if k == 'segments':
                        print('Collecting inbound segment:')
                        for idx, segment in enumerate(flight[key][k]):  # for segment in flight[key][k]:
                            # legCount = 1 for nonstop and 2 for connecting
                            # FIRST FLIGHT DATA
                            if idx == 0:
                                flightRecord['returnFlightNum'] = str(
                                    segment['airline'] + ' ' + str(segment['flight_number']))
                                flightDateTime = segment['departure']['time']
                                # flightRecord['returnFlightDate'] = flightDateTime[:10]
                                flightRecord['returnFlightDate'] = flightDateTime[5:7] + '/' + flightDateTime[
                                                                                               8:10] + '/' + flightDateTime[
                                                                                                             2:4]
                                flightRecord['returnFlightTime'] = flightDateTime[11:16]
                                if legCount == 1:
                                    flightRecord['returnRoute'] = str(
                                        segment['departure']['airport'] + '-' + segment['arrival']['airport'])

                                else:
                                    flightRecord['returnRoute'] = str(segment['departure']['airport'] + '-')
                            # CONNECTING FLIGHT DATA
                            if idx == 1:
                                flightRecord['connectingFlightIn'] = str(
                                    segment['airline'] + ' ' + str(segment['flight_number']))
                                flightRecord['returnRoute'] += str(segment['departure']['airport'] + '-' +
                                                                   segment['arrival']['airport'])
            if key == 'round_trip_cost':
                flightRecord['price'] = '{:,.2f}'.format((flight.get(key)) / 100)
        print('finished processing flight: ' + str(flightRecord))
        finalList.append(flightRecord)

    return finalList

def addFlights(allRoundtrips):
    flights = prepareFlightRecords(allRoundtrips)

    flightDB.addFlights(flights)

    flightDB.closeConnection()
    return None

