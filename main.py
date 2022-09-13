import sys

from cron import CronExpression

if __name__ == '__main__':
    CronExpression(sys.argv[1]).print_expansion()
