import unittest

from cron import CronExpression


class CronExpressionTestCase(unittest.TestCase):

    def test_simple_example(self):
        c = CronExpression('0 0 1 * 1-5 script.sh')
        output = c.print_expansion()

        self.assertEqual(
            output,
            'minute        0\n'
            'hour          0\n'
            'day of month  1\n'
            'month         1 2 3 4 5 6 7 8 9 10 11 12\n'
            'day of week   1 2 3 4 5\n'
            'command       script.sh'
        )

    def test_example_with_all_five_specification_types(self):
        # input uses literal, wildcard, range, interval, and selection syntax simultaneously
        c = CronExpression('*/15 0 1,15 * 1-5 /usr/bin/find')
        output = c.print_expansion()

        self.assertEqual(
            output,
            'minute        0 15 30 45\n'
            'hour          0\n'
            'day of month  1 15\n'
            'month         1 2 3 4 5 6 7 8 9 10 11 12\n'
            'day of week   1 2 3 4 5\n'
            'command       /usr/bin/find'
        )

    def test_example_with_month_aliases(self):
        c = CronExpression('0/10 12 5-12 jan/3 * command_text')
        output = c.print_expansion()

        self.assertEqual(
            output,
            'minute        0 10 20 30 40 50\n'
            'hour          12\n'
            'day of month  5 6 7 8 9 10 11 12\n'
            'month         1 4 7 10\n'
            'day of week   0 1 2 3 4 5 6\n'
            'command       command_text'
        )

    def test_example_with_weekday_aliases(self):
        c = CronExpression('0/10 12 5-12 jan/3 mon-THU do some stuff')
        output = c.print_expansion()

        self.assertEqual(
            output,
            'minute        0 10 20 30 40 50\n'
            'hour          12\n'
            'day of month  5 6 7 8 9 10 11 12\n'
            'month         1 4 7 10\n'
            'day of week   1 2 3 4\n'
            'command       do some stuff'
        )

    def test_example_with_range_wrap_around(self):
        c = CronExpression('0/10 12 5-12 jan/3 4-0 do some stuff')
        output = c.print_expansion()

        self.assertEqual(
            output,
            'minute        0 10 20 30 40 50\n'
            'hour          12\n'
            'day of month  5 6 7 8 9 10 11 12\n'
            'month         1 4 7 10\n'
            'day of week   0 4 5 6\n'
            'command       do some stuff'
        )

    def test_example_with_invalid_range(self):
        # ranges such as 5-3 are invalid because 3 is less than 5
        c = CronExpression('0/10 12 5-3 jan/3 mon-thu do some stuff')
        self.assertRaises(ValueError, c.print_expansion)

    def test_example_with_excessively_large_literal(self):
        c = CronExpression('0/10 100 5-3 jan/3 mon-thu do some stuff')
        self.assertRaises(ValueError, c.print_expansion)

    def test_example_with_invalid_literal_format(self):
        c = CronExpression('0/10 blah 5-3 jan/3 mon-thu do some stuff')
        self.assertRaises(ValueError, c.print_expansion)

    def test_example_with_too_few_fields(self):
        c = CronExpression('0/10 5-3 jan/3 mon-thu do some stuff')
        self.assertRaises(ValueError, c.print_expansion)

    def test_example_with_month_alias_in_wrong_field(self):
        # cannot use a month alias in any field other than month, similar for weekdays
        c = CronExpression('feb 5-3 jan/3 mon-thu do some stuff')
        self.assertRaises(ValueError, c.print_expansion)


if __name__ == '__main__':
    unittest.main()
