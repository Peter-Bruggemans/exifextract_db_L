# dit programma maakt gebruik van libimage-exiftool-perl/8.60-2
# laad de libraries
import os
from subprocess import check_output
import psycopg2
import sqlite3

# variabelen voor de broninstructieregel
bronregel = """ls -R /home/peter/Fotos | awk '/:$/&&f{s=$0;f=0}/:$/&&!f{sub(/:$/,"");s=$0;f=1;next}NF&&f{ print s"/"$0 }'"""
bronpad = '/home/peter/Fotos/'
bronbestand = 'CR2'

# variabelen voor de doelinstructieregel
doelinstructie = "exiftool -T -canon"

# variabelen voor de postgreql database
#v_dbname='exif' 
#v_user='exif_wr' 
#v_host='raspberrypi.lan' 
#v_password='exif_wr'

# variabelen voor de postgreql database
v_dbname='python' 
v_user='adminj3ikigb'
v_host='localhost'
v_password='4yWHbxthcIEL'


# variabelen voor de sqlite database
v_dbdrive = '/'
v_dbpad = 'home/peter/Documenten/exiftool/'
v_dbfile = 'exif.sqlite'

# variabelen voor de sql instructie
actie1 = '''
insert into stg_exif
(
"File Name",
"Camera Model Name",
"Date/Time Original",
"Shooting Mode",
"Shutter Speed",
"Aperture",
"Metering Mode",
"Exposure Compensation",
"ISO",
"Lens",
"Focal Length",
"Image Size",
"Quality",
"Flash",
"Flash Type",
"Flash Exposure Compensation",
"Red Eye Reduction",
"Shutter Curtain Sync",
"White Balance",
"Focus Mode",
"Contrast",
"Sharpness",
"Saturation",
"Color Tone",
"Color Space",
"Long Exposure Noise Reduction",
"File Size",
"File Number",
"Drive Mode",
"Owner Name",
"Serial Number"
)
values
(\n'''

actie3 = '''\n);'''

# maak verbinding met de database
try:
    print "connecting database"
    # voor postgresql
    connectstring = "dbname='" + v_dbname + "' user='" + v_user + "' host='" + v_host + "' password='" + v_password + "'"
    conn = psycopg2.connect(connectstring)
    # voor sqlite
    dblocatie = v_dbdrive + v_dbpad + v_dbfile
    osdblocatie = (os.path.normpath(dblocatie))
    #conn = sqlite3.connect(osdblocatie)
    
    # maak de cursor naar de database aan
    cur = conn.cursor()

    # voer de broninstructie uit
    result=check_output(bronregel, shell=True)
    # verdeel het resultaat in regels
    lines = result.split('\n')
    # filter op bronpad en bronbestand en maak de doelinstructieregel aan per broninstructieregel
    teller = 0
    for line in lines:
        if len(line) > 0:
            if line[-3:] == bronbestand:
                if line[0:len(bronpad)] == bronpad:
                    # bouw de doelinstructieregel
                    doelregel = doelinstructie + ' ' + line
                    # pas de broninstructieregel aan aan het os(/ wordt \)
                    osdoelregel = (os.path.normpath(doelregel))

                    # controle
                    #print (doelregel)
                    #print (osdoelregel)

                    # voer de doelinstructieregel uit
                    result2 = check_output(osdoelregel, shell=True)
                    # zet het resultaat van de doelinstructie om in een sql-instructie
                    fields = result2.split("\t")
                    fields2 = [word.replace('\r\n','') for word in fields]
                    sql = actie1 + ',\n'.join(map("'{0}'".format, fields2)) + actie3
                    teller = teller + 1
                    print str(teller) + " row(s) inserted"
                    cur.execute(sql)
                    # voor postgresql
                    cur.execute('commit;')
                    # voor sqlite
                    #cur.execute(';')


    # verbreek verbinding met de database
    cur.close()
    print "database connection closed"

except:
    print "an error ocurred"
