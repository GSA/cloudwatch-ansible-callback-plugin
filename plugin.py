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
#import boto3

#cloudwatch_events = boto3.client("events")


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
        #
        # # Put an event
        # response = cloudwatch_events.put_events(
        #     Entries=[
        #         {
        #             "Detail": data,
        #             "DetailType": type,
        #             "Resources": [
        #                 # TODO resource ARN?
        #                 "RESOURCE_ARN",
        #             ],
        #             "Source": "gov.gsa.ansible",
        #         }
        #     ]
        # )
        pprint(type)
        pprint(data)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.put_event('ansible-run-failed', {
            'host': result._host.get_name(),
        })
        self.put_event("runnerFailed", {"host": result._host.get_name(), "dump": vars(result)})

    def v2_runner_on_ok(self, result):
        if result._result['changed']:
            self.put_event("ansible-run-task-changed", {
                "host": result._host.get_name(),
                "task": result._task,
                "action": result._task_fields['action'],
                "action_args": result._task_fields['args'],
            })
        else:
            self.put_event("ansible-run-task-ok", {
                "host": result._host.get_name(),
                "task": result._task,
                "action": result._task_fields['action'],
                "action_args": result._task_fields['args'],
            })
        #self.put_event("runnerOkay", {"host": result._host.get_name(), "dump": vars(result)})

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
