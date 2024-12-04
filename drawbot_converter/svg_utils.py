import re


def parse_number_units(input):
    '''Parses a number out of an SVG string that might include units, e.g. "20mm"'''
    return float(re.sub("[^\\d\\.]", "", input) )

def parse_numbers_units(input):
    '''Parses several numbers out of an SVG string that might include units,
    e.g. "20mm 400mm -3mm 2mm"

    Currently stupid - doesn't deal with what the units mean...
    '''
    return [ float(re.sub("[^\\d\\.-]", "", x) ) for x in input.split()]

def size_abs(input):
    if "%" in input:
        return False
    return True
