'''This script will be used for One Link configuration application on Multiple devices'''

import sys
import os
from netmiko import ConnectHandler
from paramiko.ssh_exception import SSHException 
import time
from socket import gethostbyname
import system_snmp
import snmp_if_utils
import getpass
from datetime import datetime
import threading
from multiprocessing import Process
from time import sleep
lock = threading.Lock()
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import PIPE, Popen
import zipfile
from python_logging import initialize_logger
from python_logging import default_argparse
from itertools import islice

__author__ = "ashay@microsoft.com"
__copyright__ = "copyrighted by Microsoft"
__contributors__ = ["ashay"]
__version__ = "1.0"
__maintainer__ = "Ashay Phynet- DRI <ashay@microsoft.com>"
__maintainer__ = "Ashay Phynet - DRI <ashay@microsoft.com>"
__team_email__ = "gnsfabmonperf@microsoft.com"
__script_name__ = os.path.basename(sys.argv[0])

logger = initialize_logger(default_argparse(), __script_name__)


username = getpass.getuser()
password = getpass.getpass('Enter GME Password:   ').strip()
threadlimiter = threading.BoundedSemaphore(10)

def connection(device):
	device_input = {'device_type': __get_netmiko_device_os__(device),
				'ip':   gethostbyname(device),
				'username': username,
				'password': password,
				'global_delay_factor': 0.7
				}
	
	try:
		connection = ConnectHandler(**device_input)
		return connection
	except (EOFError, SSHException):
		print('SSH is not enabled for this device {}.'.format(device))
		

def __get_netmiko_device_os__(device):
	'''This function will be used to get vendor type'''
	
	oid=".1.3.6.1.2.1.1.1.0"
	try:
		snmp_data = system_snmp.snmp_get(device, oid)[1]
	except:
		text = open("notworkingt3.txt", "w")
		text.write('Device is not sending SNMP return {}'.format(device))
		logger.error('Device is not sending SNMP return {}'.format(device))
		text.close()

	if "arista" in snmp_data.lower():
		return "arista_eos"
	elif "nx-os" in snmp_data.lower():
		return "cisco_nxos"
	elif "dell" in snmp_data.lower():
		return "dell_force10"
	else:
		raise UnsupportedDeviceType("Unsupported device. Only Arista, NX-OS, and Dell supported.")


def save_config(connection):
    '''Save the configuration on a device'''
    save_command = "copy run start"
    try:
        connection.send_command(save_command)
    except Exception as e:
        raise OperationalCommandFailed("Failed to save configuration.")


def pre_check(device, text_file, local_conn):
	'''This function will be used to get data out from devices'''
	
	
	try:	
		#local_conn = connection(device)		
		out1 = local_conn.send_command('{}'.format('show version | grep "is:"')).strip()
		out2 = local_conn.send_command('{}'.format('show ip bgp sum')).strip()
		out3 = local_conn.send_command('{}'.format('show run | grep "boot"')).strip()
		text_file.write('================================={} Pre check ================================\n\n'.format(device))
		
		text_file.write('=================================show version | grep "is:" ================================\n\n')
		text_file.write('{}\n\n'.format(out1))
		text_file.write('=================================show ip bgp sum ================================\n\n')
		text_file.write('{}\n\n'.format(out2))
		text_file.write('=================================show run | grep "boot" ================================\n\n')
		text_file.write('{}\n\n'.format(out3))
		logger.info('Writing Pre Checks for : {}'.format(device))	
	except:		
		text_file.write('{} : No able to login \n'.format(device))
		logger.error('{} : Not able to login'.format(device))
	
