def json_read():
    import json
    file = open('config.json')
    data = json.load(file)
    print(data)