import os
import logging
import inspect
from contextlib import contextmanager
from collections import defaultdict
import luigi
from luigi_discord.discord_webhook import DiscordWebHook

log = logging.getLogger('luigi_discord')
log.setLevel(logging.DEBUG)


class DiscordMessage:
    def __init__(self, title=None, fields={}, success=None):
        self.title = title
        self.fields = fields
        self.success = success


class DiscordBot:

    def __init__(self, url,
                 events=['FAILURE'],
                 max_events=5,
                 author='Luigi-discord Bot',
                 task_representaion=str,
                 print_env=[]):
        if not isinstance(events, list):
            raise ValueError('events must be a list, {type(events)} given')

        self.events = events
        self._events_to_handle = self.events + ['SUCCESS', 'START']
        self.webhook_client = DiscordWebHook(url, author=author)  # IDEA:
        self.max_events = max_events
        self.event_queue = defaultdict(list)
        self.task_repr = task_representaion
        self._print_env = print_env

    def send_notification(self):
        message = self._format_message()
        if message:
            self.webhook_client.send_message(message)  # TODO: Implement

    def set_handlers(self):
        self._init_handlers()
        for event in self._events_to_handle:
            if event not in self._events_to_handle:
                raise ValueError('{even} is not a vaild event type.')
            handler = self._event_handlers[event]['luigi_handler']
            function = self._event_handlers[event]['function']
            luigi.Task.event_handler(handler)(function)
        return True

    def _init_handlers(self):
        self._event_handlers = {
            'SUCCESS': {
                'luigi_handler': luigi.Event.SUCCESS,
                'function': self._success
            },
            'FAILURE': {
                'luigi_handler': luigi.Event.FAILURE,
                'function': self._failure
            },
            'START': {
                'luigi_handler': luigi.Event.START,
                'function': self._start
            },
            'MISSING': {
                'luigi_handler': luigi.Event.DEPENDENCY_MISSING,
                'function': self._missing
            },
            'PROCESSING_TIME': {
                'luigi_handler': luigi.Event.PROCESSING_TIME,
                'function': self._processing_time
            }
        }

    def _success(self, task):
        task = self.task_repr(task)
        self.event_queue['FAILURE'] = [
            fail for fail in self.event_queue['FAILURE'] if task != fail['task']]
        self.event_queue['MISSING'] = [miss for miss in self.event_queue['MISSING'] if task != miss]
        self.event_queue['SUCCESS'].append(task)

    def _failure(self, task, exception):
        task = self.task_repr(task)
        failure = {'task': task, 'exception': str(exception)}
        self.event_queue['FAILURE'].append(failure)

    def _missing(self, task):
        task = self.task_repr(task)
        self.event_queue['MISSING'].append(task)

    def _start(self, task):
        task = self.task_repr(task)
        self.event_queue['START'].append(task)

    def _processing_time(self, task):
        raise NotImplementedError

    def _format_message(self):
        job = os.path.basename(inspect.stack()[-1][1])
        title = f'*Status report for {job}*'

        if self._only_success():
            if 'SUCCESS' in self.events:  # TODO
                messages = {'SUCCESS': ['Job ran successfully!']}
                success = True
            else:
                return None
        else:
            messages = self._event_messages()  # TODO
            success = False

        if self._print_env:
            env_to_print = [f"{env_var}={os.environ.get(env_var, '')}" for env_var in self._print_env]

            messages['Environment'] = env_to_print
        return DiscordMessage(title=title, fields=messages, success=success)  # TODO

    def _only_success(self):
        return len(self.event_queue['SUCCESS']) == len(self.event_queue['START'])

    def _event_messages(self):
        messages = {}
        for event_type in self.events:
            if event_type in self.event_queue:
                label = event_type

                if not self.event_queue[event_type]:
                    messages[label] = ['none']

                elif len(self.event_queue[event_type]) > self.max_events:
                    messages[label] = [f'more than {self.max_events} events, check logs.']

                else:
                    messages[label] = []

                    for event in self.event_queue[event_type]:
                        try:
                            # only "failure" is a dict
                            task = event['task']
                            exception = event['exception']
                            msg = f'Task: {task}; Exception: {exception}'
                            messages[label].append(msg)
                        except TypeError:
                            # all the other events are str
                            messages[label].append(event)
        return messages


@contextmanager
def notify(bogdabot):
    bogdabot.set_handlers()
    yield
    bogdabot.send_notification()
