#!/usr/bin/env python
import os
import socket
import pymysql
from flask import Flask
from flask import render_template
app = Flask(__name__)

sqlConn = None 
sqlCur = None

def getDatabaseInfo():
    sqlserver = os.environ.get('SQLSERVER', None)
    if sqlserver:
        print "Found SQL Server: ", sqlserver

    sqluser = os.environ.get('SQLUSER', None)
    if sqluser:
        print "Found SQL User: ", sqluser

    sqlpasswd = os.environ.get('SQLPASSWD', None)
    if sqlpasswd:
        print "Found SQL Password: ", sqlpasswd

    sqldb = os.environ.get('SQLDB', None)
    if sqlpasswd:
        print "Found SQL Database: ", sqldb

    return (sqlserver, sqluser, sqlpasswd, sqldb)

def serverName():
    return socket.gethostname()

@app.route('/')
@app.route('/index')
def index():
    server = serverName()
    title = 'Duplo'    
    return render_template('index.html', title=title, server=server)

def getInventory():
    productList = []

    if not sqlCur :
       return productList

    num = sqlCur.execute('SELECT * FROM products;')

    for row in sqlCur:
        product = {}
        product['id'] = row[0]
        product['Name'] = row[1], 
        product['Description'] = row[2]
        product['Quantity'] = row[3]
        product['Price'] = row[4]
        productList.append(product)

    print productList
    return productList

@app.route('/inventory')
def inventory():
    productList = getInventory()
    server = serverName()
    return render_template ('inventory.html', products=productList, server=server)

if __name__ == '__main__':
    (host, user, passwd, db) = getDatabaseInfo()
    print "Connecting to:", host, user, passwd, db
    sqlConn = pymysql.connect(host=host, user=user, password=passwd, db=db)
    sqlCur = sqlConn.cursor()
    app.run(host='0.0.0.0', port=8080)
