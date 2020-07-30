# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import absolute_import, division, print_function

import json, sys
from pprint import pformat, pprint
from __main__ import cli

__metaclass__ = type

# not only visible to ansible-doc, it also 'declares' the options the plugin requires and how to configure them.
DOCUMENTATION = """
  callback: cloudwatch
  callback_type: default 
  requirements:
    - whitelist in configuration
  short_description: logs aws events
  version_added: "2.0"
  description:
      - logs aws events
"""
from datetime import datetime

from ansible.plugins.callback import CallbackBase
import boto3
import os
import json

cloudwatch_events = boto3.client("events")#, aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])


class CallbackModule(CallbackBase):
    """
        self.runner_on_unredef v2_playbook_on_start(self, playbook):
    This callback module sends aws events for each ansible callback.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'cloudwatch'

    # only needed if you ship it and don't want to enable by default
    # CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):

        # make sure the expected objects are present, calling the base's __init__
        super(CallbackModule, self).__init__()

        # start the timer when the plugin is loaded, the first play should start a few milliseconds after.
        self.start_time = datetime.now()

    def put_event(self, type, data):
        # Create CloudWatchEvents client
        # cloudwatch_events = boto3.client("events")
       
        # Put an event
        response = cloudwatch_events.put_events(
            Entries=[
                {
                    #"Detail": {"instance-id": "test", "state": "terminated"},#str(data),
                    #"DetailType": "EC2 Instance State-change Notification",
                    #"Resources": [
                        # TODO resource ARN?
                    #    "RESOURCE_ARN",
                    #],
                    "Source": "gov.gsa.ansible",
                    #'Time': datetime(2020, 7, 28),
                    #'Source': 'string',
                    #'Resources': [
                    #    'string',
                    #],
                    'DetailType': 'string',
                    'Detail': json.dumps({"test":"data"}),#data),
                    #'EventBusName': 'string',
                    #'Region': 'us-east-1'
                }
            ]
        )
        #print("response = " + json.dumps(response,indent=4))
        pprint(type)
        pprint(data)

    def _pop_keys_by_prefix(self, d, prefix='_'):
        for k in list(d.keys()):
            if k.startswith(prefix):
                d.pop(k)
        return d


    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.put_event('ansible-run-failed', {
            'host': result._host.get_name(),
        })
        self.put_event("runnerFailed", {"host": result._host.get_name(), "dump": vars(result)})

    def v2_runner_on_ok(self, result):
        #print(type(result._task_fields['args']))
        #if isinstance(result._task_fields['args'], dict):
        #    print(type(result._task_fields['args']))
        #    print(result._task_fields['args'].keys())
        action_args = self._pop_keys_by_prefix(result._task_fields['args'])
        action_args = json.dumps(action_args)
        #else:
        #    action_args = "test"
        #action_args = json.loads(result._task_fields['args'])
        if result._result['changed']:
            self.put_event("ansible-run-task-changed", {
                "host": result._host.get_name(),
                "task": result._task,
                "action": result._task_fields['action'],
                "action_args": action_args,
            })
        else:
            self.put_event("ansible-run-task-ok", {
                "host": result._host.get_name(),
                "task": result._task,
                "action": result._task_fields['action'],
                "action_args": action_args,
            })

    def v2_runner_on_skipped(self, result):
        self.put_event('ansible-run-skip', {
            'host': result._host.get_name(),
        })

    def v2_runner_on_unreachable(self, result):
        self.put_event('ansible-run-unreachable', {
            'host': result._host.get_name(),
        })

    def v2_playbook_on_cleanup_task_start(self, task):
        self.put_event('ansible-run-completed', vars(task))

    def v2_playbook_on_play_start(self, play):
        self.put_event('ansible-run-begin', {
            'name': play.get_name().strip(),
            'properties': play._ds,
        })

    def v2_playbook_on_notify(self, handler, host):
        self.put_event('ansible-run-notify', {
            'host': host.get_name(),
        })
    
    def v2_playbook_on_stats(self, stats):
        self.put_event('ansible-run-stats', vars(stats))
