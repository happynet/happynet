#!/usr/bin/env python

'''This script will be used for One Link configuration application on Multiple devices'''
from __future__ import print_function
import sys
import os
from netmiko import ConnectHandler
from socket import gethostbyname
import system_snmp
import getpass
from datetime import datetime
import threading
from time import sleep
from subprocess import PIPE, Popen
import zipfile
from six.moves import input

from python_logging import initialize_logger
from python_logging import default_argparse

## Display help
def usage():
	print ('NAME\n')
	print('     small_range_scanning.py - Run a command against a list of network devices\n')
	print ('SYNOPSIS\n')
	print('    small_range_scanning.py [OPTIONS]\n')
	print ('DESCRIPTION')
	print('    Runs a user supplied command against a list of devices in a file.\n')
	print('    The device list must be in a file named devices_%user%.txt (use touch devices_%user% to create)\n')
	print('    in same location of script for devices.\n')
	print('    Maximum Devices 100, Open attachment in Notepad++\n')
	print('   No arguments are needed. The script will prompt for the info it needs.')
	print('\n')
	print('                --help                          Print help.')
	print('                -h                              Print help.\n')
	print('EXAMPLE\n')
	print('          \n')


if any(i in sys.argv for i in ['-h', '--help']):
	usage()
	
	

logger = initialize_logger(default_argparse(), __script_name__)
username = getpass.getuser()
password = getpass.getpass('Enter GME Password:   ').strip()
	
def connection(device):
    '''
    Setup netmiko connection

    Note: global_delay_factor sets a sleep time between operations in netmiko, tuned from default to 0.7 sec based on testing
    '''

    device_input = {'device_type': __get_netmiko_device_os__(device),
                    'ip': gethostbyname(device),
                    'username': username,
                    'password': password,
                    'global_delay_factor': 0.7
                    }
    connection = ConnectHandler(**device_input)
    return connection


def __get_netmiko_device_os__(device):
    '''This function will be used to get vendor type'''

    sys_descr_oid = ".1.3.6.1.2.1.1.1.0"
    snmp_data = system_snmp.snmp_get(device, sys_descr_oid)[1]

    if "arista" in snmp_data.lower():
        return "arista_eos"
    elif "nx-os" in snmp_data.lower():
        return "cisco_nxos"
    elif "dell" in snmp_data.lower():
        return "dell_force10"
    else:
        raise Exception("Unsupported device. Only Arista, NX-OS, and Dell supported.")


def command_output(device, text_file, command):
	'''This function will be used to get data out from devices'''
	try:
		local_conn = connection(device)
		out = local_conn.send_command('{}'.format(command)).strip()
	except Exception as e:
		text_file.write('Error processing device:{} Error:{}'.format(device, e))
		logger.error('Error processing device:{}'.format(device))
		logger.error('Error: {}'.format(e))	
		sys.exit()
	try:
		text_file.write('{}  : {}\n'.format(device, out))
		logger.info('writing data for : {}'.format(device))
		logger.info('==============={}====================='.format(device))
		logger.info('{}'.format(out))
	except Exception as e:
		text_file.write('Error processing device:{} Error:{}'.format(device, e) )
		logger.error('Error processing device:{}'.format(device))
		logger.error('Error: {}'.format(e))
		sys.exit()


def run_from_shell(argument):
    """Run a process from the shell and return the output"""
    process = Popen(argument, shell=True, stdout=PIPE, stderr=PIPE)
    stdout = process.stdout.read()
    return stdout


def mail_it(nameoffile, cc_list=None):
    '''standard function to send mail with attachements'''
    prezip = '{}.txt'.format(nameoffile)
    sleep(5)
    zip_file = '{}.zip'.format(nameoffile)
    zip_write = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
    zip_write.write(prezip)
    zip_write.close()
    file = '{}.zip'.format(nameoffile)
    to_address = '{}@microsoft.com'.format(username)
    subject = 'scanning report run by {}'.format(username)
    body = 'Please find attachments for your scanning job'
    cc_string = str()
    if cc_list is not None:
        for name in cc_list: cc_string += "-c {} ".format(name)
    if file is None:
        argument = 'echo "{}" | mutt -s "{}" {} {}'.format(body, subject, to_address, cc_string)
    elif isinstance(file, list):
        attachments = ""
        for entry in file: attachments += "-a {0} ".format(entry)
        argument = 'echo "{3}" | mutt -s "{1}" {4} {2} {0}'.format(attachments, subject, to_address, body, cc_string)
    else:
        argument = 'echo "{3}" | mutt -s "{1}" {4} {2} -a{0}'.format(file, subject, to_address, body, cc_string)
    return run_from_shell(argument)


def thread_main(list, command, text_file):
    for host in list:
        device = host.strip()
        my_thread = threading.Thread(target=command_output, args=(device, text_file, command,))
        my_thread.start()
        '''Sleep of 0.5 is being used to try and prevent interleaving log data between threads'''
        sleep(.5)

    main_thread = threading.currentThread()
    threading.active_count()
    for some_thread in threading.enumerate():
        if some_thread != main_thread:
            print(some_thread)
            some_thread.join(timeout = 2)

def multi_threading(command, nameoffile):
    '''Mulit-threading function arg will be command and file name'''

    start_time = datetime.now()
    getfile = open('devices_{}.txt'.format(username), 'r')
    devices = getfile.readlines()

    try:
        text_file = open("{}.txt".format(nameoffile), "w")
    except Exception as e:
        logger.error('Error: {}'.format(e))
        sys.exit(1)
    list1 = [l.strip() for l in devices]
    for i in [list1[x:x + 20] for x in range(0, len(list1), 20)]:
        print('MultiThreading currently running for {}'.format(i))
        thread_main(i, command, text_file)

    text_file.close()
    logger.info("\nTotal time taken for scanning: " + str(datetime.now() - start_time))


def main():
    '''Main Funcion'''

    logger.info('Starting scan')		
    nameoffile = input('Enter name of file where output will be saved:   ').strip()
    command = input('Enter Command:  ').strip()
    multi_threading(command, nameoffile)
    logger.info('Sending Mail check your inbox in 2 minutes')
    mail_it(nameoffile, cc_list=None)
    logger.info('Stopping scan')

if __name__ == '__main__':
    main()
