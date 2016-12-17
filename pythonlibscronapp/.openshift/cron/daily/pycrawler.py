#encoding=utf-8
from bs4 import BeautifulSoup
from bs4 import NavigableString
from urllib.request import urlopen, Request
import json
import os
import subprocess
import logging

#######################################################################
#Analogue of JS functions for decoding urls in pythonlibs
def dl(ml, mi):
    mi=mi.replace('&lt;','<')
    mi=mi.replace('&#62;','>')
    mi=mi.replace('&#38;','&')
    return dl1(ml, mi)

def dl1(ml, mi):
    ot="";
    for j in range(len(mi)):
      ot += chr(ml[ord(mi[j])-48])
    return ot
#########################################################################
#Configure loggers
logging_dir = os.environ['OPENSHIFT_LOG_DIR']
logger = logging.getLogger()
logging_handler = logging.FileHandler(
    os.path.join(logging_dir, 'commit_error.log'),
    'a',
    encoding='utf-8',
    delay='true')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging_handler.setFormatter(formatter)
logger.addHandler(logging_handler)
#########################################################################
#Crawl links and other package metadata

url = "http://www.lfd.uci.edu/~gohlke/pythonlibs/"
req = Request(
        url=url,
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:47.0) Gecko/20100101 Firefox/47.0'})

soup = BeautifulSoup(urlopen(req).read(),"lxml")
pythonlibs = soup.ul

modules_dict = {}

for packages in pythonlibs.contents[3:]:

    try:
        p_id = packages.contents[0]['id']
        package_descrp = ''
        home_page = ''
        plib_midurl = ''

        try:

            result = []
            for descendant in packages.descendants:
                if isinstance(descendant, NavigableString):
                    result.append(descendant.encode('latin1').decode('utf-8','ignore').strip())
                elif descendant.name=='ul':
                    break

            package_descrp = ' '.join(result)

            p_info_tag = packages.contents[1]
            home_page = p_info_tag.a['href']

        except TypeError as e:

            if p_id == 'misc':
                package_descrp = 'Unavailable'
                home_page = 'Unavailable'
            else:
                continue

        for x in packages.ul.contents:

            try:

                size_data = x.a['title'].split('[')[1].split(']')[0]
                package_size = ' '.join(size_data.split())
                package_date = x.a['title'].split('[')[2].split(']')[0]
                name_data = x.text
                file_name = name_data.split("-")

                jscript_url = x.a['onclick']
                ml = list(map(int,jscript_url.split('[')[1].split(']')[0].split(',')))
                mi = jscript_url.split('\"')[1].split('\"')[0]
                plib_midurl = dl(ml, mi).split('/')[0] + '/'

                if file_name[0] in modules_dict:
                    modules_dict[file_name[0]].append(
                        dict(
                            version=file_name[1],
                            compatibility_tag='-'.join(file_name[2:-1]),
                            architecture=file_name[-1][:-4],
                            package_size=package_size,
                            url=url+plib_midurl+name_data,
                            summary=package_descrp,
                            home_page=home_page,
                            last_updated=package_date,
                        ))
                else:
                    modules_dict[file_name[0]]=[dict(
                            version=file_name[1],
                            compatibility_tag='-'.join(file_name[2:-1]),
                            architecture=file_name[-1][:-4],
                            package_size=package_size,
                            url=url+plib_midurl+name_data,
                            summary=package_descrp,
                            home_page=home_page,
                            last_updated=package_date,
                        )]

            except AttributeError as e:
                pass
            except KeyError as e:
                pass
            except Exception as e:
                logger.exception('Unexpected Exception')
                raise

    except AttributeError:
        pass
    except Exception as e:
        logger.exception('Unexpected Exception')
        raise

with open(os.path.join(os.environ['OPENSHIFT_DATA_DIR'],'pythonlibs_modules/pythonlibs.json'),'w') as xt:
    xt.write(json.dumps(modules_dict, indent=2))


##########################################################
#Commit the generated file in github
##########################################################
try:
    working_dir = '/var/lib/openshift/57b884ee89f5cf7d2e0000dd/app-root/data/pythonlibs_modules/'
    cli_command = subprocess.Popen(
        ['git add --all && git commit -m Auto_Commit && git push'],
        cwd=working_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True)
    out, err = cli_command.communicate()
    #print (out)
    logger.info(out)
    if err!=None:
        logger.error(err)

except Exception as e:
    logger.exception('Unexpected Exception')
    raise
############################################################


