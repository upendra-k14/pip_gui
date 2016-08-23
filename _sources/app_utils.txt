GUI extensions of pip
=====================

These are some most frequently and important parts of code used throught the
application other than tkinter based page layouts. For more reference, please
check the :ref:`pip_tkinter`.

pip_tkinter.utils.runpip_using_subprocess
-----------------------------------------

A utility method to run `pip` console commands and return output. This method
uses subprocess module to run a console command and when the process execution
terminates, it returns the console output and errors.::

    def runpip_using_subprocess(argstring):
        """
        Run pip with argument string containing command and options. Uses
        subprocess module for executing pip commands. Returns output and error
        once execution of process terminates

        :param argstring: is quoted version of what would follow 'pip' on command \
        line.
        """

        #Explicitly specify encoding of environment for subprocess in order to
        #avoid errors
        my_env = os.environ
        my_env['PYTHONIOENCODING'] = 'utf-8'

        pip_process = subprocess.Popen(
            argstring.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env = my_env,
        )

        #Get stdout and stderr from shell
        pip_output, pip_error = pip_process.communicate()

        #Decode stdout and stderr strings to utf-8
        return (pip_output.decode('utf-8'), pip_error.decode('utf-8'))

pip_tkinter.utils.RunpipSubprocess
----------------------------------

A utility class to run `pip` commands and return *real-time* output. Since,
tkinter is not thread safe, in order to get real time output from a process
either multithreading or multiprocessing ( basically asynchronous I/O) is
needed. In both cases, output of process can be sent through a shared queue
which may be shared between multiple threads or multiple processes. However,
for this application multiprocessing turns out be a better option than
multithreading, due to following reasons :

1.  Python `multithreading` module doesn't take advantage of multiple CPU cores
    available which can degrade user expereince in case of GUI applications.
    Whereas `multiprocessing` takes advantage of multiple available cores.

2.  `multithreading` module was found to have issues with pip.main(). For more
    information about the issue click `here <https://github.com/pypa/pip/issues/2553>`_

But, tkinter widgets can't be updated from another thread or process
except the main thread or process. Therefore, possible solutions to this
problem are :

1.  Re-implement `mainloop()` method of tkinter in a thread-safe way. The
    `mainloop()` method is basically an endless loop responsible for
    periodically checking for runtime updates made to GUI and rendering them
    on the screen. A few thread-safe implementations are available like:

    -   `mtTkinter <http://tkinter.unpythonic.net/wiki/mtTkinter>`_

2.  Tkinter is designed to run from the main thread, only. See the docs:

        ``Just run all UI code in the main thread, and let the writers write to a
        Queue object.``

    The reason for tkinter to not be thread safe is that many objects and
    subsystems don't like receiving requests from multiple various threads,
    and in the case of GUI toolkit it's not rare to need specifically to use
    the main thread only.

Generally, the right Python architecture for this problem is to devote a
process (the main one, if one must) to serving the finicky object or
subsystem; every other process requiring interaction with said subsystem or
object must then obtain it by queueing requests to the dedicated process
(and possibly waiting on a "return queue" for results, if results are required as a
consequence of some request).

