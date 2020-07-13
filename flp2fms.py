#! /usr/bin/env python
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import click

ns1 = {"flp": "http://www8.garmin.com/xmlschemas/FlightPlan/v1"}

wp_types = {"AIRPORT": 1, "NDB": 2, "INT": 11, "VOR": 3}

header_v3 = "I\n3 version\n1"
header_v11 = "I\n\1100 Version\nCycle 1710"
dwnld_dir = "/mnt/c/Users/artgo/Downloads/"
fms_dir = "/mnt/c/X-Plane 11/Output/FMS plans"


def setup(fplplan):
    fname = dwnld_dir + fplplan + ".fpl"
    tree = ET.parse(fname)
    root = tree.getroot()
    route = root.find("flp:route", ns1)
    route_name = route.find("flp:route-name", ns1)
    print(f"Raw route name: {route_name.text}")
    rtpts = route.findall("flp:route-point", ns1)
    wpts = root.find("flp:waypoint-table", ns1)
    if "/" in route_name:
        route_name = route_name.text.replace("/", "-")
    else:
        route_name = route_name.text.split()
        route_name = "-".join(route_name)
    return route_name, rtpts, wpts


def elt_child_text(elt, which_child):
    child = elt.find(f"flp:{which_child}", ns1)
    return child.text


def wpt2fms(wpt):
    wpt_type = elt_child_text(wpt, "type")
    wpt_fms = {
        "type": wp_types[wpt_type],
        "id": elt_child_text(wpt, "identifier"),
        "lat": elt_child_text(wpt, "lat"),
        "lon": elt_child_text(wpt, "lon"),
        # "elev": elt_child_text(wpt, "elevation"),
    }
    return wpt_fms


def make_wptid2wpt_table(wpts):
    return {elt_child_text(wpt, "identifier"): wpt for wpt in wpts}


def rpt2cmpts(rtpt, wpt_lkup):
    """convert rtpt to its constituent elements

    Args:
        rtpt (rtpt): route point
        wpt_lkup (wpt lkup table): waypoint lookup table

    Returns:
        typ, ident, lat, lon, elev

    """
    wptid = elt_child_text(rtpt, "waypoint-identifier")
    wpt = wpt_lkup[wptid]
    wpt_fms = wpt2fms(wpt)
    typ = wpt_fms["type"]
    ident = wpt_fms["id"]
    lat = wpt_fms["lat"]
    lon = wpt_fms["lon"]
    # ver 11 files have extra column
    # 1 KCUB ADEP 4.000000 33.970470 -80.995247
    # ADEP ADES or DRCT, elevation follows in 4th col
    # print(f"type {typ}", type(typ))
    elev = 0.00000
    if typ == 1:
        try:
            elev = elt_child_text(wpt, "elevation")
        except AttributeError:
            elev = "0.00000"
    return typ, ident, lat, lon, elev



def print_fms_rtpt(rtpt, wpt_lkup, f):
    typ, ident, lat, lon, elev = rpt2cmpts(rtpt, wpt_lkup)
   
    print(f"{typ} {ident} {elev} {lat} {lon}", file=f)
    

def print_fms(rtpts, wpt_lkup, f=sys.stdout):
    print(header_v3, file=f)
    print(f"{len(rtpts)-1}", file=f)
    for rtpt in rtpts:
        print_fms_rtpt(rtpt, wpt_lkup, f)


@click.group()
def cli():
    pass


def output_preamble(fplplan):
    print("Input plan name:", fplplan)
    route_name, rtpts, wpts = setup(fplplan)
    print(f"Route name: {route_name}")
    wpt_lookup_table = make_wptid2wpt_table(wpts)
    fname = f"{fms_dir}/{route_name}.fms"
    print(f"Writing to file {fname}")
    return fname, rtpts, wpt_lookup_table


@cli.command()
@click.argument("fplplan")
def decode(fplplan):
    fname, rtpts, wpt_lookup_table = output_preamble(fplplan)
    print_fms(rtpts, wpt_lookup_table)
    with open(fname, "w") as f:
        print_fms(rtpts, wpt_lookup_table, f)


@cli.command()
def files():
    fms_files = [file for file in os.listdir(dwnld_dir) if file.endswith(".fpl")]
    print(fms_files)



def build_gtn(rtpts, wpt_lkup, f=sys.stdout):
    output = "FPN/RI"
    fix = ":F:"
    for rtpt in rtpts:
        typ, ident, lat, lon, elev = rpt2cmpts(rtpt, wpt_lkup)
        output = output + fix + ident
    return output

@cli.command()
@click.argument("fplplan")
def gtn(fplplan):
    fname, rtpts, wpt_lookup_table = output_preamble(fplplan)
    output = build_gtn(rtpts, wpt_lookup_table, fname)
    print(output)




# if __name__ == "__main__":
#     cli()  # pylint: disable=no-value-for-parameter
