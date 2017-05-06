import os, glob
import subprocess
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    help = """Конвертирует pdf в html.
Параметры in, out пути к папкам, относительно корня проекта.
Пример: python manage.py pdf2html /path/to/pdf /path/to/store/html
    """
    def add_arguments(self, parser):
        parser.add_argument('in')

    def handle(self, *args, **options):
        path_in = os.path.join(settings.BASE_DIR, options['in'])
        if not os.stat(path_in):
            raise CommandError("dir {} does not exist".format(path_in))

        files = [f for f in glob.glob('{}/*.pdf'.format(path_in))]
        for file in files:
            session_dir = file.split('/')[-1].replace('.pdf', '').replace(' ', '\\ ')
            file = file.replace(' ', '\\ ')

            subprocess.call('pdf2htmlEX --optimize-text 1 --split-pages 1 --page-filename law-%d.html --dest-dir voting_files/{} {}'.format(session_dir, file),  shell=True)

            #todo create task for parsing session laws or signals event

