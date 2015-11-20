# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python program to enable/disable a given ESX alarm
Parameters:
	-s: IP address of vCenter to connect to
	-u: vCenter user
	-p: vCenter password
	-o: vCenter secure port (optional. default is 443)
	-n: ESX alarm object name (for example 'alarm.StorageConnectivityAlarm')
	-e | -d: -e to enable the alarm; -d to disable the alarm

Syntax example to disable an alarm:
	set_alarm_state.py -s 1.1.1.1 -u admin -p password -n alarm.StorageConnectivityAlarm -d
Syntax example to enable an alarm:
	set_alarm_state.py -s 1.1.1.1 -u admin -p password -n alarm.StorageConnectivityAlarm -e

Requirements:
	python2.7
	pyVmomi - python library for VMware SDK developed by VMware. Details for installation are
	on github: https://github.com/vmware/pyvmomi

This code is developed in a lab ESX environment with self-signed certificates. It requires a special hack
that should NOT be used in production environments. Please remove/comment out the hack below when running
with valid vCenter Certificates.
"""

import atexit
import argparse
import getpass

################################################
# below lines are a hack for my lab environment
# production environments with valid vCenter Certificates
# do not need this code
import requests
requests.packages.urllib3.disable_warnings()

import ssl

try:
 _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
 # Legacy Python that doesn't verify HTTPS certificates by default
 pass
else:
 # Handle target environment that doesn't support HTTPS verification
 ssl._create_default_https_context = _create_unverified_https_context
# end hack
#################################################

from pyVim import connect
from pyVmomi import vmodl

def get_args():
    """Get command line args from the user.
    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter')

    # because -h is reserved for 'help' we use -s for service
    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    # because we want -p for password, we use -o for port
    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('-n', '--alarmname',
			required=True,
			action='store',
			help='Alarm name to enable/disable')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-e', '--enabled',
			action='store_true',
			help='Enable an alarm')
    group.add_argument('-d', '--disabled',
			action='store_false',
			help='Disable an alarm')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args

def main():
    args = get_args()

    try:
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port))

        atexit.register(connect.Disconnect, service_instance)


	# Set the enabled state for the given alarm
	alarm_manager = service_instance.content.alarmManager
	alarms = alarm_manager.GetAlarm()
	for alarm in alarms:
		if alarm.info.systemName == args.alarmname:			
			print alarm.info.enabled
			spec = alarm.info
			if args.enabled:
				spec.enabled = args.enabled
			if not args.disabled:
				spec.enabled = args.disabled
			alarm.ReconfigureAlarm(spec)
			print alarm.info.enabled
			break

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return service_instance

#start the program
if __name__ == "__main__":
    main()

