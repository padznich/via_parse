#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as Et


def get_itinerary(elem):
    """
    Parse <OnwardPricedItinerary> or <ReturnPricedItinerary>
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
        flight_numbers = [item["FlightNumber"] for item in sub_flights]
        sub_routes = [
            (item["Source"], item["Destination"]) for item in sub_flights
            ]

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
        onward_flight = None
        return_flight = None
        sum_price = None
        for elem in flights:
            if elem.tag == "OnwardPricedItinerary":
                onward_flight = get_itinerary(elem)
            if elem.tag == "ReturnPricedItinerary":
                return_flight = get_itinerary(elem)
            if elem.tag == "Pricing":
                sum_price = sum(
                    [float(price.text) for price in elem]
                )
        route = onward_flight[0]
        if return_flight:
            onward_flight[1].extend(return_flight[1])
            onward_flight[1].append(sum_price)
            if route not in out:
                out[route] = [onward_flight[1]]
            else:
                out[route].extend([onward_flight[1]])
        else:
            onward_flight[1].append(sum_price)
            if route not in out:
                out[route] = [onward_flight[1]]
            else:
                out[route].extend([onward_flight[1]])
    return out


def show_diff(f_1, f_2):
    """
    Compare Flights from file f_2 to  file f_1.
    If route from f_2 not in f_1, then add it to out_diff dictionary

    :param f_1: [STRING]
        Path to xml-file 1
    :param f_2: [STRING]
        Path to xml-file 2
    :return: [DICT]
        Difference between files
    """

    out_diff = {}
    f_1_dict = get_flights(f_1)
    f_2_dict = get_flights(f_2)

    for route, flights_list in f_1_dict.iteritems():

        out_diff[route] = []

        for val in f_2_dict[route]:
            if val not in flights_list:
                out_diff[route].append(val)

    return out_diff


if __name__ == "__main__":

    # Conf
    xml_file_1 = "RS_Via-3.xml"
    xml_file_2 = "RS_ViaOW.xml"

    # Main func
    for k, v in show_diff(xml_file_1, xml_file_2).iteritems():
        print k
        for i in v:
            print i
