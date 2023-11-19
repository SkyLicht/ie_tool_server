from array import array
from dataclasses import dataclass, field
import json
from enum import Enum
from datetime import date
from typing import List

import requests
import itertools

from src.lib.util_config import is_mackenzie_online


class LineSide(Enum):
    SMT_IN = 'INPUT'
    SMT_OUT = 'OUTPUT'
    PACKING = 'PACKING'


LINES = [
    'J01',
    'J02',
    'J03',
    'J05',
    'J06',
    'J07',
    'J08',
    'J09',
    'J10',
    'J11',
    'J12',
    'J13'
]


@dataclass
class OutputsData:
    index: int
    smt_in: int
    smt_out: int
    packing: int

    def __init__(self, index, smt_in, smt_out, packing):
        self.index = index
        self.smt_in = smt_in
        self.smt_out = smt_out
        self.packing = packing

    def print(self):
        print(f'index: {self.index} smt in: {self.smt_in} smt out: {self.smt_out} packing: {self.packing} ')


@dataclass
class LineData:
    line: str
    data: List[OutputsData] = field(default_factory=dict)

    def __init__(self, name, output_data: List[OutputsData]):
        self.line = name
        self.data = output_data

    def log(self):
        print(self.line)
        print('-----------------------------------------------')
        for i in self.data:
            print(i.print())

    def is_empty(self) -> bool:
        temp = 0
        for i in self.data:
            temp += (i.smt_in + i.smt_out + i.packing)
        if temp != 0: return True
        return False

    def length(self) -> int:
        return len(self.data)


def http_url_fix_day(current_day: str, side: LineSide):
    return f'http://10.13.89.96:83/home/reporte?entrada={current_day}00&salida={current_day}2300&transtype={side.value}'


def get_current_day_outputs_data() -> List[LineData]:
    current_day = date.today().strftime("%Y%m%d")
    lines_data: List[LineData] = []

    if not is_mackenzie_online():
        print('mackenzie online')
        for dummy in dummy_data:
            print(dummy)
        return []
    try:
        '''get the output from mackenzie api'''
        smt_in = requests.get(http_url_fix_day(current_day, LineSide.SMT_IN))
        smt_out = requests.get(http_url_fix_day(current_day, LineSide.SMT_OUT))
        packing = requests.get(http_url_fix_day(current_day, LineSide.PACKING))
        print('api responds', smt_in, smt_out, packing)

        dic_smt_in = {"smt_in": []}
        for k, g in itertools.groupby(smt_in.json(), key=lambda x: x['LINE']):
            f = {"line": translate_line_standard(k), "smt_in": list(g)}
            for i in f.get('smt_in'):
                i.pop('LINE')
                i.pop('NEXTDAY')

            dic_smt_in["smt_in"].append(f)

        if len(dic_smt_in['smt_in']) > 0:
            dic_smt_in['smt_in'].pop(0)

        dic_smt_out = {"smt_out": []}
        for k, g in itertools.groupby(smt_out.json(), key=lambda x: x['LINE']):
            f = {"line": translate_line_standard(k), "smt_out": list(g)}
            for i in f.get('smt_out'):
                i.pop('LINE')
                i.pop('NEXTDAY')
            dic_smt_out["smt_out"].append(f)

        if len(dic_smt_out['smt_out']) > 0:
            dic_smt_out['smt_out'].pop(0)
        dic_packing = {"packing": []}
        for k, g in itertools.groupby(packing.json(), key=lambda x: x['LINE']):
            f = {"line": translate_line_standard(k), "packing": list(g)}
            for i in f.get('packing'):
                i.pop('LINE')
                i.pop('NEXTDAY')
            dic_packing["packing"].append(f)

        if len(dic_packing['packing']) > 0:
            dic_packing['packing'].pop(0)

        for line in LINES:

            d1 = [a['smt_in'] for a in dic_smt_in['smt_in'] if a['line'] == line]
            d2 = [a['smt_out'] for a in dic_smt_out['smt_out'] if a['line'] == line]
            d3 = [a['packing'] for a in dic_packing['packing'] if a['line'] == line]
            hours: List[OutputsData] = []

            for i in range(24):
                temp_hour: OutputsData = OutputsData(index=i, smt_in=0, smt_out=0, packing=0)
                if len(d1) > 0:
                    for h_smt_in in d1[0]:
                        if h_smt_in['HOURS'] == translate_index_to_hour(i):
                            temp_hour.smt_in = h_smt_in['QTY']

                if len(d2) > 0:
                    for h_smt_out in d2[0]:
                        if h_smt_out['HOURS'] == translate_index_to_hour(i):
                            temp_hour.smt_out = h_smt_out['QTY']

                if len(d3) > 0:
                    for h_packing in d3[0]:
                        if h_packing['HOURS'] == translate_index_to_hour(i):
                            temp_hour.packing = h_packing['QTY']

                hours.append(temp_hour)

            temp_line = LineData(name=line, output_data=hours)
            if temp_line.is_empty(): lines_data.append(temp_line)

        # for l_i in lines_data:
        #     l_i.log()

    except Exception as e:
        print(e)

    return lines_data


