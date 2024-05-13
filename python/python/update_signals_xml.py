import xml.etree.ElementTree as ET

def read(file_name='signal_controls.xml'):
    file = ET.parse(file_name)
    root = file.getroot()
    ns = {'ns': 'http://www.matsim.org/files/dtd'}

    signal_systems = root.findall('ns:signalSystem', ns)
    for signal_system in signal_systems:
        signal_system_controller = signal_system.find('ns:signalSystemController', ns)
        signal_plans = signal_system_controller.findall('ns:signalPlan', ns)
        for signal_plan in signal_plans:
            print("signal plan id:", signal_plan.attrib['id'])
            print("  start time:", signal_plan.find('ns:start', ns).attrib['daytime'])
            print("  cycle time:", signal_plan.find('ns:cycleTime', ns).attrib['sec'])
            print("  offset:", signal_plan.find('ns:offset', ns).attrib['sec'])
            signal_group_settings = signal_plan.findall('ns:signalGroupSettings', ns)
            for signal_group_setting in signal_group_settings:
                print("  signal group setting id:", signal_group_setting.attrib['refId'])
                onset = signal_group_setting.find('ns:onset', ns).attrib['sec']
                print("    onset:", onset)
                dropping = signal_group_setting.find('ns:dropping', ns).attrib['sec']
                print("    dropping:", dropping)

def update(x, file_name='signal_controls.xml'):
    file = ET.parse(file_name)
    root = file.getroot()
    ns = {'ns': 'http://www.matsim.org/files/dtd'}
    
    i = 0
    count = len(x)//2
    signal_systems = root.findall('ns:signalSystem', ns)
    for signal_system in signal_systems:
        signal_system_controller = signal_system.find('ns:signalSystemController', ns)
        signal_plans = signal_system_controller.findall('ns:signalPlan', ns)
        for signal_plan in signal_plans:
            signal_group_settings = signal_plan.findall('ns:signalGroupSettings', ns)
            for signal_group_setting in signal_group_settings:
                signal_group_setting.find('ns:onset', ns).set('sec', str(x[i]))
                signal_group_setting.find('ns:dropping', ns).set('sec', str(x[count+i]))
                i += 1
    
    file.write(file_name)

if __name__ == "__main__":
    update([1,2,3,4,5,6,7,8])