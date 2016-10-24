# -*- coding: utf-8 -*-
import requests

from bs4 import BeautifulSoup
from django.core.files.storage import default_storage
from parser import ListSubjectsParser, SubjectParser, StudentParser
from sippa.settings import BASE_AWS_URL


class SIPPAWrapper(object):

    START_URL = 'https://sistemas.quixada.ufc.br/sippa/'
    CAPTCHA_URL = 'https://sistemas.quixada.ufc.br/sippa/captcha.jpg'
    ACTION_FORM_URL = 'https://sistemas.quixada.ufc.br/ServletCentral'

    SUBJECT_CLASS_URL = 'https://sistemas.quixada.ufc.br/ServletCentral?comando=CmdListarFrequenciaTurmaAluno&id=%s'

    FILES_URL = 'https://sistemas.quixada.ufc.br/sippa/aluno_visualizar_arquivos.jsp?sorter=1'
    EXAMS_URL = 'https://sistemas.quixada.ufc.br/ServletCentral?comando=CmdVisualizarAvaliacoesAluno'
    HOMEWORK_URL = 'https://sistemas.quixada.ufc.br/sippa/aluno_enviar_trabalhos.jsp'
    SECOND_CALL_URL = 'https://sistemas.quixada.ufc.br/sippa/aluno_cadastrar_solicitacao.jsp'
    CALENDAR_URL = 'https://sistemas.quixada.ufc.br/sippa/aluno_listar_recessos.jsp'

    def __init__(self):
        self.__identifier = None
        self.__session = None
        self.__login = None
        self.__password = None
        self.__captcha_url = None

    @staticmethod
    def format_subject_url(class_identifier):
        return SIPPAWrapper.SUBJECT_CLASS_URL % class_identifier

    def download_file(self):
        local_filename = 'captchas/%s.jpg' % self.__session

        cookies = dict(JSESSIONID=self.__session)
        r = requests.get(SIPPAWrapper.CAPTCHA_URL, stream=True, verify=False, cookies=cookies)

        with default_storage.open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        return '%s/%s' % (BASE_AWS_URL, local_filename)

    def start_auth(self):
        """
        Inicia o processo de autenticação no SIPPA.

        Exemplo de retorno: {"identifier": "ABCDE12345", "captcha_url": "http://lorempixel.com/200/200"}
        :return: JSON contendo um identificador da sessão e uma url para download do captcha.
        :rtype: dict
        """
        sippa_request = requests.get(SIPPAWrapper.START_URL, verify=False)

        self.__session = sippa_request.cookies['JSESSIONID']
        self.__captcha_url = self.download_file()

        return {"identifier": self.__session, "captcha_url": self.__captcha_url}

    def run(self, session, login, password, captcha_value):
        """
        Executa o processo de pesquisar as informações das disciplinas do aluno configurado no objeto.

        Em caso de sucesso retorna um dicionário com a seguinte estrutura:
        {
            "student": {
                "name": "Nome do aluno",
                "registration": "00000000"
            },
            "subjects": [
                {
                    "code": "qxd0000",
                    "class_identifier": "123456",
                    "name": "Disciplina 1",
                    "average": null,
                    "teacher": {
                        "name": "Nome do professor",
                        "email": "email@email.com",
                        "avatar_url": "http://lorempixel.com/200/200"
                    },
                    "notices": [
                        {
                            "order": 1,
                            "date": "dd/mm/YYYY",
                            "text": "Notícia"
                        }
                    ],
                    "lesson_plans": [
                        {
                            "lesson": 1,
                            "description": "Exemplo de aula",
                            "planned_description": "Exemplo de aula",
                            "date": "dd/mm/YYYY",
                            "presence_hours": "0"
                        }
                    ],
                    "frequency": {
                        "text": "100% de Frequência; 0 Presenças em Horas; 0 Faltas em Horas",
                        "presence_hours": 0,
                        "absence_hours": 0,
                        "max_hours": 0
                    },
                    "exams": [
                        {
                            "order": 1,
                            "short_description": "AP1",
                            "description": "Primeira Avaliação Parcial",
                            "weight": "1.0",
                            "value": null
                        }
                    ],
                    "files": [
                        {
                            "description": "Lista_de_exercicios.pdf",
                            "date": "dd/mm/YYYY",
                            "order": 1
                        }
                    ],
                    "second_call_options": [
                        {
                            "order": 1,
                            "description": "AP1",
                            "code": "1234"
                        }
                    ],
                    "second_call_history": [
                        {
                            "order": 1,
                            "exam_description": "AP1",
                            "exam_code": "1234",
                            "motive": "Justificativa da solicitação",
                            "date": "dd/mm/YYYY"
                        }
                    ],
                    "calendar": {
                        "start_period": "dd/mm/YYYY",
                        "end_period": "dd/mm/YYYY",
                        "start_final_exams": "dd/mm/YYYY",
                        "end_final_exams": "dd/mm/YYYY",
                        "holidays": [
                            {
                                "order": 1,
                                "date": "dd/mm/YYYY",
                                "description": "Feriado nacional",
                                "kind": "Feriado Nacional"
                            }
                        ]
                    },
                    "homework": [
                        {
                            "order": 1,
                            "file": null,
                            "description": "Trabalho",
                            "max_date": "dd/mm/YYYY"
                        }
                    ]
                }
            ]
        }

        Em caso de erro retorna um dicionário com a seguinte estrutura:
        {"error_message": "Message", "error_code": "code"}

        :rtype: dict
        """
        self.__session = session
        self.__login = login
        self.__password = password

        cookies = dict(JSESSIONID=self.__session)
        payload = {'login': self.__login, 'senha': self.__password,
                   'conta': 'aluno', 'captcha': captcha_value,
                   'comando': 'CmdLogin'}

        sippa = requests.post(SIPPAWrapper.ACTION_FORM_URL, verify=False, cookies=cookies, data=payload)

        subjects = ListSubjectsParser(sippa.content)
        subjects_to_process = []

        response = {'subjects': []}

        student_parser = StudentParser(sippa.content)
        response['student'] = student_parser.get_dict()

        for subject in subjects.get_all():
            code = subject.get('code')
            name = subject.get('name')
            class_identifier = subject.get('class_identifier')
            teacher_name = subject.get('teacher_name')

            subject_parser = SubjectParser(code=code, name=name,
                                           class_identifier=class_identifier, teacher_name=teacher_name)

            subject_request = requests.get(self.format_subject_url(class_identifier), cookies=cookies, verify=False)
            subject_parser.home_content = subject_request.content.decode('utf-8', 'ignore')

            subject_request = requests.get(SIPPAWrapper.FILES_URL, cookies=cookies, verify=False)
            subject_parser.files_content = subject_request.content.decode('utf-8', 'ignore')

            subject_request = requests.get(SIPPAWrapper.EXAMS_URL, cookies=cookies, verify=False)
            subject_parser.exams_content = subject_request.content.decode('utf-8', 'ignore')

            subject_request = requests.get(SIPPAWrapper.HOMEWORK_URL, cookies=cookies, verify=False)
            subject_parser.homework_content = subject_request.content.decode('utf-8', 'ignore')

            subject_request = requests.get(SIPPAWrapper.SECOND_CALL_URL, cookies=cookies, verify=False)
            subject_parser.second_call_content = subject_request.content.decode('utf-8', 'ignore')

            subject_request = requests.get(SIPPAWrapper.CALENDAR_URL, cookies=cookies, verify=False)
            subject_parser.calendar_content = subject_request.content.decode('utf-8', 'ignore')

            subjects_to_process.append(subject_parser)

        for subject in subjects_to_process:
            parsed_subject = subject.get_dict()
            response['subjects'].append(parsed_subject)

        default_storage.delete('captchas/%s.jpg' % self.__session)

        return response