def get_day_before_outputs_data() -> List[LineData]:
    import datetime
    today = datetime.date.today()
    day = datetime.timedelta(days=1)
    yesterday = today - day
    lines_data: List[LineData] = []

    try:
        """get the output from mackenzie api'"""
        smt_in = requests.get(http_url_fix_day(yesterday.strftime("%Y%m%d"), LineSide.SMT_IN))
        smt_out = requests.get(http_url_fix_day(yesterday.strftime("%Y%m%d"), LineSide.SMT_OUT))
        packing = requests.get(http_url_fix_day(yesterday.strftime("%Y%m%d"), LineSide.PACKING))
        print('api responds', smt_in, smt_out, packing)

        dic_smt_in = {"smt_in": []}
        for k, g in itertools.groupby(smt_in.json(), key=lambda x: x['LINE']):
            f = {"line": translate_line_standard(k), "smt_in": list(g)}
            for i in f.get('smt_in'):
                i.pop('LINE')
                i.pop('NEXTDAY')

            dic_smt_in["smt_in"].append(f)

        if len(dic_smt_in['smt_in']) > 0:
            dic_smt_in['smt_in'].pop(0)

        dic_smt_out = {"smt_out": []}
        for k, g in itertools.groupby(smt_out.json(), key=lambda x: x['LINE']):
            f = {"line": translate_line_standard(k), "smt_out": list(g)}
            for i in f.get('smt_out'):
                i.pop('LINE')
                i.pop('NEXTDAY')
            dic_smt_out["smt_out"].append(f)

        if len(dic_smt_out['smt_out']) > 0:
            dic_smt_out['smt_out'].pop(0)
        dic_packing = {"packing": []}
        for k, g in itertools.groupby(packing.json(), key=lambda x: x['LINE']):
            f = {"line": translate_line_standard(k), "packing": list(g)}
            for i in f.get('packing'):
                i.pop('LINE')
                i.pop('NEXTDAY')
            dic_packing["packing"].append(f)

        if len(dic_packing['packing']) > 0:
            dic_packing['packing'].pop(0)

        for line in LINES:

            d1 = [a['smt_in'] for a in dic_smt_in['smt_in'] if a['line'] == line]
            d2 = [a['smt_out'] for a in dic_smt_out['smt_out'] if a['line'] == line]
            d3 = [a['packing'] for a in dic_packing['packing'] if a['line'] == line]
            hours: List[OutputsData] = []

            for i in range(24):
                temp_hour: OutputsData = OutputsData(index=i, smt_in=0, smt_out=0, packing=0)
                if len(d1) > 0:
                    for h_smt_in in d1[0]:
                        if h_smt_in['HOURS'] == translate_index_to_hour(i):
                            temp_hour.smt_in = h_smt_in['QTY']

                if len(d2) > 0:
                    for h_smt_out in d2[0]:
                        if h_smt_out['HOURS'] == translate_index_to_hour(i):
                            temp_hour.smt_out = h_smt_out['QTY']

                if len(d3) > 0:
                    for h_packing in d3[0]:
                        if h_packing['HOURS'] == translate_index_to_hour(i):
                            temp_hour.packing = h_packing['QTY']

                hours.append(temp_hour)

            temp_line = LineData(name=line, output_data=hours)
            if temp_line.is_empty(): lines_data.append(temp_line)

        for l_i in lines_data:
            l_i.log()

    except Exception as e:
        print(e)

    return lines_data


def translate_line_standard(line):
    switch = {
        'SMTJ01A': 'J01',
        'SMTJ02A': 'J02',
        'SMTJ03A': 'J03',
        'SMTJ05': 'J05',
        'SMTJ06': 'J06',
        'SMTJ07': 'J07',
        'SMTJ08': 'J08',
        'SMTJ09A': 'J09',
        'SMTJ10A': 'J10',
        'SMTJ11A': 'J11',
        'SMTJ12A': 'J12',
        'SMTJ13A': 'J13'
    }
    return switch.get(line, "total")


