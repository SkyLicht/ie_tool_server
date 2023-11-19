from src.http.get_data_from_mackenzie_api import get_day_before_outputs_data


def post_output_day_before():
    """get the data from the mackenzie api and load to the database '' """
    data = get_day_before_outputs_data()

    for i in data:
        if i.length() <= 0: pass
        to_db_line_ids = []


# for l in temp_lines:
#     print(l)
#
#     if len(l['hours']) > 0:
#
#         to_db_line_ids = []
#         print('inside')
#         for h in l['hours']:
#             print('lp', h)
#             post_hours = requests.post(
#                 url='http://10.13.33.46:3030/api/collections/hour/records',
#                 headers={
#                     'Content-Type': 'application/json',
#                     'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTgxNTE3NDMsImlkIjoiang1cXc2eW5mM2QxY3o0IiwidHlwZSI6ImFkbWluIn0.aA73pdcN5g5hrgAF8tO4IZ3-YsLWYcAAnzRLB75PqAs'
#                 },
#                 data=json.dumps(
#                     {"place": h['index'], "smtIn": h['smtA'], "smtOut": h['smtB'], "packing": h['output']}
#                 )
#             )
#             print('status', post_hours.status_code)
#             to_db_line_ids.append(post_hours.json()['id'])
#
#         post_day = requests.post(
#             url='http://10.13.33.46:3030/api/collections/day/records',
#             headers={
#                 'Content-Type': 'application/json',
#                 'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTgxNTE3NDMsImlkIjoiang1cXc2eW5mM2QxY3o0IiwidHlwZSI6ImFkbWluIn0.aA73pdcN5g5hrgAF8tO4IZ3-YsLWYcAAnzRLB75PqAs'
#             },
#             data=json.dumps(
#                 {"work_date": str(date_to_post), "line": l['line'], "hours": to_db_line_ids}
#             )
#         )
