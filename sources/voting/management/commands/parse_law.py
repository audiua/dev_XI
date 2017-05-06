import os
import glob
import datetime
import logging
from natsort import natsorted
from bs4 import BeautifulSoup
import re
from django.conf import settings
from django.core.management.base import BaseCommand
from voting.models import CounsilSession, Counsil, Deputy, Law, LawVoting

logger = logging.getLogger('voting_app')

class Command(BaseCommand):

    help = """Парсинг файлов html. 
    Получаемые данные хранятся в базе данных
    Комманда парсить сессии которых нет в базе
    """

    def __init__(self, *args, **kwargs):
        self.counsil = None
        self.counsil_session = None
        self.not_parse_page = []
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        path_in = os.path.join(settings.BASE_DIR, settings.VOTING_PDF_DIR)

        if not os.stat(path_in):
            logger.error("dir {} does not exist".format(path_in))
            self.stdout.write(self.style.ERROR("dir {} does not exist".format(path_in)))
            return

        # получаем папки сессии с файлами законов в html
        session_html_dirs_path = [f for f in glob.glob('{}/*'.format(path_in)) if os.path.isdir(f)]
        session_dir_names = [name.split('/')[-1] for name in session_html_dirs_path]

        parsed_sessions_dir_names = []
        try:
            parsed_sessions = CounsilSession.objects.values("voting_result_file").distinct()
            if parsed_sessions:
                parsed_sessions_dir_names = [session['voting_result_file'].replace('.pdf', '')
                                             for session in parsed_sessions]
        except CounsilSession.DoesNotExist:
            pass

        # берем еще не спарсеную сессию
        new_session_dirs = list(set(session_dir_names) - set(parsed_sessions_dir_names))
        if not new_session_dirs:
            self.stdout.write(self.style.NOTICE("All sessions are parsed"))
            return

        # парсим все новые файлы
        for new_session_dir in new_session_dirs:

            # clear dump objects for each session
            self.counsil = None
            self.counsil_session = None
            self.not_parse_page = []

            self.stdout.write("Start with dir '{}'".format(new_session_dir))
            # todo create task for workers
            for law in natsorted(glob.glob("{}/*-*.html".format(os.path.join(settings.BASE_DIR,
                                                                             settings.VOTING_PDF_DIR,
                                                                             new_session_dir)))):
                if law in self.not_parse_page:
                    continue

                self.stdout.write("start to parse a file '{}'".format(law))
                session_law = None
                session_law_deputies = []

                law_page_data = self.get_law_page_data(law)

                # проверяем что закон полностью на однойстранице
                # если закон на двух страницах - соединяем их, и исключаем вторую для парсинга
                if not law_page_data['sinle_page']:
                    law_file = law.split('/')[-1]
                    page_number = re.findall(r'(\d+)', law_file)[0]
                    next_page = int(page_number) + 1
                    law_part_file = law.replace('law-{}'.format(page_number), 'law-{}'.format(next_page))
                    self.not_parse_page.append(law_part_file)
                    self.stdout.write(self.style.WARNING("Закон из двух страниц '{}', '{}"
                                                         .format(law, law_part_file)))
                    law_page_data = self.get_law_page_data(law, second_part=law_part_file)

                # создаем или получаем совет
                if not self.counsil:
                    self.counsil = self.get_or_create_counsil(law_page_data)

                # создаем или получаем сессию совета
                if not self.counsil_session:
                    self.counsil_session = self.get_or_create_counsil_session(law_page_data, "{}.pdf"
                                                                              .format(new_session_dir))

                # создаем или получаем закон в сессии
                law_file_path_part = law.split('/')
                law_dir_file_path = os.path.join(law_file_path_part[-2], law_file_path_part[-1])
                if not session_law:
                    session_law = self.get_or_create_law(law_page_data, law_dir_file_path)

                # создаем депутатов для совета если их нет
                for deputy in law_page_data['deputy_name_voting']:
                    session_deputy_voting = {
                        'deputy': self.get_or_create_deputy(deputy[0:3]),
                        'vote': deputy[-1],
                        'law': session_law
                    }

                    # добавляем депутатов сессии которые уже есть в базе
                    # или созданы после фильтровки стоп слов
                    if session_deputy_voting['deputy']:
                        session_law_deputies.append(session_deputy_voting)

                # создаем именованные результаты голосования депутатов по закону
                for deputy_voting in session_law_deputies:
                    self.create_law_name_voting(deputy_voting)

    def get_law_page_data(self, law_html_file, second_part=None):
        """Парсинг html страницы закона"""

        with open(law_html_file, 'rb') as file:
            data = file.read()
            if second_part:
                with open(second_part, 'rb') as part:
                    self.stdout.write(self.style.NOTICE("concat two files {} + {}".
                                                        format(law_html_file, second_part)))
                    data += part.read()

            data = self._filter(data)

            soup = BeautifulSoup(data, "html.parser")
            page = {}
            try:

                page['counsil_title'] = soup.find('div', {'class': 'y2'}).text
                page['session_title'] = soup.find('div', {'class': ['y3', 'y184']}).text

                page['law_text'] = ''
                for line in soup.find_all('div', {'class': 'fc1'}):
                    page['law_text'] += line.text
                try:
                    page['voting_number'] = soup.find_all('div', {'class': 'fc1'})[-1].find_next_sibling("div", {"class": 'fc0'}).find_next_sibling("div").text
                except AttributeError as e:
                    page['voting_number'] = soup.find_all('div', {'class': 'fc1'})[-1].parent.find_next_sibling("div", {"class": 'fc0'}).find_next_sibling("div").text
                except:
                    logger.exception("ошибка получаения page['voting_number'] {}".format(law_html_file))

                # сначала проверить на совпадение а потом применять ---
                pattern = re.compile(r'(?u)([А-ЯІЄ]{1}[а-яєїі]+)\s([А-ЯІЄ]{1}[а-яєїі]+)\s([А-ЯІЄ]{1}[а-яєїі]+).*?(За|Відсутній|Не голосував|Проти|Утримався|Утрималися|Не голосував)')
                pattern_deputy_couple_line = re.compile(r'(?u)([А-ЯІЄ]{1}[а-яєїі]+)\s([А-ЯІЄ]{1}[а-яєїі]+)\s(?:</.*?>)([А-ЯІЄ]{1}[а-яєїі]+).*?(За|Відсутній|Не голосував|Проти|Утримався|Утрималися|Не голосував)')

                page['deputy_name_voting'] = re.findall(pattern, data.decode('utf-8'))
                page['deputy_name_voting'] += (re.findall(pattern_deputy_couple_line, data.decode('utf-8')))

                page['voting_result_for'] = soup.find('div', {'class': 'fc2'}).text
                page['voting_result_against'] = soup.find('div', {'class': 'fc3'}).text
                page['voting_result_contrary'] = soup.find('div', {'class': 'fc4'}).text
                page['voting_result_abstained'] = soup.find('div', {'class': 'fc4'}).find_next_sibling('div').text
                page['voting_result_missing'] = soup.find('div', {'class': 'fc4'}).find_next_sibling('div').find_next_sibling('div').text
                page['voting_resolution'] = soup.find('div', {'class': 'ff4'}).text
                page['sinle_page'] = bool(page['voting_resolution'])
            except AttributeError as e:
                # законы которые состоят из двух страниц
                logger.exception('ошибка получаения page {}'.format(law_html_file))
                page['sinle_page'] = False

        return page


    def get_or_create_counsil(self, law_page):
        counsil, created = Counsil.objects.get_or_create(title=law_page['counsil_title'])
        if created:
            self.stdout.write(self.style.SUCCESS("created a counsil - {}".format(counsil.title)))
        return counsil

    def get_or_create_counsil_session(self, law_page, voting_file):
        number = re.compile(r'(\d+)\s+', re.IGNORECASE)
        from_date = re.compile(r'(\d+)[.|_](\d+)[.|_](\d+)')
        date_items = from_date.findall(law_page['session_title'])[0]
        date = datetime.date(int('20' + date_items[2]), int(date_items[1]), int(date_items[0]))
        session_number = number.match(law_page['session_title']).group()
        counsil_session, created = CounsilSession.objects.get_or_create(title=law_page['session_title'], counsil=self.counsil,
                                                                        defaults={
                                                                            'title': law_page['session_title'],
                                                                            'voting_result_file':voting_file,
                                                                            'number': session_number,
                                                                            'from_date': date,
                                                                        })
        if created:
            self.stdout.write(self.style.SUCCESS("created a counsil_session - {}".format(counsil_session.title)))

        return counsil_session

    def get_or_create_deputy(self, data):
        """Создание или получение депутата"""

        # исключения из назвы депутатов
        exclude_full = [
                   'Героїв Небесної Сотні',
                   'Фелікс Енерджи Груп',
                   'Уповноважити Сільверстюк Валентину',
                   'Єпархії Української Православної',
                   'Тарасія Константинопольського Переяслав',
                   'Товариства Червоного Хреста']

        stop_words = ['України']

        name = " ".join(data)
        if name in exclude_full:
            return None

        for stop_word in stop_words:
            if name.find(stop_word) != -1:
                return None


        deputy, created = Deputy.objects.get_or_create(name=name, counsil=self.counsil)
        if created:
            self.stdout.write(self.style.SUCCESS("created a deputy - {}".format(deputy.name)))
        return deputy

    def get_or_create_law(self, law_page, law_file):
        """Создание или получение закона"""
        voting_result ="{}, {}, {}, {}".format(law_page['voting_result_for'],
                                           law_page['voting_result_against'],
                                           law_page['voting_result_abstained'],
                                           law_page['voting_result_missing'])
        law, created = Law.objects.get_or_create(text=law_page['law_text'], session = self.counsil_session, law_file_name=law_file,
                                                 defaults={
                                                           'resolution': law_page['voting_resolution'],
                                                           'voting_result': voting_result,
                                                           'voting_number': law_page['voting_number']})
        if created:
            self.stdout.write(self.style.SUCCESS('created a session law - {}, stored in file "{}"'.format(law.text.strip(), law.law_file_name)))
        return law


    def create_law_name_voting(self, data):
        """Создание голосования депутата"""
        self.stdout.write(self.style.SUCCESS("created a deputy voting - {}={}, for file {}".format(data['deputy'], data['vote'], data['law'].law_file_name)))
        LawVoting.objects.create(deputy=data['deputy'], law=data['law'], vote=data['vote'])


    def _filter(self, data):
        """нормализация данных для парсинга"""
        data = data.decode('utf-8').replace('<span class="_ _0"></span>', '')
        data = data.replace('<span class="_ _1"></span>', '')
        data = data.replace('<span class="_ _3"></span>', '')
        data = data.replace('', ' ')
        return data.encode('utf-8')
