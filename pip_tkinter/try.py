import pip
from pip import main
#from pip import SearchCommand
from pip import parseopts
from pip.commands.search import SearchCommand
from pip.commands.show import ShowCommand, search_packages_info
import pdb
pdb.run("pip.main(['show','wheel'])")

package='wheel'
cmd_name, cmd_args = parseopts(['show','--log','hello.txt',package])
print("Command name : {}".format(cmd_name))
print(cmd_args)
pdb.run("hh = search_packages_info(cmd_args)")
for x in hh:
    print (x)
