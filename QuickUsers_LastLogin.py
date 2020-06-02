import logging

# create logger with 'QuickUsers_LastLogin' application
logger = logging.getLogger('QuickUsers_LastLogin')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('QuickUsers_LastLogin.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

# logger.info('Starting script execution')

try:
    import pandas as pd
    # import csv
    import pymssql
    from tabulate import tabulate
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib
    from configparser import RawConfigParser
    import os

    config = RawConfigParser()
    if os.path.exists('.//config.ini'):
        config.read('.//config.ini')
    else:
        raise Exception('Config file not exist')

    query = config.get('SqlConn', 'query')
    #logger.info('Read from config the following query: {0}'.format(query))

    with pymssql.connect(server=config.get('SqlConn', 'server'), port=config.get('SqlConn', 'port'),
                         user=config.get('SqlConn', 'user'), password=config.get('SqlConn', 'password'),
                         database=config.get('SqlConn', 'database'), charset='cp1251') as sql_conn:
        with sql_conn.cursor() as cursos:
            # query = query
            results = pd.read_sql_query(query, sql_conn)
            # results.to_csv(r".\\LoginCounts.csv", index=False)

    # print(results)

    html = """
    <html>
    <head>
    <style> 
     table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
      th, td {{ padding: 5px; }}
    </style>
    </head>
    <body><p>Hello,</p>
    <p>Here is the list of QUIK users who haven't been logging in 60 days (users with lastLogin = 'NaT ' haven't logged in at all):</p>
    {table}
    <p>Regards,</p>
    <p>IT Support QUIK</p>
    </body></html>
    """

    col_list = list(results.columns.values)
    data = results
    # above line took every col inside csv as list
    html = html.format(table=tabulate(data, headers=col_list, tablefmt="html", showindex=False))

    me = config.get('EmailCfg', 'me')
    server = config.get('EmailCfg', 'server')
    you = config.get('EmailCfg', 'you')

    message = MIMEMultipart(
        "alternative", None, [MIMEText(html, 'html')])

    message['Subject'] = config.get('EmailCfg', 'Subject')
    message['From'] = me
    message['To'] = you
    message['Cc'] = config.get('EmailCfg', 'Cc')
    server = smtplib.SMTP(server)
    server.sendmail(me, you, message.as_string())
    server.quit()
except Exception as err:
    logger.error('Failed to execute script: {0}'.format(err))
