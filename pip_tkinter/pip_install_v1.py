from io import StringIO
from pip import main
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import subprocess
import sys

sysout = StringIO()
syserr = StringIO()

class redirect:
    """Context manager for temporarily redirecting stdout/err.

    Simplified and generalize from contextlib.redirect_stdout.
    """

    def __init__(self, stdfile, new_target):
        self._stdfile = stdfile  # 'stdout' or 'stderr'
        self._new_target = new_target

    def __enter__(self):
        self._old = getattr(sys, self._stdfile)
        setattr(sys, self._stdfile, self._new_target)
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stdfile, self._old)

# For GUI version, redirects would be here, done once.
# Put in runpip for prototype testing in text mode, so can print.

def runpip_using_subprocess(argstring):
    '''Run pip with argument string containing command and options.
    Argstring is quoted version of what would follow 'pip' on command line.
    '''
    with redirect('stdout', sysout) as f1, redirect('stderr', syserr) as f2:
        status = subprocess.Popen(
                    ["pip"]+argstring.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        out, err = status.communicate()

    sysout.seek(0); sysout.truncate(0)
    syserr.seek(0); syserr.truncate(0)
    return out.decode('utf-8'), err.decode('utf-8')


class Multi_items_list(object):

    def __init__(self, parent, headers_list, items_list):
        self.scroll_tree = None
        self.parent = parent
        self.headers_list = headers_list
        self.items_list = items_list
        self.initialize()
        self.populate_rows()

    def initialize(self):

        self.myframe = ttk.Frame(self.parent)
        self.myframe.pack(fill='both', expand=True)

        self.scroll_tree = ttk.Treeview(self.parent, columns=self.headers_list, show='headings')
        vrtl_scrbar = ttk.Scrollbar(
                        orient="vertical",
                        command=self.scroll_tree.yview)
        hrtl_scrbar = ttk.Scrollbar(
                        orient="horizontal",
                        command=self.scroll_tree.xview)
        self.scroll_tree.configure(
            yscrollcommand=vrtl_scrbar.set,
            xscrollcommand=hrtl_scrbar.set)
        self.scroll_tree.grid(column=0, row=0, sticky='nswe', in_=self.myframe)
        vrtl_scrbar.grid(column=1, row=0, sticky='ns', in_=self.myframe)
        hrtl_scrbar.grid(column=0, row=1, sticky='ew', in_=self.myframe)
        self.myframe.grid_columnconfigure(0, weight=1)
        self.myframe.grid_rowconfigure(0, weight=1)

    def populate_rows(self):
        for header in self.headers_list:
            self.scroll_tree.heading(header, text=header)
            self.scroll_tree.column(header, width=30)

        for item in self.items_list:
            self.scroll_tree.insert('', 'end', values=item)


class Pip_gui(Frame):

    def __init__(self, parent):
        """
        Set the parent of the current frame
        """

        Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()
        self.load_settings()
        self.parent.protocol('WM_DELETE_WINDOW', self.onExit)

    def initialize(self):
        """
        Set the contents of the GUI for pip package manager
        """
        self.parent.title('PIP package manager')
        self.adjustWindow()
        self.nb = ttk.Notebook(self.parent)
        self.installed_tab = ttk.Frame(self.nb)
        self.search_tab = ttk.Frame(self.nb)
        self.settings_tab = ttk.Frame(self.nb)
        self.update_installed_tab()
        self.nb.add(self.installed_tab, text='Installed Packages')
        self.nb.add(self.search_tab, text='Install Packages')
        self.nb.add(self.settings_tab, text='Settings')
        self.nb.pack(expand=1, fill='both')

    def _get_data(self, func_option):
        """
        A separate function for extracting data from the runpip() function.
        It is done in order to get this function tested using unittest module

        According to func_option, it returns the data extracted :

        Options:
        -------
        1. list : for listing all currently installed packages
        2. show <package name> : show details of installed packages
        3. search <keyword> : show formated search results
        4. install <package name> : get results while installing packages
        """

        splitted_options = func_option.split()

        if splitted_options[0] == 'list':
            return runpip(func_option)

        elif splitted_options[0] == 'show':
            out, err = runpip(func_option)
            print ("Output :\n" + str(out))
            print ("Error :\n" + str(err))
            return out, err

        elif splitted_options[0] == 'search':
            return runpip(func_option)

        elif splitted_options[0] == 'install':
            return runpip(func_option)

    def get_data_list(self):
        """
        Get the result from the pip list command.
        Split it into lines.
        Split each line in two parts : package and version
        Append the third field as the latest package version available
        """
        out, err = runpip('list')
        #print (out)
        installed_pkg_list = out.splitlines()
        for i in range(len(installed_pkg_list)):
            pkg_name, pkg_version = installed_pkg_list[i].split('(')
            pkg_version = pkg_version[:len(pkg_version)-1]
            latest_version = '  '
            installed_pkg_list[i] = (pkg_name, pkg_version, latest_version)
        print (installed_pkg_list)
        return installed_pkg_list

    def get_data_search(self, func_option):
        return runpip('search ' + func_option)

    def get_data_install(self, func_option):
        return runpip('install ' + func_option)

    def get_data_show(self, func_option):
        return runpip('show ' + func_option)

    def update_installed_tab(self):
        """
        Update the installed tab by getting the list of installed
        packages
        """
        #Get list of all installed PyPI packages
        self.all_instt_packages = self.get_data_list()
        self.headers_list = ['Package','Version','Latest']
        print (self.headers_list)
        self.tree_list = Multi_items_list(
                            self.installed_tab,
                            self.headers_list,
                            self.all_instt_packages)
        self.tree_list.scroll_tree.bind("<Double-Button-1>",self.show_details)
        self.instt_package_details=StringVar()
        self.instt_package_details.set(' ')
        self.package_subwindow = Label(
            self.tree_list.myframe,
            textvariable=self.instt_package_details,
            width=60)
        self.package_subwindow.grid(row=0, column=2, sticky=N+S+W+E)
        self.instt_package_details.set(' ')

    def show_details(self, event=None):
        """
        Show further details of the selected package
        """

        try:
            curr_item = self.tree_list.scroll_tree.focus()
            item_dict = self.tree_list.scroll_tree.item(curr_item)
            selected_name = item_dict['values'][0] + ' \('
            selected_name = selected_name + item_dict['values'][1] + '\)'
            #print (selected_name)
            out, err = self.get_data_show(selected_name)
            #print (out)
            self.instt_package_details.set(out)
            self.package_subwindow.config(
                textvariable=self.instt_package_details)
        except:
            self.instt_package_details.set('No package selected')
            self.package_subwindow.config(
                textvariable=self.instt_package_details)

    def adjustWindow(self):
        """
        Set the window at center position of the screen
        """

        #Get the screen width and screen height
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        #Calculate the appropriate window width and height
        window_width = int(0.75*screen_width);
        window_height = int(0.75*screen_height);

        #Determine the position of the window
        x = (screen_width - window_width)//2
        y = (screen_height - window_height)//2

        self.parent.geometry(
            str(window_width)+'x'+str(window_height)+'+'+str(x)+'+'+str(y))

    def onExit(self):
        """
        Manage the close event of the window
        """

        result = messagebox.askyesno(
                    'Quit', 'Do you want to quit?', icon='question')
        if result:
            self.parent.destroy()

# example usage

if __name__=='__main__':

    root = Tk()
    root.resizable(width=FALSE, height=FALSE)
    pip_window = Pip_gui(root)
    root.mainloop()