def translate_index_to_hour(index):
    switch = {
        0: '0000',
        1: '0100',
        2: '0200',
        3: '0300',
        4: '0400',
        5: '0500',
        6: '0600',
        7: '0700',
        8: '0800',
        9: '0900',
        10: '1000',
        11: '1100',
        12: '1200',
        13: '1300',
        14: '1400',
        15: '1500',
        16: '1600',
        17: '1700',
        18: '1800',
        19: '1900',
        20: '2000',
        21: '2100',
        22: '2200',
        23: '2300'
    }
    return switch.get(index, 1)


dummy_data = [
    {
        "line": "J01",
        "hours": [
            {
                "index": 0,
                "smt_in": 94,
                "smt_out": 72,
                "packing": 41
            },
            {
                "index": 1,
                "smt_in": 82,
                "smt_out": 78,
                "packing": 81
            },
            {
                "index": 2,
                "smt_in": 90,
                "smt_out": 69,
                "packing": 83
            },
            {
                "index": 3,
                "smt_in": 40,
                "smt_out": 72,
                "packing": 82
            },
            {
                "index": 4,
                "smt_in": 106,
                "smt_out": 72,
                "packing": 86
            },
            {
                "index": 5,
                "smt_in": 62,
                "smt_out": 70,
                "packing": 80
            },
            {
                "index": 6,
                "smt_in": 67,
                "smt_out": 53,
                "packing": 45
            },
            {
                "index": 7,
                "smt_in": 100,
                "smt_out": 84,
                "packing": 45
            },
            {
                "index": 8,
                "smt_in": 87,
                "smt_out": 83,
                "packing": 80
            },
            {
                "index": 9,
                "smt_in": 93,
                "smt_out": 81,
                "packing": 82
            },
            {
                "index": 10,
                "smt_in": 59,
                "smt_out": 49,
                "packing": 80
            },
            {
                "index": 11,
                "smt_in": 84,
                "smt_out": 82,
                "packing": 73
            },
            {
                "index": 12,
                "smt_in": 69,
                "smt_out": 71,
                "packing": 82
            },
            {
                "index": 13,
                "smt_in": 8,
                "smt_out": 2,
                "packing": 0
            },
            {
                "index": 14,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 15,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 16,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 17,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 18,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 19,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 20,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 21,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 22,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 23,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            }
        ]
    },
    {
        "line": "J02",
        "hours": [
            {
                "index": 0,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 1,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 2,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 3,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 4,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 5,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 6,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 7,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 8,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 7
            },
            {
                "index": 9,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 7
            },
            {
                "index": 10,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 11,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 12,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 13,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 14,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 15,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 16,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 17,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 18,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 19,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 20,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 21,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 22,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 23,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            }
        ]
    },
    {
        "line": "J03",
        "hours": []
    },
    {
        "line": "J05",
        "hours": [
            {
                "index": 0,
                "smt_in": 100,
                "smt_out": 72,
                "packing": 50
            },
            {
                "index": 1,
                "smt_in": 108,
                "smt_out": 112,
                "packing": 98
            },
            {
                "index": 2,
                "smt_in": 112,
                "smt_out": 82,
                "packing": 96
            },
            {
                "index": 3,
                "smt_in": 61,
                "smt_out": 74,
                "packing": 58
            },
            {
                "index": 4,
                "smt_in": 93,
                "smt_out": 78,
                "packing": 85
            },
            {
                "index": 5,
                "smt_in": 64,
                "smt_out": 69,
                "packing": 93
            },
            {
                "index": 6,
                "smt_in": 62,
                "smt_out": 74,
                "packing": 51
            },
            {
                "index": 7,
                "smt_in": 74,
                "smt_out": 89,
                "packing": 55
            },
            {
                "index": 8,
                "smt_in": 81,
                "smt_out": 89,
                "packing": 36
            },
            {
                "index": 9,
                "smt_in": 101,
                "smt_out": 94,
                "packing": 102
            },
            {
                "index": 10,
                "smt_in": 72,
                "smt_out": 79,
                "packing": 101
            },
            {
                "index": 11,
                "smt_in": 96,
                "smt_out": 99,
                "packing": 99
            },
            {
                "index": 12,
                "smt_in": 65,
                "smt_out": 85,
                "packing": 110
            },
            {
                "index": 13,
                "smt_in": 2,
                "smt_out": 3,
                "packing": 2
            },
            {
                "index": 14,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 15,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 16,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 17,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 18,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 19,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 20,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 21,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 22,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 23,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            }
        ]
    },
    {
        "line": "J06",
        "hours": [
            {
                "index": 0,
                "smt_in": 85,
                "smt_out": 74,
                "packing": 86
            },
            {
                "index": 1,
                "smt_in": 95,
                "smt_out": 98,
                "packing": 56
            },
            {
                "index": 2,
                "smt_in": 75,
                "smt_out": 89,
                "packing": 99
            },
            {
                "index": 3,
                "smt_in": 92,
                "smt_out": 81,
                "packing": 72
            },
            {
                "index": 4,
                "smt_in": 95,
                "smt_out": 80,
                "packing": 94
            },
            {
                "index": 5,
                "smt_in": 64,
                "smt_out": 86,
                "packing": 100
            },
            {
                "index": 6,
                "smt_in": 89,
                "smt_out": 92,
                "packing": 58
            },
            {
                "index": 7,
                "smt_in": 96,
                "smt_out": 99,
                "packing": 36
            },
            {
                "index": 8,
                "smt_in": 100,
                "smt_out": 102,
                "packing": 106
            },
            {
                "index": 9,
                "smt_in": 99,
                "smt_out": 101,
                "packing": 103
            },
            {
                "index": 10,
                "smt_in": 104,
                "smt_out": 103,
                "packing": 102
            },
            {
                "index": 11,
                "smt_in": 103,
                "smt_out": 102,
                "packing": 104
            },
            {
                "index": 12,
                "smt_in": 110,
                "smt_out": 101,
                "packing": 94
            },
            {
                "index": 13,
                "smt_in": 6,
                "smt_out": 9,
                "packing": 7
            },
            {
                "index": 14,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 15,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 16,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 17,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 18,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 19,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 20,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 21,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 22,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 23,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            }
        ]
    },
    {
        "line": "J07",
        "hours": []
    },
    {
        "line": "J08",
        "hours": []
    },
    {
        "line": "J09",
        "hours": []
    },
    {
        "line": "J10",
        "hours": [
            {
                "index": 0,
                "smt_in": 48,
                "smt_out": 54,
                "packing": 47
            },
            {
                "index": 1,
                "smt_in": 53,
                "smt_out": 51,
                "packing": 43
            },
            {
                "index": 2,
                "smt_in": 66,
                "smt_out": 58,
                "packing": 52
            },
            {
                "index": 3,
                "smt_in": 43,
                "smt_out": 55,
                "packing": 41
            },
            {
                "index": 4,
                "smt_in": 43,
                "smt_out": 34,
                "packing": 37
            },
            {
                "index": 5,
                "smt_in": 50,
                "smt_out": 55,
                "packing": 62
            },
            {
                "index": 6,
                "smt_in": 34,
                "smt_out": 36,
                "packing": 22
            },
            {
                "index": 7,
                "smt_in": 57,
                "smt_out": 65,
                "packing": 63
            },
            {
                "index": 8,
                "smt_in": 66,
                "smt_out": 55,
                "packing": 62
            },
            {
                "index": 9,
                "smt_in": 58,
                "smt_out": 58,
                "packing": 62
            },
            {
                "index": 10,
                "smt_in": 52,
                "smt_out": 56,
                "packing": 62
            },
            {
                "index": 11,
                "smt_in": 63,
                "smt_out": 59,
                "packing": 63
            },
            {
                "index": 12,
                "smt_in": 62,
                "smt_out": 58,
                "packing": 62
            },
            {
                "index": 13,
                "smt_in": 2,
                "smt_out": 5,
                "packing": 3
            },
            {
                "index": 14,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 15,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 16,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 17,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 18,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 19,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 20,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 21,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 22,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 23,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            }
        ]
    },
    {
        "line": "J11",
        "hours": [
            {
                "index": 0,
                "smt_in": 110,
                "smt_out": 125,
                "packing": 70
            },
            {
                "index": 1,
                "smt_in": 178,
                "smt_out": 135,
                "packing": 200
            },
            {
                "index": 2,
                "smt_in": 160,
                "smt_out": 167,
                "packing": 197
            },
            {
                "index": 3,
                "smt_in": 170,
                "smt_out": 188,
                "packing": 157
            },
            {
                "index": 4,
                "smt_in": 176,
                "smt_out": 163,
                "packing": 176
            },
            {
                "index": 5,
                "smt_in": 88,
                "smt_out": 136,
                "packing": 162
            },
            {
                "index": 6,
                "smt_in": 0,
                "smt_out": 66,
                "packing": 75
            },
            {
                "index": 7,
                "smt_in": 50,
                "smt_out": 81,
                "packing": 49
            },
            {
                "index": 8,
                "smt_in": 53,
                "smt_out": 115,
                "packing": 121
            },
            {
                "index": 9,
                "smt_in": 134,
                "smt_out": 12,
                "packing": 26
            },
            {
                "index": 10,
                "smt_in": 88,
                "smt_out": 8,
                "packing": 15
            },
            {
                "index": 11,
                "smt_in": 100,
                "smt_out": 76,
                "packing": 50
            },
            {
                "index": 12,
                "smt_in": 58,
                "smt_out": 160,
                "packing": 130
            },
            {
                "index": 13,
                "smt_in": 0,
                "smt_out": 11,
                "packing": 11
            },
            {
                "index": 14,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 15,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 16,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 17,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 18,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 19,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 20,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 21,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 22,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 23,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            }
        ]
    },
    {
        "line": "J12",
        "hours": [
            {
                "index": 0,
                "smt_in": 14,
                "smt_out": 72,
                "packing": 46
            },
            {
                "index": 1,
                "smt_in": 132,
                "smt_out": 164,
                "packing": 135
            },
            {
                "index": 2,
                "smt_in": 158,
                "smt_out": 90,
                "packing": 122
            },
            {
                "index": 3,
                "smt_in": 131,
                "smt_out": 129,
                "packing": 135
            },
            {
                "index": 4,
                "smt_in": 105,
                "smt_out": 157,
                "packing": 135
            },
            {
                "index": 5,
                "smt_in": 85,
                "smt_out": 86,
                "packing": 119
            },
            {
                "index": 6,
                "smt_in": 148,
                "smt_out": 86,
                "packing": 51
            },
            {
                "index": 7,
                "smt_in": 176,
                "smt_out": 174,
                "packing": 135
            },
            {
                "index": 8,
                "smt_in": 154,
                "smt_out": 160,
                "packing": 137
            },
            {
                "index": 9,
                "smt_in": 168,
                "smt_out": 159,
                "packing": 140
            },
            {
                "index": 10,
                "smt_in": 142,
                "smt_out": 143,
                "packing": 140
            },
            {
                "index": 11,
                "smt_in": 148,
                "smt_out": 140,
                "packing": 141
            },
            {
                "index": 12,
                "smt_in": 148,
                "smt_out": 145,
                "packing": 145
            },
            {
                "index": 13,
                "smt_in": 12,
                "smt_out": 6,
                "packing": 4
            },
            {
                "index": 14,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 15,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 16,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 17,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 18,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 19,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 20,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 21,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 22,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 23,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            }
        ]
    },
    {
        "line": "J13",
        "hours": [
            {
                "index": 0,
                "smt_in": 19,
                "smt_out": 43,
                "packing": 31
            },
            {
                "index": 1,
                "smt_in": 66,
                "smt_out": 36,
                "packing": 32
            },
            {
                "index": 2,
                "smt_in": 43,
                "smt_out": 33,
                "packing": 35
            },
            {
                "index": 3,
                "smt_in": 37,
                "smt_out": 20,
                "packing": 13
            },
            {
                "index": 4,
                "smt_in": 27,
                "smt_out": 27,
                "packing": 39
            },
            {
                "index": 5,
                "smt_in": 18,
                "smt_out": 24,
                "packing": 16
            },
            {
                "index": 6,
                "smt_in": 11,
                "smt_out": 8,
                "packing": 12
            },
            {
                "index": 7,
                "smt_in": 29,
                "smt_out": 39,
                "packing": 3
            },
            {
                "index": 8,
                "smt_in": 36,
                "smt_out": 35,
                "packing": 33
            },
            {
                "index": 9,
                "smt_in": 61,
                "smt_out": 37,
                "packing": 45
            },
            {
                "index": 10,
                "smt_in": 27,
                "smt_out": 37,
                "packing": 9
            },
            {
                "index": 11,
                "smt_in": 31,
                "smt_out": 32,
                "packing": 43
            },
            {
                "index": 12,
                "smt_in": 38,
                "smt_out": 53,
                "packing": 30
            },
            {
                "index": 13,
                "smt_in": 5,
                "smt_out": 5,
                "packing": 4
            },
            {
                "index": 14,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 15,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 16,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 17,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 18,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 19,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 20,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 21,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 22,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            },
            {
                "index": 23,
                "smt_in": 0,
                "smt_out": 0,
                "packing": 0
            }
        ]
    }
]
