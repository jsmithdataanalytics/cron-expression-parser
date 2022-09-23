import re
from typing import List


class CronExpression:

    _MONTH_ALIASES = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12,
    }

    _WEEKDAY_ALIASES = {
        'sun': 0,
        'mon': 1,
        'tue': 2,
        'wed': 3,
        'thu': 4,
        'fri': 5,
        'sat': 6,
    }

    def __init__(self, cron_string: str):
        self.cron_string = cron_string

        self._minute = None
        self._hour = None
        self._day_of_month = None
        self._month = None
        self._day_of_week = None
        self._command = None

    def print_expansion(self) -> str:
        self._expand()

        cron_field_names = ['minute', 'hour', 'day of month', 'month', 'day of week']
        output_text = ''

        for field_name in cron_field_names:
            values = self.__getattribute__(f'_{field_name.replace(" ", "_")}')
            values_string = ' '.join(map(str, values))
            output_text += field_name.ljust(14, ' ') + values_string + '\n'

        output_text += f'command       {self._command}'

        print(output_text)

        return output_text

    def _expand(self):
        cron_string = self.cron_string.strip()

        # split into five cron fields, then take whatever remains as the command
        fields = cron_string.split(maxsplit=5)

        if len(fields) != 6:
            raise ValueError(f'Expected 5 cron fields, found {len(fields) - 1}')

        # expand each cron field into a sorted list of integer values
        self._minute = self._expand_cron_field(fields[0], 0, 59)
        self._hour = self._expand_cron_field(fields[1], 0, 23)
        self._day_of_month = self._expand_cron_field(fields[2], 1, 31)
        self._month = self._expand_cron_field(fields[3], 1, 12, allow_month_aliases=True)
        self._day_of_week = self._expand_cron_field(
            field=fields[4],
            min_value=0,
            max_value=6,
            allow_weekday_aliases=True,
            allow_range_wrap_around=True
        )

        self._command = fields[5]

    def _expand_cron_field(
        self,
        field: str,
        min_value: int,
        max_value: int,
        allow_month_aliases: bool = False,
        allow_weekday_aliases: bool = False,
        allow_range_wrap_around: bool = False,
    ) -> List[int]:
        """Expands a single cron field specification into a sorted list of integer values
        :param field: string representing a single cron field specification, e.g. "0-5"
        :param min_value: the lowest valid value for the cron field, e.g. lowest valid hour is 0
        :param max_value: the highest valid value for the cron field, e.g. highest valid hour is 23
        :param allow_month_aliases: whether to allow use of month aliases in this field, e.g. "jan"
        :param allow_weekday_aliases: whether to allow use of weekday aliases in this field, e.g. "mon"
        :param allow_range_wrap_around: whether to allow backward ranges, e.g. "5-1"
        """

        # normalise to lower case so that month and weekday aliases are case insensitive
        field = field.lower()

        # construct a regex that will match only valid literals
        # usually, only sequences of digits are valid
        valid_literals = ['\\d+']

        # if we're allowing month or weekday aliases, then literals such as "jan" and "mon" are valid
        if allow_month_aliases:
            valid_literals += list(self._MONTH_ALIASES.keys())

        elif allow_weekday_aliases:
            valid_literals += list(self._WEEKDAY_ALIASES.keys())

        # construct the literal regex
        literal = f'({"|".join(valid_literals)})'

        # if "*", return full range
        if re.fullmatch('\\*', field):
            values = list(range(min_value, max_value + 1))

        # if single literal, return single value
        elif re.fullmatch(literal, field):
            values = [self._convert_literal_to_integer(field)]

        # if range between two literals, expand range
        elif re.fullmatch(f'{literal}-{literal}', field):
            first_value = self._convert_literal_to_integer(field.split('-')[0])
            last_value = self._convert_literal_to_integer(field.split('-')[1])

            is_first_value_bad = first_value < min_value or first_value > max_value
            is_last_value_bad = last_value < min_value or last_value > max_value

            if is_first_value_bad or is_last_value_bad:
                raise ValueError(f'Invalid range specified: {field}')

            if first_value > last_value:

                if not allow_range_wrap_around:
                    raise ValueError(f'Invalid range specified: {field}')

                values = list(range(min_value, last_value + 1)) + list(range(first_value, max_value + 1))

            else:
                values = list(range(first_value, last_value + 1))

        # if step value syntax, expand
        elif re.fullmatch(f'({literal}|\\*)/\\d+', field):
            # "*" in this context means start at minimum value
            field = field.replace('*', str(min_value))
            first_value = self._convert_literal_to_integer(field.split('/')[0])
            interval = int(field.split('/')[1])

            if first_value < min_value or first_value > max_value:
                raise ValueError(f'Invalid specification, initial value out of bounds: {field}')

            values = list(range(first_value, max_value + 1, interval))

        # if comma-separated literals, extract them all
        elif re.fullmatch(f'{literal}(,{literal})+', field):
            literals = field.split(',')
            values = [self._convert_literal_to_integer(literal) for literal in literals]

        # if none of the above cases match, it is invalid or unsupported cron syntax
        else:
            raise ValueError(f'Invalid cron field: {field}')

        # if a value is outside the allowable range, then the expression must include an invalid literal
        if not all([min_value <= value <= max_value for value in values]):
            raise ValueError(f'Found values outside the range [{min_value}, {max_value}]: {values}')

        return sorted(values)

    def _convert_literal_to_integer(self, literal: str) -> int:
        """Converts a literal into an integer value
        E.g. "005" -> 5
        E.g. "feb" -> 2
        E.g. "sat" -> 6
        """
        output = self._MONTH_ALIASES.get(literal, literal)
        output = self._WEEKDAY_ALIASES.get(output, output)

        return int(output)

    def __repr__(self):
        return f"<{self.__class__.__name__}('{self.cron_string}')>"
