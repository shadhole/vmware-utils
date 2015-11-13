# VMware vSphere Python SDK
# Copyright (c) 2008-2013 VMware, Inc. All Rights Reserved.
#
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
Python program with utility functions for virtual environments	
	enable_alarm
	disable_alarm
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

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args

# helper function to list basic info about all alarms in the vCenter instance
def list_alarms(alarms):

	for alarm in alarms:
		print "Alarm object:" + alarm.alarminfo.alarm
		print "Alarm name:" + alarm.alarminfo.name
		print "Alarm entity" + alarm.alarminfo.entity
		print "Alarm enabled?" + alarm.alarminfo.enabled
	return

def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """

    args = get_args()

    try:
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port))

        atexit.register(connect.Disconnect, service_instance)


        print "\nHello World!\n"
	"""
        print "If you got here, you authenticted into vCenter."
        print "The server is {}!".format(args.host)
        # NOTE (hartsock): only a successfully authenticated session has a
        # session key aka session id.
        session_id = service_instance.content.sessionManager.currentSession.key
        print "current session id: {}".format(session_id)
        print "Well done!"
        print "\n"
        print "Download, learn and contribute back:"
        print "https://github.com/vmware/pyvmomi-community-samples"
        print "\n\n"
	"""
 
	alarm_manager = service_instance.content.alarmManager
	alarms = None
	alarms = alarm_manager.GetAlarm
#	list_alarms(alarms)
#	for alarm in alarms:
	print alarms.val

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return service_instance

#start the program
if __name__ == "__main__":
    main()

