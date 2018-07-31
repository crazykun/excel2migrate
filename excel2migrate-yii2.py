# -*- coding: utf-8 -*-
import xlrd
import os
import re
import time


php_body='''
<?php

use yii\db\Migration;

class %s extends Migration
{
    protected  $tableName="%s";
    public function safeUp()
    {
        $linkColumn=array(
			%s
		);
        $options="engine=innodb default charset=utf8  COMMENT=\'%s\'";
		$this->createTable($this->tableName,$linkColumn,$options);
        return true;
    }

    public function safeDown()
    {
        $this->dropTable($this->tableName);
        return true;
    }

}
'''

sql_demo={
    'pk': '"%s"=>"pk  COMMENT \'%s\'",',
    'int': '\t\t\t"%s"=>"%s NOT NULL DEFAULT \'0\' COMMENT \'%s\'",',
    'varchar': '\t\t\t"%s"=>"%s NOT NULL DEFAULT \'\' COMMENT \'%s\'",',
    'text': '\t\t\t"%s"=>"%s NOT NULL  COMMENT \'%s\'",',
    'datetime': '\t\t\t"%s"=>"%s NOT NULL DEFAULT  \'0000-00-00 00:00:00\' COMMENT \'%s\'",',
    'date': '\t\t\t"%s"=>"%s NOT NULL DEFAULT  \'0000-00-00\' COMMENT \'%s\'",',
}

NEWLINE = '\n'
#MIGRATE_PATH = '/data/python/excel2migrate/migrate/'
MIGRATE_PATH = os.path.abspath('.')+'/migrate'



def create_migrate(file):
    table = xlrd.open_workbook(file).sheets()[0]  # 打开xls文件的 第一张表
    nrows = table.nrows  # 获取表的行数
    column=''
    table_name=''
    table_commit = ''
    table_num=0
    
    for i in range(nrows):  # 循环逐行打印  
        #print('line ',i)
        field_name=str(table.row_values(i)[0])
        if  field_name=='' or  field_name in ['键名','PRIMARY','字段']:
            continue
        else:
            field_type=str(table.row_values(i)[1])
            if '索引' in field_name:
                #写前一个表
                if table_name and column:                
                    #time.sleep(1)
                    filename = create_filename(table_name, table_num)
                    migrate_text = php_body % (filename,table_name,column,table_commit)
                    write_php(migrate_text,filename)
                    column = ''
                    table_num+=1
                    print('create table', filename, ' success')
                print("create migrate : "+table_name)
            elif field_type=='':
                table_name=field_name
            else:                
                field_commet=table.row_values(i)[5]
                for key in sql_demo:
                    if '主键' in field_name:
                        #print("create column : "+field_name)
                        column += sql_demo['pk'] % (field_name.replace('(主键)','').strip(),'主键')
                        column += NEWLINE
                        break                        
                    else:
                        if key in field_type:
                            #print("create column : "+field_name)
                            column += sql_demo[key] % (field_name, field_type, field_commet)
                            column += NEWLINE
                            break

    return '[+] create table migrate over...'


def write_php(data,filename='test'):
    filename = MIGRATE_PATH+'/'+filename+'.php'
    try:
        with open(filename, 'w+') as f:
            f.write(data)
    except:
        print('write data to php error!')

def create_filename(tablename='tablename',sleep=0):
    time_stamp = time.localtime(time.time()+sleep)
    date=time.strftime("%Y%m%d_%H%M%S", time_stamp)[2:]
    return 'm%s_create_table_%s' % (date,tablename)  


def del_old_migrate_file(path=MIGRATE_PATH):
    for i in os.listdir(path):
        path_file = os.path.join(path, i) 
        os.remove(path_file)
 
 
def main():
    file = input("Enter your file path: ")
    if(os.path.exists(MIGRATE_PATH)):        
        del_old_migrate_file()
    else:
        os.makedirs(MIGRATE_PATH) 
    re=create_migrate(file)
    print(re)


if __name__ == '__main__':
    main()
