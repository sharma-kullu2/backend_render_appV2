import psycopg2
import os


DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE = os.getenv('DATABASE')
USER = os.getenv('DBUSER')
PASSWORD=os.getenv('DBKEY')



class DB():
    
    def __init__(self):
        pass
    
    def connect(self):
        try:
            #conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            self.conn = psycopg2.connect(dbname=DATABASE, user=USER,password=PASSWORD, host=DATABASE_URL)
            #
            self.conn.autocommit = True
            db_version=self.query('''
            select version();
            ''')
            if db_version is not None:
                print("DB ",db_version)
            #print (self.query('SELECT * from stockmaster;'))
            return 1
        except (Exception, psycopg2.DatabaseError) as error:
            print("DB CONNECT EXCEPTION ",error)
            return 0

    def getconnhandle(self):
        return self.conn
    

    def query(self,sql):
        try:
            UniqueViolation = psycopg2.errors.lookup('23505')
            self.conn=self.getconnhandle()
            cur = self.conn.cursor()
            try:
                cur.execute(sql)
                res=cur.fetchall()
                cur.close()
                return res
            except UniqueViolation as err:
                print (err)
            cur.close()
            return None
        except (Exception, psycopg2.DatabaseError) as error:
            print("EXCEPTION_QUERY ",error)
            return None
    
    
    def query_only(self,sql):
        try:
            self.conn=self.getconnhandle()
            cur = self.conn.cursor()
            cur.execute(sql)
            cur.close()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print("EXCEPTION_QUERY ",error)
            return False
            


    def con_close(self):
        self.conn=self.getconnhandle()
        if self.conn is not None:
            self.conn.close()
            print('Database connection closed.')
        else:
            print ('Database connection not closed.')

    def add_to_postmaster(self,path,title,posttype,author='MedicalGeek'):
        #sql 
        sql='''
        insert into postmaster(date, title, author)
        values(CURRENT_DATE,'{title}','{author}')
        returning DID;
        '''.format(title=title,author=author)
        print("add_to_postmaster--> ",sql)
        res=self.query(sql)
        if res is not None:
            did=res[0][0]
            sql='''insert into folders (did,folder) 
            values('{ID}','{folder}');
            '''.format(ID=did,folder=path)
            print("add_to_folders--> ",sql)
            if self.query_only(sql):
                sql='''insert into posttypes (did,type) 
                values('{ID}','{posttype}');
                '''.format(ID=did,posttype=posttype)
                print("add_to_postypes--> ",sql)
                return self.query_only(sql)                
        return False


