# -*- coding: utf-8 -*-
__module_name__ = "PySysInfo"
__module_version__ = "0.1"
__module_description__ = "Displays current system info using Python"
__author__ = "Anirban Mukhopadhyay"

import hexchat, psutil, subprocess
from datetime import datetime
from collections import namedtuple

class WMI(object):
    def __init__(self, root):
        self.root = root

    def get(self, path):
        result = subprocess.check_output(['wmic', '/NAMESPACE:%s' % (self.root,), 'Path', path, 'Get'], shell=True)
        lines = result.strip().split('\n')
        properties = lines[0].strip().split()
        indices = [lines[0].index(p) for p in properties]

        PathNamedTuple = namedtuple(path + 'TupleType', properties)
        tuples = []
        for l in lines[1:]:
            values = []
            for i, prop_index in enumerate(indices):
                values.append(l[prop_index : len(l) if i + 1 == len(indices) else indices[i + 1]].strip())
            tuples.append(PathNamedTuple(*values))
        return tuples

def avg(l):
    l = list(l)
    return sum(l) / len(l)

def bytes_to_gbytes(bytes):
    return bytes / 1024.0 / 1024.0 / 1024.0

def bytes_to_tbytes(bytes):
    return bytes_to_gbytes(bytes) / 1024.0

def get_client_info():
    return u'\002Client\002: HexChat %s' % (hexchat.get_info('version'))

def get_os_info(cimv2):
    os = cimv2.get('Win32_OperatingSystem')[0]
    return u'\002OS\002: %s (%s)' % (os.Caption, os.OSArchitecture)

def get_cpu_info(hardware_list, sensor_list):
    cpu_clocks = [s for s in sensor_list if (s.SensorType == u'Clock' and u'cpu' in s.Parent.lower())]
    cpu_temps = [s for s in sensor_list if (s.SensorType == u'Temperature' and u'cpu' in s.Parent.lower())]
    cpu = [h for h in hardware_list if h.Identifier == cpu_clocks[0].Parent]
    return u'\002CPU\002: %s [%.2fGHz (%.2fGHz)] [%.2f°C (%.2f°C)]' % (cpu[0].Name,
                                                                        round(avg(float(c.Value) for c in cpu_clocks) / 1024.0, 2),
                                                                        round(avg(float(c.Max) for c in cpu_clocks) / 1024.0, 2),
                                                                        round(avg(float(t.Value) for t in cpu_temps), 2),
                                                                        round(avg(float(t.Max) for t in cpu_temps), 2))

def get_gpu_info(hardware_list, sensor_list):
    gpu_temps = [s for s in sensor_list if (s.SensorType == u'Temperature' and u'gpu' in s.Parent.lower())]
    gpu = [h for h in hardware_list if h.Identifier == gpu_temps[0].Parent]
    return u'\002GPU\002: %s [%.2f°C (%.2f°C)]' % (gpu[0].Name,
                                                    round(avg(float(t.Value) for t in gpu_temps), 2),
                                                    round(avg(float(t.Max) for t in gpu_temps), 2))

def get_memory_info():
    memory_stats = psutil.virtual_memory()
    return u'\002Memory\002: %.2fGB Used (%.2fGB Total)' % (round(bytes_to_gbytes(memory_stats.used), 2),
                                                            round(bytes_to_gbytes(memory_stats.total), 2))

def get_disk_info(sensor_list):
    disks = [psutil.disk_usage(s.mountpoint) for s in psutil.disk_partitions()]
    hdd_temps = [s for s in sensor_list if (s.SensorType == u'Temperature' and u'hdd' in s.Parent.lower())]
    return u'\002Storage\002: %.2fTB Used (%.2fTB Total) [%.2f°C (%.2f°C)]' % (round(bytes_to_tbytes(sum([d.used for d in disks])), 2),
                                                                            round(bytes_to_tbytes(sum([d.total for d in disks])), 2),
                                                                            round(avg(float(h.Value) for h in hdd_temps), 2),
                                                                            round(avg(float(h.Max) for h in hdd_temps), 2))

def get_uptime():
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return u'\002Uptime\002: %ud %uh %um %us' % (uptime.days, hours, minutes, seconds)

def get_system_info(wmi_CIMV2, wmi_OpenHardwareMonitor):
    hardware_list = wmi_OpenHardwareMonitor.get('Hardware')
    sensor_list = wmi_OpenHardwareMonitor.get('Sensor')
    return [get_client_info(),
            get_os_info(wmi_CIMV2),
            get_cpu_info(hardware_list, sensor_list),
            get_gpu_info(hardware_list, sensor_list),
            get_memory_info(),
            get_disk_info(sensor_list),
            get_uptime()]

def send_system_info(word, word_eol, userdata):
    wmi_CIMV2 = WMI('\\\\root\CIMV2')
    wmi_OpenHardwareMonitor = WMI('\\\\root\OpenHardwareMonitor')
    hexchat.command('say %s' % (u' \002•\002 '.join(get_system_info(wmi_CIMV2, wmi_OpenHardwareMonitor)).encode('utf-8'),))
    return hexchat.EAT_ALL

hexchat.hook_command("systeminfo", send_system_info)