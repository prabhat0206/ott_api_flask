import io
from .models import BackupDate
from . import upload_file_to_s3, db
from datetime import date
import sqlite3
import threading


def backup_data():
    threading.Timer(15, backup_data).start()
    last_date = BackupDate.query.filter_by(id=1).first()
    if last_date.last_date < date.today():
        conn = sqlite3.connect('python7.db')  
        with io.open(r'backupdatabase_dump.sql', 'w') as p: 
            for line in conn.iterdump():
                p.write('%s\n' % line)
        print('Backup performed successfully!')
        file = ('backupdatabase_dump.sql',open('backupdatabase_dump.sql','rb'),'application/octet-stream')
        upload_file_to_s3(file, True, f'backupdatabase_dump_{date.today()}.sql')
        conn.close()
        last_date.last_date = date.today()
        db.session.commit()
