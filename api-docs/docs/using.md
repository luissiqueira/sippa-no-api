# Utilizando a API

Exibir quais são os serviços disponíveis, falar sobre o msgpack e json, exemplificar.

## Entendendo o processo de login

Para realizar login no [SIPPA](https://sistemas.quixada.ufc.br/apps/sippa/)
é necessário informar quatro campos básicos:

- Matrícula
- Senha
- Tipo de usuário
- Valor para o captcha

O tipo de usuário nesse caso é fixo pois apenas trataremos de alunos nessa API. Caso deseje
expandir para outros tipo de usuários será necessário flexibilizar esse argumento também para as
chamadas da API.

O valor para o captcha atualmente é informado de forma manual, onde o usuário que irá realizar
o login na aplicação deverá informar qual o valor presente na imagem a ser exibida (assim como
acontece no login tradicional via site oficial).

## Iniciando um processo de login

Para iniciar o processo de login é necessário gerar um identificador de sessão juntamente com
a url do captcha a ser informado.

***Exemplo de requisição***

```http
  GET  http://sippa-no-api.us-east-1.elasticbeanstalk.com/api/start-login
```

***Exemplo de retorno***

```json
  {
    "identifier": "ABCDE12345",
    "captcha_url": "http://lorempixel.com/200/200"
  }
```

- identifier: Deve ser reenviado na solicitação de informações do usuário juntamente com o valor do captcha.
- captcha_url: Link da imagem de captcha associada ao identificador de sessão.

## Obtendo informações do aluno

Em posse do identificador de sessão e do valor do captcha a ele associado, é chegada a vez de informar os dados
do aluno (matrícula e senha) e receber as informações atuais.

***Exemplo de requisição***

```http
  POST          http://sippa-no-api.us-east-1.elasticbeanstalk.com/api/process-login
  Content-Type  application/x-www-form-urlencoded

  login="0330000"
  password="123456"
  session="ABCDE12345"
  captcha_value="q1w2"

```

***Exemplo de retorno***

```json
  {
    "student": {
      "name": "Nome do aluno",
      "registration": "0330000"
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
```

## Recebendo a resposta no formato MessagePack

Definição breve sobre o MessagePack segundo o site oficial: *"It's like JSON.
But fast and small."*

Para os serviços envolvidos no processo de obtenção de dados do usuário, é possível receber a resposta no formato
do [MessagePack](https://msgpack.org).

Para isso é preciso apenas enviar um query parameter na URL chamado *format* com o valor *msgpack*.

***Exemplo de requisição requisitando MessagePack como padrão de resposta***

```http
  GET  http://sippa-no-api.us-east-1.elasticbeanstalk.com/api/start_login?format=msgpack
```

Para entender mais, acesse o [site oficial](https://msgpack.org) do projeto.