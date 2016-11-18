#!/usr/bin/env python
import os
import socket
import pymysql
import logging
import subprocess
from flask import Flask
from flask import render_template
app = Flask(__name__)

frontendHost = '0.0.0.0'
frontendPort = 8080
db = None

class Database(object):

    def __init__(self, server=None, user=None, password=None, db=None):
       '''
          usage: SQLDatabase(server, user, password, db)

          server - IP address or fully qualified domain name of MySQL server
          user - SQL Server user
          password - SQL Server password
          db - SQL Database name 

          parameters are optional. If parameters aren't speficied they are 
          initialized from environment variable 

          Environment variable mapping
          server = SQLSERVER          
          user = SQLUSER          
          password = SQLPASSWD          
          db = SQLDB
       '''
       if not server:
          self.server = os.environ.get('SQLSERVER', None)
       else: 
          self.server = server

       if not self.server:
          logging.error("SQL Server not found")
       else:
          logging.info("SQL Server:%s", self.server)

       if not user:
          self.user = os.environ.get('SQLUSER', None)
       else: 
          self.user = user

       if not self.user:
           logging.error("SQL User not found")
       else:
           logging.info("SQL User:%s", self.user)


       if not password: 
          self.password = os.environ.get('SQLPASSWD', None)
       else: 
          self.password = password

       if not self.password:
          logging.error("SQL Password not found")
       else:
          logging.info("SQL Password:%s ", self.password)

       if not db:
          self.db = os.environ.get('SQLDB', None)
       else: 
          self.db = None
       
       if not self.db:
          logging.error("SQL db not found")
       else:
          logging.info("SQL Database:%s ", self.db)

       self.frontendServer = socket.gethostname()
       logging.info("Database initialized on %s", self.frontendServer)
       return 

    def getServer(self):
        return self.frontendServer

    def connect(self):
        self.sqlConn = pymysql.connect(host=self.server, 
                                  user=self.user, 
                                  password=self.password, 
                                  db=self.db)
        self.sqlCur = self.sqlConn.cursor()
        return

    def close(self):
        self.sqlConn.close()
         
    def getProductList(self):
        productList = []

        self.connect()

        if not self.sqlCur :
           logging.error("Get Product list Failed due to connect to db failure")
           return productList

        num = self.sqlCur.execute('SELECT * FROM products;')
        for row in self.sqlCur:
            product = {}
            product['id'] = row[0]
            product['Name'] = row[1], 
            product['Description'] = row[2]
            product['Quantity'] = row[3]
            product['Price'] = row[4]
            productList.append(product)

        logging.info("getProducts: Found %d products in product table", num)

        self.close()
        return productList

    def getServerList(self):
        serverList = []
        self.connect()

        if not self.sqlCur :
           logging.error("Get Server list Failed due to connect to db failure")
           return serverList

        num = self.sqlCur.execute('SELECT * FROM servers;')

        for row in self.sqlCur:
            server = {}
            server['id'] = row[0]
            server['Name'] = row[1], 
            server['Uptime'] = row[2]
            serverList.append(server)

        logging.info("getServer: Found %d server in server table", num)
        self.close()
        return serverList

    def initProductsTable(self):
        table = '''
          CREATE TABLE IF NOT EXISTS products (
             productID    INT UNSIGNED  NOT NULL AUTO_INCREMENT,
             productCode  CHAR(3)       NOT NULL DEFAULT '',
             name         VARCHAR(30)   NOT NULL DEFAULT '',
             quantity     INT UNSIGNED  NOT NULL DEFAULT 0,
             price        DECIMAL(7,2)  NOT NULL DEFAULT 99999.99,
             PRIMARY KEY  (productID)
          );
        '''
        self.connect()
        if not self.sqlCur :
           logging.error("Init Product table failed due to connect to db error")
           return 

        self.sqlCur.execute(table)
        self.sqlConn.commit()
        row = "INSERT INTO products VALUES  (NULL, 'SER', '{0}', 1, 2000);".format(self.frontendServer)
        logging.info(row)
        self.sqlCur.execute(row)
        self.sqlConn.commit()
        self.close()

        logging.info("Added: %s", row)
        return 

    def initServersTable(self):
        table = '''
        CREATE TABLE IF NOT EXISTS servers (
            ServerID     INT UNSIGNED  NOT NULL AUTO_INCREMENT,
            Name         VARCHAR(30)   NOT NULL DEFAULT '',
            Uptime       VARCHAR(80)   NOT NULL DEFAULT '',
            PRIMARY KEY  (ServerID)
        );
        '''
        self.connect()
        if not self.sqlCur :
           logging.error("Init server table failed due to connect to db error")
           return 

        self.sqlCur.execute(table)
        self.sqlConn.commit()
        uptime = subprocess.check_output('uptime') 
        uptime = uptime.split(',')[0]
        row = "INSERT INTO servers VALUES  (NULL, '{0}', '{1}');".format(self.frontendServer, uptime)
        logging.info("Inserting %s", row)
        self.sqlCur.execute(row)
    	self.sqlConn.commit()
        self.close()
        return 

@app.route('/boot')
def boot():
    db.initProductsTable()
    db.initServersTable()
    return ''

@app.route('/products')
def inventory():
    productList = db.getProductList()
    frontendServer = db.getServer()
    return render_template ('products.html', products=productList, 
                             server=frontendServer)
 
@app.route('/servers')
def server():
    serverList = db.getServerList()
    frontendServer = db.getServer()
    return render_template ('servers.html', servers=serverList, 
                            frontend=frontendServer)

@app.route('/')
@app.route('/index')
def index():
    server = db.getServer()
    title = 'DuploDemo'    
    return render_template('index.html', title=title, server=server)

def initLogging():
    logging.basicConfig(filename='/tmp/duplodemo.log', 
                        filemode='w', 
                        level=logging.DEBUG)
    return

if __name__ == '__main__':
    initLogging()

    db = Database()

    logging.info("Starting Flask Application on  %s:%s", 
                  frontendHost, frontendPort)
    try: 
       app.run(host=frontendHost, port=frontendPort)
    except :  
       logging.error("Failed to start the app on %s:%s",
                     frontendHost, frontendPort)