class BlogWrapper(object):

    START_URL = 'http://www.quixada.ufc.br/docente/'

    def __init__(self):
        self.teachers = []

    def run(self):
        '''
        Lista os professores no seguinte formato:
        [{
            'name': 'Professor',
            'emails': ['email@email.com'],
            'avatar_url': 'http://lorempixel.com/200/200',
            'position': 'Professor Assistente',
            'url': 'http://google.com.br'
        }]
        '''

        blog_request = requests.get(BlogWrapper.START_URL)
        soup = BeautifulSoup(blog_request.content.decode('utf-8', 'ignore'), 'html.parser')

        self.teachers = []

        for div in soup.find_all('div', class_='col-md-10'):
            name = div.h2.text
            position = div.p.text
            url = div.a['href']

            teacher_request = requests.get(url)
            soup_teacher = BeautifulSoup(teacher_request.content, 'html.parser', from_encoding='utf-8')

            if soup_teacher.em is not None:
                emails = soup_teacher.em.text
            elif len(div.find_all('li')) > 0:
                emails = div.find_all('li')[1].text
            else:
                emails = ''

            emails = ' '.join([x.replace(u'\xa0', u'').strip() for x in emails.split(' ') if '@' in x])

            avatar_url = soup_teacher.find(id='conteudo').find('img', class_='wp-post-image')['src']

            self.teachers.append({
                'name': name,
                'position': position,
                'avatar_url': avatar_url,
                'emails': emails
            })

        return self.teachers
