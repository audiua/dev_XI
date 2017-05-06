import os
import glob
import subprocess
import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger('voting_app')


class Command(BaseCommand):

    help = """Конвертирует pdf в html.
Параметры in, out пути к папкам, относительно корня проекта.
Пример: python manage.py pdf2html
    """

    def handle(self, *args, **options):
        path_in = os.path.join(settings.BASE_DIR, settings.VOTING_PDF_DIR)
        if not os.stat(path_in):
            logger.warning("dir {} does not exist".format(path_in))
            self.stdout.write(self.style.ERROR("dir {} does not exist".format(path_in)))
            return

        files = [f for f in glob.glob('{}/*.pdf'.format(path_in))]
        for file in files:
            session_dir = file.split('/')[-1].replace('.pdf', '').replace(' ', '\\ ')
            file = file.replace(' ', '\\ ')

            try:
                subprocess.call('pdf2htmlEX --optimize-text 1 --split-pages 1 --page-filename law-%d.html --dest-dir voting_files/{} {}'.format(session_dir, file),  shell=True)
            except:
                logger.exception("ошибка конвертирования файлов")
                self.stdout.write(self.style.ERROR("ошибка конвертирования файлов"))

            #todo create task for parsing session laws or signals event

