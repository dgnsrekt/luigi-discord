import luigi
from luigi_discord import notify, DiscordBot


class HelloWorldTask(luigi.Task):
    task_namespace = 'examples'

    def output(self):
        return luigi.LocalTarget('fake.log')

    def run(self):
        task = self.__class__.__name__
        print('-------------------------')
        print('{task} says: Hello world!')
        print('-------------------------')
        self.output()


class NextTask(luigi.Task):

    def require(self):
        return HelloWorldTask()

    def run(self):
        assert self.input() == True


url = 'https://discordapp.com/api/webhooks/{}/{}'

bogdabot = DiscordBot(url=url, events=['SUCCESS', 'FAILURE'])

with notify(bogdabot):
    luigi.build([NextTask()])
