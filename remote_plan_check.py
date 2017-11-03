#!/home/tops/bin/python
# -*- coding: utf-8 -*-
import sys

DEFAULT_PY_PATH = '/home/tops/bin/python'
DEFAULT_BASH_PATH = '/bin/bash'
TASK_SAVE_PATH = '/tmp/task/'

COMMAND_PS = 'ps -ef|grep work_schedule.py|grep %s |wc -l'
COMMAND_EXEC = 'nohup ' + DEFAULT_PY_PATH + ' ' + TASK_SAVE_PATH + 'work_schedule.py %s %s %s > /dev/null 2>&1 &'
COMMAND_KILL = 'ps -ef|grep work_schedule.py|grep %s|awk \'{print $2}\'|xargs -I {} kill -9 {}'
COMMAND_MKDIR = 'mkdir -p %s'
COMMAND_EXISTS = 'ls %s|grep %s |wc -l'
COMMAND_REMOVE = 'rm -rf %s'
__HELP = '''
%s  <option> <conf> <local:remote> [interval] [other command...]
    example:
        %s -r default /tmp/demo/:/tmp/demo/example.py 0 cp#/tmp/demo/result.json#/root/
        option:
            -r --run : copy local file to remote and run it(if task exists remove them).
            -s --start : copy local file to remote and run it(if task exists ignore them).
            -c --check : just check remote task, 1=running 0=not running
            -u --user : run your command only
            -h --help : ...
        conf:
            the ssh config file path
            if you don't know wtf it is. use "default"
            "default" is ./conf.cfg
        local:
            local file path.(can be directory)
            if use check mode local can be void.
            if use user mode local and remote can be void.(excludes ":")
        remote:
            remote file path.(only can be .py or .sh)
            if use user mode local and remote can be void.(excludes ":")
        interval:
            script execution interval (minutes).
            zero for never.
            default is 10.
        other command:
            other commands executed after the script completes.
            use '#' to replace ' '
'''

__WORK_SCHEDULE = '''
#!/home/tops/bin/python
# -*- coding: utf-8 -*-
import commands

from Logger import init_logger

LOG_FILE = '/tmp/task/WorkSchedule.log'

def run_cmd(cmd):
    s, r = commands.getstatusoutput(cmd)
    if s > 0:
        logger.error("error,run cmd: %s, cause: %s, exit %d" % (cmd, r, s))
        raise SystemError("error,run cmd: %s, cause: %s, exit %d" % (cmd, r, s))
    return s, r


def time_task(command, sleep_time=10, args=None):
    if args is None:
        args = []
    import time
    while True:
        logger.info("run command %s" % command.replace('#', ' '))
        run_cmd(command.replace('#', ' '))
        for cmd in args:
            cmd = str(cmd).replace('#', ' ')
            logger.info("run command %s" % cmd)
            run_cmd(cmd)
        logger.info("%s sleep %s min." % (command, sleep_time))
        if int(sleep_time) == 0:
            return
        else:
            time.sleep(int(sleep_time) * 60)


if __name__ == "__main__":
    import sys

    logger = init_logger("WorkSchedule", LOG_FILE)
    if len(sys.argv) == 1:
        print "%s  <command> [sleep] [command...] " % sys.argv[0]
    if len(sys.argv) == 2:
        time_task(sys.argv[1])
    if len(sys.argv) == 3:
        time_task(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 3:
        time_task(sys.argv[1], sys.argv[2], sys.argv[3:])
'''


def _format_path(path):
    if path.endswith('.sh') or path.endswith('.py'):
        return path[0:path.rfind('/')] + '/'
    if not path.endswith('/'):
        return path + '/'
    else:
        return path


def _help():
    print __HELP % (sys.argv[0], sys.argv[0])


ssh = None


def _start_ssh(conf):
    import SSHClient
    import ConfigReader
    global ssh
    config = ConfigReader.ConfigReader(conf)
    ssh = SSHClient.SSHClient(config)
    ssh.start()


def _stop_ssh():
    global ssh
    ssh.stop()


def _work_schedule():
    global ssh
    if int(ssh.exec_command(COMMAND_EXISTS % (TASK_SAVE_PATH, 'work_schedule.py'))) == 0:
        ssh.exec_command(COMMAND_MKDIR % TASK_SAVE_PATH)
        ssh.open_sftp()
        ssh.put('work_schedule.py', TASK_SAVE_PATH + 'work_schedule.py')
        ssh.put('Logger.py', TASK_SAVE_PATH + 'Logger.py')
        ssh.close_sftp()


def _run():
    global option, conf_file, local, remote, interval, other_commands
    global ssh
    bash = remote.endswith(".py") and DEFAULT_PY_PATH or DEFAULT_BASH_PATH
    # 尝试杀掉进程并删除remote
    ssh.exec_command(COMMAND_KILL % remote)
    ssh.exec_command(COMMAND_REMOVE % remote)
    ssh.open_sftp()
    import os
    # 上传local
    if os.path.isdir(local):
        local = _format_path(local)
        files = os.listdir(local)
        if int(ssh.exec_command(COMMAND_EXISTS % (_format_path(remote), remote))) == 0:
            ssh.exec_command(COMMAND_MKDIR % _format_path(remote))
        for f in files:
            ssh.put(local + f, _format_path(remote) + f)
    else:
        ssh.put(local, remote)
    ssh.close_sftp()
    # 尝试启动使用work_schedule启动remote
    ssh.exec_command(COMMAND_EXEC % (bash + '#' + remote, interval, other_commands))
    # print local, remote, interval, other_commands


def _start():
    global option, conf_file, local, remote, interval, other_commands
    global ssh
    if _check() == 0:
        _run()


def _check():
    global option, conf_file, local, remote, interval, other_commands
    global ssh
    result = int(ssh.exec_command(COMMAND_PS % remote)) > 1 and 1 or 0
    print result
    return result


def _user():
    global option, conf_file, local, remote, interval, other_commands
    global ssh
    ssh.exec_command(COMMAND_EXEC % (other_commands.replace(' ', ''), interval, ''))
    # print other_commands


option = None
conf_file = None
local = None
remote = None
interval = None
other_commands = None

switch = {
    '-r': _run,
    '-s': _start,
    '-c': _check,
    '-u': _user,
    '-h': _help
}


def chose():
    global option, conf_file, local, remote, interval, other_commands
    # test ↓
    option = '-r'
    conf_file = None
    local = 'd:/Download/cld_check.sh'
    remote = '/tmp/demo/cld_check.sh'
    interval = 0
    other_commands = 'docker#cp#/apsarapangu/cloud_log.$(date "+%Y-%m-%d-%H-%M-%S").tar.gz#asd:/tmp'
    # test ↑
    option = sys.argv[1]
    conf_file = sys.argv[2]
    if conf_file == 'default':
        conf_file = None
    local = sys.argv[3].split(':')[0]
    remote = sys.argv[3].split(':')[1]
    interval = 10
    other_commands = ''
    if len(sys.argv) > 4:
        interval = int(sys.argv[4])
    if len(sys.argv) > 5:
        tmp = sys.argv[5:]
        for command in tmp:
            other_commands += command + ' '

    fun = switch[option]
    if fun is None:
        _help()
        return
    _start_ssh(conf_file)
    _work_schedule()
    fun()
    _stop_ssh()


if __name__ == '__main__':
    argv_len = len(sys.argv)
    # if argv_len < 4:
    #     _help()
    # else:
    chose()
