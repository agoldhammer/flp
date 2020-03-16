import xml.etree.ElementTree as ET

ns1 = {"flp": "http://www8.garmin.com/xmlschemas/FlightPlan/v1"}

wp_types = {
    "AIRPORT": 1,
    "NDB": 2,
    "INT": 11,
    "VOR": 3}

header = 'I\n1100 Version\n'

def setup():
    tree = ET.parse('KJFK.fpl')
    root = tree.getroot()
    route = root.find("flp:route", ns1)
    rtpts = route.findall("flp:route-point", ns1)
    wpts = root.find("flp:waypoint-table", ns1)
    return rtpts, wpts

def elt_child_text(elt, which_child):
    child = elt.find(f'flp:{which_child}', ns1)
    return child.text

def wpt2fms(wpt):
    wpt_type = elt_child_text(wpt, 'type')
    wpt_fms = {
        "type": wp_types[wpt_type],
        "id": elt_child_text(wpt, 'identifier'),
        "lat": elt_child_text(wpt, 'lat'),
        "lon": elt_child_text(wpt, 'lon')
    }
    return wpt_fms


def make_wptid2wpt_table(wpts):
    return {elt_child_text(wpt, "identifier"): wpt
     for wpt in wpts}


def print_fms_rtpt(rtpt, wpt_lkup):
    wptid = elt_child_text(rtpt, "waypoint-identifier")
    wpt = wpt_lookup_table[wptid]
    wpt_fms = wpt2fms(wpt)
    typ = wpt_fms['type']
    ident = wpt_fms['id']
    lat = wpt_fms['lat']
    lon = wpt_fms['lon']
    print(f'{typ} {ident} 0.000000 {lon} {lat}')

def print_fms(rtpts, wpt_lkup):
    print(header)
    print(f"NUMENR {len(rtpts)}")
    for rtpt in rtpts:
        print_fms_rtpt(rtpt, wpt_lkup)

if __name__ == "__main__":
    rtpts, wpts = setup()
    wpt_lookup_table = make_wptid2wpt_table(wpts)
    print_fms(rtpts, wpt_lookup_table)
