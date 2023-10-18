# from os import environ

environ['CW_SERVICES'] = ',postgres:postgres,'

compose.add_compose_file('config/compose.yaml')