def post_check(device, text_file, local_conn_again):
	'''This function will be used to get data out from devices'''
	
	
	try:	
		#local_conn = connection(device)		
		out1 = local_conn_again.send_command('{}'.format('show version | grep "is:"')).strip()
		out2 = local_conn_again.send_command('{}'.format('show ip bgp sum')).strip()
		out3 = local_conn_again.send_command('{}'.format('show run | grep "boot"')).strip()
		sys = local_conn_again.send_command('show ver | grep "is:"').strip().split(':')[-1].replace('/','')
		bootsys = local_conn_again.send_command('show run | grep "boot"').strip().split(':')[-1].replace('/','')
		text_file.write('================================={} Post check ================================\n\n'.format(device))
		
		text_file.write('=================================show version | grep "is:" ================================\n\n')
		text_file.write('{}\n\n'.format(out1))
		text_file.write('=================================show ip bgp sum ================================\n\n')
		text_file.write('{}\n\n'.format(out2))
		text_file.write('=================================show run | grep "boot" ================================\n\n')
		text_file.write('{}\n\n'.format(out3))
		text_file.write('{} : PostChecks : Device has been fixed : {} : {}\n'.format(device, sys, bootsys))
		logger.info('Writing Post Checks for : {}'.format(device))	
	except:		
		text_file.write('{} : No able to login \n'.format(device))
		logger.error('{} : Not able to login'.format(device))
	
def ping(device):
	response = os.popen('ping -c 1 {} | grep 64'.format(device), 'r').readline()
	return response
		

def needed_info(device, local_conn, text_file):
	try:	
		sys = local_conn.send_command('show ver | grep "is: "').strip().split(':')[-1].replace('/','')			
		bootsys = local_conn.send_command('show run | grep "boot"').strip().split(':')[-1].replace('/','')
		bootflash = local_conn.send_command('dir bootflash: | grep ".4e"').strip().split(' ')[-1]
			
	except:		
		logger.error('{} : Not able to login'.format(device))
		text_file.write('{} : Not able to Login to Device\n'.format(device))
	return sys, bootsys, bootflash
		

			
		
def implementation(device, text_file, local_conn):
	'''This function will be used to apply one line configuration on devices'''	

	sys, bootsys, bootflash = needed_info(device, local_conn, text_file)
	#print (sys, bootsys, bootflash)
	if 'n9000-dk9.6.1.2.I3.4e.bin' in bootflash:			
		config_command_1 = list()
		config_command_1 = ['boot nxos bootflash:/{}'.format(bootflash)]
		config_command_2 = list()
		config_command_2 = ['exit', 'cppy run start']
		config_command_3 = list()
		config_command_3 = ['fast-reload nxos bootflash:///n9000-dk9.6.1.2.I3.4e.bin non-interruptive']
		try:	
			local_conn.send_config_set(config_command_1)	
			print('Changing boot')
			sleep(10)
			local_conn.send_config_set(config_command_2)
			print('Saving config')
			sleep(10)
			print('fast-rebooting there will be sleep for 5 minutes. Please wait..........')
			local_conn.send_config_set(config_command_3)					
		except:
			sleep(240)
			response = ping(device)
			if response:
				print ('Device is up again')	
				local_conn_again = connection(device)				
				sys = local_conn_again.send_command('show ver | grep "is: "').strip().split(':')[-1].replace('/','')
				if 'n9000-dk9.6.1.2.I3.4e.bin' in sys:
					print ('Device has been upgraded')
					logger.info('Device has been upgraded : {}'.format(device))
					post_check(device, text_file, local_conn_again)

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
	zip_write = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED )
	zip_write.write(prezip)
	zip_write.close()		
	
	file = '{}.zip'.format(nameoffile)	
	to_address = '{}@microsoft.com'.format(username)

	subject = 'scanning report run by {}'.format(username)
	body = 'Please find attachments for your scanning job'
	cc_string = str()
	if cc_list != None:
		for name in cc_list: cc_string += "-c {} ".format(name)
	if file is None:
		argument = """echo "{}" | mutt -s "{}" {} {}""".format(body, subject, to_address, cc_string)
	elif type(file) == type(list()):
		attachments = ""
		for entry in file: attachments += "-a {0} ".format(entry)
		argument = """echo "{3}" | mutt -s "{1}" {4} {2} {0}""".format(attachments, subject, to_address, body, cc_string)
	else:
		argument = """echo "{3}" | mutt -s "{1}" {4} {2} -a{0}""".format(file, subject, to_address, body, cc_string)	
	return run_from_shell(argument)

	
	
