"""
   example:
   killprocs python
   will kill all processes with python in the name
   requires:
      
      conda install psutil
"""
import psutil
from .helper_funs import make_tuple

import argparse
import textwrap


def on_terminate(proc):
    print("process {} terminated with exit code {}".format(
               proc, proc.returncode))

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = textwrap.dedent(__doc__)
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('snip', type=str, help='string in processname')
    return parser

def main(args=None):
    """
    args: optional -- if missing then args will be taken from command line
          or pass [snippet] -- string to search for in processes
    """
    parser = make_parser()
    args = parser.parse_args(args)
    keepit = {}
    keys = ['time', 'name', 'cmdline', 'proc']
    for proc in psutil.process_iter():
        try:
            the_dict = dict(zip(keys, (proc.create_time(), proc.exe(),
                                       proc.cmdline(), proc)))
            keepit[proc.pid] = make_tuple(the_dict)
        except (psutil.ZombieProcess, psutil.AccessDenied,
                psutil.NoSuchProcess):
            pass
        except FileNotFoundError:
            pass
    print(f'in killprocs, looking for {args.snip}')
    #
    # don't kill this process or the emacs python parser
    #
    proclist = []
    for the_tup in keepit.values():
        string_cmd = ' '.join(the_tup.cmdline)
        if the_tup.name.find(args.snip) > -1 and \
           string_cmd.find('killprocs') == -1 and \
           string_cmd.find('elpy') == -1:
            proclist.append(the_tup)

    proconly = [item.proc for item in proclist]
    if proconly:
        print(f'ready to kill {proconly}')
    for item in proconly:
        cmd_string = ' '.join(item.cmdline())
        print('terminating: {}'.format(cmd_string))
    [proc.terminate() for proc in proconly]

    gone, alive = psutil.wait_procs(proconly, timeout=3, callback=on_terminate)

    for p in alive:
        p.kill()


if __name__ == "__main__":

    main()
    