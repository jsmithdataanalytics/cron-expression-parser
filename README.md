# Cron Expression Parser
A Python 3 script for parsing and expanding cron expressions. Pass in a valid cron string, 
and see it printed out in expanded form!

## Dependencies
  - Python 3.6+

## Run
Run `main.py` with a cron string as a command line argument. For example:

```python main.py "*/15 0 1,15 * 1-5 /usr/bin/find"```

## Features
This project defines a `CronExpression` class, which can be used to represent and expand cron expressions.

```
c = CronExpression('0 12 * * *')
c.print_expansion()
```

### Supported cron features
All standard cron features are supported. For example:
  - use of `*`
  - use of range syntax, e.g. `1-5`
  - use of step value syntax, e.g. `0/2` or `*/4`
  - use of comma syntax, e.g. `15,25,50`
  - use of month aliases, e.g. `jan` or `DEC`
  - use of weekday aliases, e.g. `mon` or `FRI`

### Unsupported features
Non-standard cron syntax is not supported. For example:
  - use of `@hourly` and similar shorthands
  - use of `7` for day of week
  - use of `L`, `W`, `#`, or `?`