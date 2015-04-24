"""Import GEO-Data to meinBerlin.

The functions are registered in setup.py
in setup.py.
"""


import sys
import os
import json
import re
import unicodedata

from pyramid.paster import bootstrap

from substanced.util import find_service

import transaction

from adhocracy_core.sheets.name import IName
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.pool import IPool
from adhocracy_core.resources.geo import multipolygon_meta
from adhocracy_core.sheets.geo import IMultiPolygon
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_sheet_field


def slugify(value):
    """slugify string."""
    value = unicodedata.normalize(
        'NFKD',
        value).encode(
        'ascii',
        'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def import_bezirksregions():
    """Get geodata for berlin's bezirksregions from FIS-Broker."""
    try:
        import_bezirke()
    except:
        pass

    call = 'ogr2ogr -s_srs EPSG:25833 -t_srs WGS84 -f geoJSON ' \
           '/tmp/bezirksregions.json WFS:"http://fbinter.stadt-berlin.de' \
           '/fb/wfs/geometry/senstadt/re_bezirksregion?TYPENAMES=GML2" ' \
           ' fis:re_bezirksregion'

    try:
        os.remove('/tmp/bezirksregions.json')
        print('Old file removed')
    except:
        print('No file to remove')

    try:
        os.system(call)
    except Exception:
        t, e = sys.exc_info()[:2]
        print(e)
        sys.exit()

    data = json.load(open('/tmp/bezirksregions.json', 'r'))

    env = bootstrap('./etc/development.ini')
    root = env['root']
    registry = env['registry']
    locations = find_service(root, 'locations')
    pool = get_sheet(root, IPool)
    params = {'depth': 3,
              'content_type': IMultiPolygon,
              'elements': 'content',
              }
    results = pool.get(params)
    bezirke = results['elements']
    lookup = {}
    for bezirk in bezirke:
        if (get_sheet_field(bezirk,
                            IMultiPolygon,
                            'administrative_division') == 'stadtbezirk'):
            name = (get_sheet_field(bezirk, IName, 'name'))
            lookup[name] = bezirk

    for feature in data['features']:

        geometry = feature['geometry']['coordinates']
        bezirk = feature['properties']['BEZIRK']
        bezirks_region_name = feature['properties']['BZR_NAME']
        type = feature['geometry']['type']
        if type == 'Polygon':
            geometry = [geometry]

        geosheet = {'coordinates': geometry,
                    'administrative_division': 'bezirksregion',
                    'part_of': lookup[slugify(bezirk)],
                    'type': 'MultiPolygon'}

        appstructs = {
            IName.__identifier__: {
                'name': slugify(bezirks_region_name)},
            IMultiPolygon.__identifier__: geosheet,
            ITitle.__identifier__: {
                'title': bezirks_region_name}}

        try:
            registry.content.create(
                multipolygon_meta.iresource.__identifier__,
                appstructs=appstructs,
                parent=locations)
            root._p_changed = True
            transaction.commit()
        except Exception:
            t, e = sys.exc_info()[:2]
            print(e)


def import_bezirke():
    """Get geodata for berlin's bezirke from FIS-Broker."""
    call = 'ogr2ogr -s_srs EPSG:25833 -t_srs WGS84 -f geoJSON ' \
           ' /tmp/bezirke.json WFS:"http://fbinter.stadt-berlin.de' \
           '/fb/wfs/geometry/senstadt/re_bezirke?TYPENAMES=GML2"' \
           'fis:re_bezirke'

    try:
        os.remove('/tmp/bezirke.json')
        print('Old file removed')
    except:
        print('No file to remove')

    try:
        os.system(call)
    except Exception:
        t, e = sys.exc_info()[:2]
        print(e)
        sys.exit()

    data = json.load(open('/tmp/bezirke.json', 'r'))

    env = bootstrap('./etc/development.ini')
    root = env['root']
    registry = env['registry']
    locations = find_service(root, 'locations')

    for feature in data['features']:

        geometry = feature['geometry']['coordinates']
        bezirk = feature['properties']['spatial_alias']
        type = feature['geometry']['type']
        if type == 'Polygon':
            geometry = [geometry]

        geosheet = {'coordinates': geometry,
                    'administrative_division': 'stadtbezirk',
                    'part_of': None,
                    'type': 'MultiPolygon'}

        appstructs = {IName.__identifier__: {'name': slugify(bezirk)},
                      IMultiPolygon.__identifier__: geosheet,
                      ITitle.__identifier__: {'title': bezirk}
                      }

        try:
            registry.content.create(
                multipolygon_meta.iresource.__identifier__,
                appstructs=appstructs,
                parent=locations)
        except Exception:
            t, e = sys.exc_info()[:2]
            print(e)
    transaction.commit()