Therefore, `multiprocessing` module was chosen to log real time output from
running process to tkinter text widget.::

    class RunpipSubprocess():
        """
        Run pip with argument string containing command and options. Uses
        subprocess module for executing pip commands. Logs real time output in
        output queue.

        In output queue a tuple object is sent consisting of two elements:

        -   Output code : For identification of purpose of message

            Code    Purpose
            0       Start marker for logging output to tkinter text widget
            1       Output message
            2       Error message
            3       End marker for logging output to tkinter text widget

        -   Message : a string variable containing the string collected from
            stdout and stderr streams
        """

        def __init__(self, argstring, output_queue):
            """
            Initialize subprocess for running pip commands.

            :param output_queue: queue for buffering line by line output
            :param argstring: is quoted version of what would follow 'pip' on
             command line.
            """

            self.pip_process = subprocess.Popen(
                argstring.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            self.output_queue = output_queue

        def start_logging_threads(self):
            """
            Starts logging to output and error queue
            """

            # If system platform is not Windows
            if get_build_platform()!='Windows':

                fileio_streams = [
                    self.pip_process.stdout.fileno(),
                    self.pip_process.stderr.fileno(),]

                #Do I/O multiplexing
                io_iterator = select.select(fileio_streams, [], [])
                self.output_queue.put((0, 'process_started'))

                while True:

                    #iterate over available file descriptors in io_iterator
                    for file_descrp in io_iterator[0]:

                        #if something is there in stdout stream
                        if file_descrp == self.pip_process.stdout.fileno():
                            pipout = self.pip_process.stdout.readline()
                            self.output_queue.put((1,pipout))

                        #else check in stderr stream
                        elif file_descrp == self.pip_process.stderr.fileno():
                            piperr = self.pip_process.stderr.readline()
                            self.output_queue.put((2,piperr))

                    #Check if process has ended, if process is not completed
                    #then self.pip_process.poll() returns None
                    if self.pip_process.poll() != None:
                        self.output_queue.put((3,self.pip_process.poll()))
                        break

            #Else if platform is Windows
            else:
                #Create two child threads for this alternate process
                #output thread manages stdout
                output_thread = threading.Thread(target=self.getoutput)
                #error thread manages stderr
                error_thread = threading.Thread(target=self.geterror)

                #send 'process started' indication with message code : 0
                self.output_queue.put((0, 'process_started'))

                #starts both threads
                output_thread.start()
                error_thread.start()

                #Wait for both threads to complete their execution
                output_thread.join()
                error_thread.join()

                #If both threads are completed, then this alternate process should
                #end. If execution completed, then
                if self.pip_process.poll() != None:
                    #Send ending message with process code and message code as 3
                    self.output_queue.put((3,self.pip_process.poll()))

        def getoutput(self):
            """
            Iterate over output line by line
            """

            for line in iter(self.pip_process.stdout.readline, b''):
                self.output_queue.put((1,line))
            self.pip_process.stdout.close()
            self.pip_process.wait()

        def geterror(self):
            """
            Iterate over error line by line
            """

            for line in iter(self.pip_process.stderr.readline, b''):
                self.output_queue.put((2,line))
            self.pip_process.stderr.close()
            self.pip_process.wait()

pip_tkinter.utils.downloadfile
------------------------------

This utility is used in a multiprocessing or multithreaded way. It has been
used to download files with periodic feedback about the percentage of file
downloaded. It also uses a queue based approach to pass results from one process
to another process (or from one thread to another thread).::

    def downloadfile(url, update_queue):
        """
        A utility function to download file in small chunks and also to return
        download percentage

        Code    Purpose
        0       Start marker for logging output
        1       Output message
        2       End marker for logging output
        3       Error message

        """
        import math
        from urllib.request import urlopen, Request
        from urllib.error import HTTPError, URLError

        targetfile = os.path.basename(url)
        resource_dir = create_resource_directory()

        try:
            update_queue.put((0,'Started downloading ...'))

            file_path = os.path.join(resource_dir, targetfile)
            req = Request(
                url=url,
                headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:47.0) Gecko/20100101 Firefox/47.0'})
            req = urlopen(req)

            total_size = int(req.info()['Content-Length'].strip())

            downloaded = 0
            chunk_size = 256 * 10240

            with open(file_path, 'wb') as fp:
                while True:
                    chunk = req.read(chunk_size)
                    downloaded += len(chunk)
                    update_queue.put((1,math.floor((downloaded/total_size)*100)))
                    if not chunk:
                        break
                    fp.write(chunk)
            update_queue.put((2,'Completed downloading'))
        except HTTPError as e:
            update_queue.put((3,"HTTP Error: {} {}".format(e.code, url)))
            return False
        except URLError as e:
            update_queue.put((3,"URL Error: {} {}".format(e.reason, url)))
            return False

        return True

.. toctree::
    :maxdepth: 4
