#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et


def get_onward(elem):
    """
    Parse <OnwardPricedItinerary>...
    :param elem: [STRING] xml-data
    :return: [LIST]
        [route, [sub_route_1, sub_route_2, ...]]
    """

    out = []
    for flights in elem:

        # SUBROUTES
        sub_flights = []
        for j, flight in enumerate(flights):

            sub_flights.append({})
            for el in flight:
                if el.tag == "Carrier":
                    sub_flights[j][el.tag] = el.attrib.get("id")
                else:
                    sub_flights[j][el.tag] = str(el.text).strip()

        # ROUTE
        source = sub_flights[0]["Source"]
        destination = sub_flights[-1]["Destination"]
        time_depature = sub_flights[0]["DepartureTimeStamp"]
        time_arrival = sub_flights[-1]["ArrivalTimeStamp"]
        flight_numbers = [i["FlightNumber"] for i in sub_flights]
        sub_routes = [(i["Source"], i["Destination"]) for i in sub_flights]

        key = "{}_{}".format(
            source,
            destination,
        )
        out.append(key)
        out.append([time_depature, time_arrival, flight_numbers, sub_routes])
    return out


def get_flights(_file):
    """
    Parse <PricedItineraries><Flights>...
    :param _file: [STRING] path to file xml-file
    :return: [DICT]
    """

    with open(_file, "r") as f:
        xml_data = f.read()

    if not xml_data:
        print "Empty file"
        return

    root = Et.fromstring(xml_data)
    xpath = ".//PricedItineraries/Flights"

    out = {}
    for flights in root.findall(xpath):
        flight = None
        sum_price = None
        for elem in flights:
            if elem.tag == "OnwardPricedItinerary":
                flight = get_onward(elem)
            if elem.tag == "Pricing":
                sum_price = sum(
                    [float(price.text) for price in elem]
                )
        route = flight[0]
        flight[1].append(sum_price)
        if route not in out:
            out[route] = [flight[1]]
        else:
            out[route].extend([flight[1]])
    return out


def show_diff(f_1, f_2):
    """
    Compare Flights from two xml-files
    :return: [DICT]
        difference for each route
    """

    out_diff = {}

    for route, flights_list in get_flights(f_1).iteritems():

        out_diff[route] = []

        for val in get_flights(f_2)[route]:
            if val not in flights_list:
                out_diff[route].append(val)

    return out_diff


if __name__ == "__main__":

    xml_1 = "RS_Via-3.xml"
    xml_2 = "RS_ViaOW.xml"

    for k, v in show_diff(xml_1, xml_2).iteritems():
        print k
        print v
