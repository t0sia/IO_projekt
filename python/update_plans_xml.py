import xml.etree.ElementTree as ET
from random import shuffle, choices

def read(file_name='plans.xml'):
    file = ET.parse(file_name)
    root = file.getroot()

    people = root.findall('person')
    for person in people:
        print("person id:", person.attrib["id"])
        plan = person.find('plan')
        
        actions = plan.findall('act')
        for action in actions:
            print("  action link:", action.attrib['link'])
        
        leg = plan.find('leg')
        route = leg.find('route').text
        print("  route:", route)

def update(x, file_name='plans.xml'):
    file = ET.parse(file_name)
    root = file.getroot()

    i = 0
    people = root.findall('person')
    for person in people:
        plan = person.find('plan')
        
        actions = plan.findall('act')
        for action in actions:
            if action.get('end_time') is not None: # from
                action.set('link', str(x[i][0]))
            else: # to
                action.set('link', str(x[i][-1]))
        leg = plan.find('leg')
        route = leg.find('route')
        route.text = " ".join(str(node) for node in x[i][1:-1])
        i += 1

    file.write(file_name)
    with open(file_name, 'r') as original:
        data = original.read()
    with open(file_name, 'w') as modified:
        modified.write('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plans SYSTEM "http://www.matsim.org/files/dtd/plans_v4.dtd">\n' + data)

def get_x(distribution, n):
    routes, probabilities = zip(*distribution.items())

    return choices(routes, probabilities, k=n)

if __name__ == "__main__":
    distribution = {
        (1,19,10,18,3) : .24,
        (6,20,11,15,8) : .10,
        (12,21,13,12,14) : .10,
        (4,22,14,18,3) : .23,
        (9,23,16,15,11) : .10,
        (15,24,17,12,14) : .23,
    }
    x = get_x(distribution, 7200)
    
    update(x)

'''
routes: from to
1,10,18,9 1 3
2,11,15,6 6 8
4,13,12,3 12 14
5,14,18,9 4 3
7,16,15,6 9 11
8,17,12,3 15 14
'''
