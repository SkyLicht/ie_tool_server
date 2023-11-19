
from dataclasses import dataclass
from typing import List
import requests
from src.http.get_data_from_mackenzie_api import get_current_day_outputs_data, LineData, OutputsData
from src.lib.util import Server
from src.lib.util_config import get_ip

@dataclass
class WorkPlan:
    line: str
    sku: str
    target_oee: float
    uph_d: int
    uph_i: int
    hour: List[OutputsData]

    def __init__(self, l: str, s: str, t: float, d: int, i: int, h: List[OutputsData]):
        self.line = l
        self.sku = s
        self.target_oee = t
        self.uph_d = d
        self.uph_i = i
        self.hour = h


def wp_with_hours(work_plan, output: List[LineData]) -> List[WorkPlan]:
    """
    the work plan contains the dato form one day of planned production e.g. []

    """

    def find(line: str) -> List[OutputsData]:
        for i in output:
            if i.line == line: return i.data
        return []

    r_wp: List[WorkPlan] = []

    for wp in work_plan:
        data = {
            'id': wp['id'],
            'work_date': wp['work_date'],
            'line': wp['line'],
            'platform': wp['expand']['model']['platform'],
            'sku': wp['expand']['model']['sku'],
            'type': wp['type'],
            'status': wp['status'],
            'phrs_1': wp['phrs_1'],
            'phrs_2': wp['phrs_2'],
            'phrs_3': wp['phrs_3'],
            'phrs_s': wp['phrs_s'],
            'target_oee': wp['target_oee'],
            'uph_i': wp['uph_i'],
            'uph_d': wp['expand']['model']['uph']
        }
        r_wp.append(
            WorkPlan(
                l=data['line'],
                s=data['sku'],
                t=data['target_oee'],
                d=data['uph_d'],
                i=data['uph_i'],
                h=find(line=wp['line'])
            )
        )

    print(r_wp)
    return r_wp


def get_wp_current_day():
    from datetime import date
    current_day = date.today().strftime("%Y-%m-%d")
    try:
        work_plan = requests.get(
            url=f'http://{get_ip(Server.ONLINE)}:3030/api/collections/workplanv2/records?filter=(work_date = "{current_day}")&expand=model',
            headers={
                'Content-Type': 'application/json',
                'Authorization': ''
            }
        )
        if len(work_plan.json()['items']) > 0:
            return work_plan.json()['items']

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

    return []


def get_wp() -> List[WorkPlan]:
    """get current outputs data form mackenzie api"""
    outputs = get_current_day_outputs_data()
    """get current wp from database"""
    work_plan = get_wp_current_day()
    # return a work plan
    return wp_with_hours(work_plan=work_plan, output=outputs)
