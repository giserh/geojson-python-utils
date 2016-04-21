import json
import math


def linestrings_intersect(line1, line2):
    """
    To valid whether linestrings from geojson are intersected with each other.

    Keyword arguments:
    line1 -- first line geojson object
    line2 -- second line geojson object

    if(line1 intersects with other) return intersect point array else empty array
    """
    intersects = []
    for i in range(0, len(line1['coordinates']) - 1):
        for j in range(0, len(line2['coordinates']) - 1):
            a1_x = line1['coordinates'][i][1]
            a1_y = line1['coordinates'][i][0]
            a2_x = line1['coordinates'][i + 1][1]
            a2_y = line1['coordinates'][i + 1][0]
            b1_x = line2['coordinates'][j][1]
            b1_y = line2['coordinates'][j][0]
            b2_x = line2['coordinates'][j + 1][1]
            b2_y = line2['coordinates'][j + 1][0]
            ua_t = (b2_x - b1_x) * (a1_y - b1_y) - (b2_y - b1_y) * (a1_x - b1_x)
            ub_t = (a2_x - a1_x) * (a1_y - b1_y) - (a2_y - a1_y) * (a1_x - b1_x)
            u_b = (b2_y - b1_y) * (a2_x - a1_x) - (b2_x - b1_x) * (a2_y - a1_y)
            if not u_b == 0:
                u_a = ua_t / u_b
                u_b = ub_t / u_b
                if 0 <= u_a and u_a <= 1 and 0 <= u_b and u_b <= 1:
                    intersects.append({'type': 'Point', 'coordinates': [a1_x + u_a * (a2_x - a1_x), a1_y + u_a * (a2_y - a1_y)]})
    # if len(intersects) == 0:
    #     intersects = False
    return intersects


def bbox_around_polycoords(coords):
    """
    bounding box
    """
    x_all = []
    y_all = []

    for first in coords[0]:
        x_all.append(first[1])
        y_all.append(first[0])

    return [min(x_all), min(y_all), max(x_all), max(y_all)]


def point_in_bbox(point, bounds):
    """
    valid whether the point is inside the bounding box
    """
    return not(point['coordinates'][1] < bounds[0] or point['coordinates'][1] > bounds[2] \
     or point['coordinates'][0] < bounds[1] or point['coordinates'][0] > bounds[3])


def pnpoly(x, y, coords):
    """
    the algorithm to judge whether the point is located in polygon
    reference: https://www.ecse.rpi.edu/~wrf/Research/Short_Notes/pnpoly.html#Explanation
    """
    vert = [[0, 0]]

    for coord in coords:
        for node in coord:
            vert.append(node)
        vert.append(coord[0])
        vert.append([0, 0])

    inside = False

    i = 0
    j = len(vert) - 1

    while i < len(vert):
        if ((vert[i][0] > y) != (vert[j][0] > y)) and (x < (vert[j][1] - vert[i][1]) \
         * (y - vert[i][0]) / (vert[j][0] - vert[i][0]) + vert[i][1]):
            inside = not inside
        j = i
        i += 1

    return inside


def _point_in_polygon(point, coords):
    inside_box = False
    for coord in coords:
        if inside_box:
            break
        if point_in_bbox(point, bbox_around_polycoords(coord)):
            inside_box = True
    if not inside_box:
        return False

    inside_poly = False
    for coord in coords:
        if inside_poly:
            break
        if pnpoly(point['coordinates'][1], point['coordinates'][0], coord):
            inside_poly = True
    return inside_poly

def point_in_polygon(point, poly):
    """
    valid whether the point is located in a polygon

    Keyword arguments:
    point -- point geojson object
    poly  -- polygon geojson object

    if(point inside poly) return true else false
    """
    coords = [poly['coordinates']] if poly['type'] == 'Polygon' else poly['coordinates']
    return _point_in_polygon(point, coords)

def point_in_multipolygon(point, multipoly):
    """
    valid whether the point is located in a mulitpolygon (donut polygon is not supported)

    Keyword arguments:
    point      -- point geojson object
    multipoly  -- multipolygon geojson object

    if(point inside multipoly) return true else false
    """
    coords_array = [multipoly['coordinates']] if multipoly['type'] == "MultiPolygon" else multipoly['coordinates']

    for coords in coords_array:
        if _point_in_polygon(point, coords):
            return True

    return False

def number2radius(number):
    """
    convert degree into radius
    """
    return number*math.pi /180

def number2degree(number):
    """
    convert radius into degree
    """
    return number* 180/math.pi

#drawCircle

#rectangleCentroid

#pointDistance

#geometryWithinRadius

#area

#centroid

#simplify

#destinationPoint

def test():
    """
    test for geojson-python-utils
    """
    #linestrings intersect
    diagonal_up_str = '{ "type": "LineString","coordinates": [[0, 0], [10, 10]]}'
    diagonal_down_str = '{ "type": "LineString","coordinates": [[10, 0], [0, 10]]}'
    far_away_str = '{ "type": "LineString","coordinates": [[100, 100], [110, 110]]}'
    diagonal_up = json.loads(diagonal_up_str)
    diagonal_down = json.loads(diagonal_down_str)
    far_away = json.loads(far_away_str)
    print "two lines intersect:"
    print linestrings_intersect(diagonal_up, diagonal_down)
    print "two lines do not intersect:"
    print linestrings_intersect(diagonal_up, far_away)

    #point in polygon
    in_str = '{"type": "Point", "coordinates": [5, 5]}'
    out_str = '{"type": "Point", "coordinates": [15, 15]}'
    box_str = '{"type": "Polygon","coordinates": [[ [0, 0], [10, 0], [10, 10], [0, 10] ]]}'
    in_box = json.loads(in_str)
    out_box = json.loads(out_str)
    box = json.loads(box_str)
    print "point inside box:  "
    print point_in_polygon(in_box, box)
    print "point outside box:"
    print point_in_polygon(out_box, box)

    #point in multipolygon
    point_str = '{"type": "Point", "coordinates": [0.5, 0.5]}'
    single_point_str = '{"type": "Point", "coordinates": [-1, -1]}'
    multipoly_str = '{"type":"MultiPolygon","coordinates":[[[[0,0],[0,10],[10,10],[10,0],[0,0]]],[[[10,10],[10,20],[20,20],[20,10],[10,10]]]]}'
    point = json.loads(point_str)
    single_point = json.loads(single_point_str)
    multipoly = json.loads(multipoly_str)
    print "point inside multipoly: "
    print  point_in_multipolygon(point, multipoly)
    print "point outside multipoly : "
    print point_in_multipolygon(single_point, multipoly)


if __name__ == '__main__':
    test()
