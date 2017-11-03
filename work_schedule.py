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
