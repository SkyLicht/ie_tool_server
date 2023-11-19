from src.lib.util import Server


def get_ip(host: Server) -> str:
    import json
    selected_host = ''
    match host:
        case Server.ONLINE:
            selected_host = 'ip_online'
        case Server.LOCAL:
            selected_host = 'ip_local'
    file = open('config.json')
    data = json.load(file)
    return data[selected_host]


def is_mackenzie_online() -> bool:
    import json
    file = open('config.json')
    data = json.load(file)
    print(data['is_mackenzie_online'])
    match data['is_mackenzie_online']:
        case 'true':
            return True
        case 'false':
            return False
        case _: return False