def check_info(device, text_file):
	local_conn = connection(device)	
	sys, bootsys, bootflash = needed_info(device, local_conn, text_file)
	try:
		if sys == bootsys:	
			print('{}:Device is running in golden state'.format(device))
			text_file.write('{} : Device is running in golden state : {} : {}\n'.format(device, sys, bootsys))
		else:
			print('{}:Device Need to be repaired'.format(device))
			text_file.write('{} : Device Need to be repaired : {} : {}\n'.format(device, sys, bootsys))
	except:
		print('{}:could not test'.format(device))
		
		
	
def application(device, text_file):
	local_conn = connection(device)
	nameoffile = '{}_{}'.format(device, username)
	sys, bootsys, bootflash = needed_info(device, local_conn, text_file)	
	response = ping(device)
	if response:
		print ('Device is up Before Change')
		if 'n9000-dk9.6.1.2.I3.4e.bin' in sys:
			print('Device {} is running in the golden state'.format(device))
			text_file.write('{} : Device is running in golden state : {} : {}\n'.format(device, sys, bootsys))
		else:
			pre_check(device, text_file, local_conn)
			sleep(5)
			implementation(device, text_file, local_conn)		
			logger.info('Sending Mail for {} inbox in 2 minutes'.format(device))
			print'\n'
			mail_it(nameoffile, cc_list=None)	
		
	
def thread_main_scan(list, text_file):
	for host in list:
		device = host.strip()		
		my_thread = threading.Thread(target=check_info, args=(device, text_file))
		my_thread.start()
		sleep(.5)
		my_thread.join()
	main_thread = threading.currentThread()
	threading.active_count()
	for some_thread in threading.enumerate():
		if some_thread != main_thread:			
			print some_thread
			some_thread.join()

			
def multi_threading_scan():
    '''Mulit-threading function arg will be command and file name'''

    start_time = datetime.now()
    getfile = open('devices_{}_scan.txt'.format(username), 'r')
    devices = getfile.readlines()
    try:
        text_file = open("ScanData_{}".format(username), "w")
    except Exception as e:
        logger.error('Error: {}'.format(e))
        sys.exit(1)

    list1 = [l.strip() for l in devices]
    for i in [list1[x:x + 100] for x in range(0, len(list1), 100)]:
        print('MultiThreading currently running for {}'.format(i))
        thread_main_scan(i, text_file)
    text_file.close()
	
	
def thread_main_config(list):
	for host in list:
		device = host.strip()
		text_file = open("ConfigData_3164_{}".format(device), "w")
		my_thread = threading.Thread(target=application, args=(device, text_file))
		my_thread.start()
		sleep(.5)
		my_thread.join()
	main_thread = threading.currentThread()
	threading.active_count()
	for some_thread in threading.enumerate():
		if some_thread != main_thread:			
			print some_thread
			some_thread.join()				
	text_file.close()	
	
def multi_threading_config():
    '''Mulit-threading function arg will be command and file name'''
    start_time = datetime.now()
    getfile = open('devices_3164_config.txt'.format(username), 'r')
    devices = getfile.readlines()
    list1 = [l.strip() for l in devices]
    for i in [list1[x:x + 5] for x in range(0, len(list1), 5)]:
        print('MultiThreading currently running for {}'.format(i))
        thread_main_config(i)		
    	
		
def one_by_one():
	getfile = open('devices_3164_config.txt'.format(username), 'r')
	devices = getfile.readlines()
	for host in devices:		
		device = host.strip()
		logger.info('==================================')
		logger.info('Going for {}\n'.format(device))
		text_file = open("ConfigData_3164_{}".format(device), "w")
		application(device, text_file)
		text_file.close()
	
		
def main():
	'''Main Funcion'''
	print '\n'
	logger.info('This script will be used for boot var fix only. '
	'devices_{}_config.txt for Config devices and devices_{}_scan.txt for scanning devices. '
	'output will be saved ScanData_{}.txt and ConfigData_{}.txt respectively' .format(username, username, username, username))
	print '\n'
	print '\n'
	print('\n1) Scanning of Device, checking the bootvar config\n2) Configuring the device, Fixing the bootvar config\n3) Exit')		

	choice = raw_input('\nPlease provide your choice: ').strip()

	# Health check
	if choice == '1':
		multi_threading_scan()

	elif choice == '2':
		#multi_threading_config()
		one_by_one()
	
	elif choice == '3':
		sys.exit()
	else:
		print('Select some option')

if __name__ == '__main__':
    main()

	
