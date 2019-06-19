import sys


def execute_mysql_code(sql_lines, config, return_result=False):
    # Local import as pymysql may not be available on systems configured for sql server
    import pymysql.cursors
    connection = pymysql.connect(host=config['host'],
                                 user=config['user'],
                                 port=config['port'],
                                 password=config['password'],
                                 db=config['database'])

    result = None
    with connection.cursor() as cursor:
        for line in sql_lines:
            cursor.execute(line)
            result = cursor.fetchall()
    connection.commit()
    return result


def execute_mssql_code(sql_lines, config, return_result=False):
    # Local import as pyodbc may not be available on systems configured for MySQL
    import pyodbc
    # Note that ODBC Driver 17 is the correct driver version for Ubuntu 18.04.
    # When running tests from Windows just need to be: DRIVER={{SQL Server}}
    if sys.platform == 'linux' or sys.platform == 'darwin':
        driver = 'ODBC Driver 17 for SQL Server'
    else:
        driver = 'SQL Server'
    connection_string = 'DRIVER={{{}}};SERVER={};DATABASE={};UID={};PWD={}'
    connection = pyodbc.connect(connection_string.format(
                                     driver,
                                     config['host'],
                                     config['database'],
                                     config['user'],
                                     config['password']))
    connection.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
    connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    connection.setencoding(encoding='utf-8')

    result = None
    with connection.cursor() as cursor:
        for line in sql_lines:
            result = cursor.execute(line)
            if return_result:
                result = cursor.fetchall()
    connection.commit()
    return result
