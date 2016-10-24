# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

import re

from core.models import Teacher


class StudentParser(object):

    def __init__(self, content):
        self.__content = content

    def get_name(self):
        return None

    def get_registration(self):
        return None

    def get_dict(self):
        return {'name': self.get_name(), 'registration': self.get_registration()}


class SubjectParser(object):

    def __init__(self, code, name, class_identifier, teacher_name):
        self.__class_identifier = class_identifier
        self.__code = code
        self.__name = name
        self.__teacher_name = teacher_name
        self.home_content = None
        self.files_content = None
        self.exams_content = None
        self.homework_content = None
        self.second_call_content = None
        self.calendar_content = None
        self.default_avatar_url = 'http://lorempixel.com.br/200/200'

    def find_teacher_avatar(self, name, email):
        teacher = Teacher.find_by_name_or_email(name=name, email=email)
        return teacher.avatar_url.encode('utf-8') if teacher is not None else self.default_avatar_url

    def get_notices(self):
        soup = BeautifulSoup(self.home_content, 'html.parser', from_encoding='utf-8')
        notices = []

        for idx, notice in enumerate(soup.find_all(class_='tabela-coluna0')):
            date_re = re.search('\d+\/\d+\/\d+', notice.text)
            date = date_re.group(0) if date_re is not None else ''
            text = re.sub(' +', ' ', notice.td.text.replace('\n', ''))
            notices.append({'order': idx + 1, 'date': date, 'text': text})

        return notices

    def get_lesson_plans(self):
        soup = BeautifulSoup(self.home_content, 'html.parser', from_encoding='utf-8')
        tbody = soup.find(class_='tabela_ver_freq').tbody

        lessons = []

        for info in tbody.find_all('tr'):
            infos = info.find_all('td')
            lesson = infos[0].text
            planned_description = infos[1].text.split('\n')[1].strip()
            description = infos[2].text.split('\n')[1].strip()
            date = infos[2].text.split('\n')[0].strip()
            presence_hours = infos[3].text

            lessons.append({
                'lesson': int(lesson),
                'date': date.encode('utf-8'),
                'planned_description': planned_description.encode('utf-8'),
                'description': description.encode('utf-8'),
                'presence_hours': int(presence_hours) if len(presence_hours) > 0 else 0
            })

        return lessons

    def get_frequency(self):
        soup = BeautifulSoup(self.home_content, 'html.parser', from_encoding='utf-8')
        el = soup.h3

        text = el.text.strip()
        els = text.split(';')

        presence_re = re.search('\d+', els[1])
        absence_re = re.search('\d+', els[2])
        max_hours = len(soup.tbody.find_all('tr')) * 2

        return {
            'text': text.encode('utf-8'),
            'presence_hours': int(presence_re.group(0)) if presence_re is not None else None,
            'absence_hours': int(absence_re.group(0)) if absence_re is not None else None,
            'max_hours': max_hours
        }

    def get_exams(self):
        soup = BeautifulSoup(self.exams_content, 'html.parser', from_encoding='utf-8')
        exams = []

        for idx, exam in enumerate(soup.thead.find_all('th')):
            text = exam.text
            if '(x ' in text:
                weight_re = re.search('\d+\.\d+', text)
                exams.append({
                    'order': idx,
                    'short_description': text.split('(')[0].encode('utf-8'),
                    'weight': weight_re.group(0) if weight_re is not None else 1
                })

        for idx, value in enumerate(soup.tbody.find_all('td')):
            if idx == 0 or len(exams) < idx:
                continue

            exams[idx - 1]['value'] = value.text.encode('utf-8') if len(value.text) > 0 else None

        for idx, description in enumerate(soup.form.find_all_next('p')[1::2]):
            exams[idx]['description'] = description.text.encode('utf-8')

        return exams

    def get_code(self):
        return self.__code

    def get_class_identifier(self):
        return self.__class_identifier

    def get_name(self):
        return self.__name

    def get_average(self):
        soup = BeautifulSoup(self.exams_content, 'html.parser', from_encoding='utf-8')
        values = soup.tbody.find_all('td')

        return values[::-1][0].text.encode('utf-8')

    def get_teacher(self):
        soup = BeautifulSoup(self.home_content, 'html.parser', from_encoding='utf-8')

        name = self.__teacher_name
        email = soup.h2.text.split('-')[1].strip()

        return {
            'name': name,
            'email': email.encode('utf-8'),
            'avatar_url': self.find_teacher_avatar(name=name, email=email)
        }

    def get_files(self):
        return []

    def get_second_call_options(self):
        return []

    def get_second_call_history(self):
        return []

    def get_calendar(self):
        return []

    def get_homework(self):
        return []

    def get_dict(self):
        return {
            'code': self.get_code(),
            'class_identifier': self.get_class_identifier(),
            'name': self.get_name(),
            'average': self.get_average(),
            'teacher': self.get_teacher(),
            'notices': self.get_notices(),
            'lesson_plans': self.get_lesson_plans(),
            'frequency': self.get_frequency(),
            'exams': self.get_exams(),
            'files': self.get_files(),
            'second_call_options': self.get_second_call_options(),
            'second_call_history': self.get_second_call_history(),
            'calendar': self.get_calendar(),
            'homework': self.get_homework()
        }


class ListSubjectsParser(object):

    def __init__(self, content):
        self.__content = content

    def get_all(self):
        '''
        Lista as disciplinas no seguinte formato.
        {
            "code": "qxd0000",
            "class_identifier": "123456",
            "name": "Disciplina 1",
            "teacher_name": "Professor"
        }
        '''
        soup = BeautifulSoup(self.__content, 'html.parser', from_encoding='utf-8')

        tbody = soup.find(class_='tabela_ver_freq').tbody

        subjects = []

        for info in tbody.find_all('tr'):
            infos = info.find_all('td')
            code = infos[0].a.text
            name = infos[1].a.text
            teacher_name = infos[2].a.text

            class_identifier = infos[0].a["href"].split("id=")[1]

            subjects.append({
                'code': code,
                'class_identifier': class_identifier,
                'name': name.encode('utf-8'),
                'teacher_name': teacher_name.encode('utf-8')
            })

        return subjects
