CARDS_CLASSIC = {
    "normal": {
    },
    "not_playable": {
        "r_0": "CAADAgAD9l8AAqG-aEm1N0MDmDKmuQI",
        "r_1": "CAADAgADCl8AAkmuaUluF1n2I8-47wI",
        "r_2": "CAADAgADrmAAAqmLaUn_xH_m5MZCGAI",
        "r_3": "CAADAgADLGUAAl8MaEln0qeSdyHJvAI",
        "r_4": "CAADAgADJFwAArrlaUnNgARazALoSwI",
        "r_5": "CAADAgADXmUAAqT9aUniTrgZNO6VQwI",
        "r_6": "CAADAgAD_18AAsbNaUmQtV8W1Rnl1AI",
        "r_7": "CAADAgAD8GQAAlsEaUmuWtwLO1Lk6QI",
        "r_8": "CAADAgAD714AAvn6aUmMH4kb0r2N5gI",
        "r_9": "CAADAgADQGAAAgKPaEmoacqaEnp8tAI",
        "r_draw": "CAADAgAD9mQAAtnnYUlEpboCdX8qrAI",
        "r_reverse": "CAADAgADWloAAjjNaUlWXvrnmEy3xwI",
        "r_skip": "CAADAgADCWgAAvsHaUl7v6RBUl8PlAI",
        "g_0": "CAADAgADLWcAArqXaEm4wBY2S8eqpAI",
        "g_1": "CAADAgAD9GAAAsSBaUkUM8BL6ccUKAI",
        "g_2": "CAADAgADzmUAAp--aEn9498Mhr_kSAI",
        "g_3": "CAADAgADFl4AAitIaUnjPMUFFd7KTAI",
        "g_4": "CAADAgADQFkAAl2AaUkyanMOPXbRLwI",
        "g_5": "CAADAgADnm0AAr-0aUkZn781zzosUAI",
        "g_6": "CAADAgADA1kAAsJoaUnzTX_u2fW5FwI",
        "g_7": "CAADAgADqF4AAkXsaUmJOP0m7XXC9wI",
        "g_8": "CAADAgADEGIAAnoHaEmM2XXh-W9ZqgI",
        "g_9": "CAADAgADFloAAjd3aUmdabV4t7JBpAI",
        "g_draw": "CAADAgADFGIAAtADaEn_WWFq49idHQI",
        "g_reverse": "CAADAgADkVsAAl4baEnQmC8B7PLk7gI",
        "g_skip": "CAADAgADu14AAn3fYUmgC__ZYoW3wwI",
        "b_0": "CAADAgADPWcAAv_LaUmTh1_yMkS96gI",
        "b_1": "CAADAgADVlsAAjEnYElGUTtPoAGXCgI",
        "b_2": "CAADAgADLWEAArjYaUmSjSAi3PRIUgI",
        "b_3": "CAADAgADeF4AAt0YaEn8A4f2u3o-AwI",
        "b_4": "CAADAgADaF0AAvxVaEnuW8vbG1ldRQI",
        "b_5": "CAADAgADP1oAAjOtaUneHfpcA9NPtgI",
        "b_6": "CAADAgADCl4AArAUaEmPRoVJZ1ERnAI",
        "b_7": "CAADAgADhl4AAjFDaEkhBGKU4DFu1gI",
        "b_8": "CAADAgADrGYAAup_aEmJr4vqhx3GmgI",
        "b_9": "CAADAgADNmMAAoqYaUnvt34qaMi7qAI",
        "b_draw": "CAADAgADX1wAAslNaEkF16twdqHJCQI",
        "b_reverse": "CAADAgADmmAAApQ4aEm-DEug76oHAQI",
        "b_skip": "CAADAgADdV4AAjL0aEl--q81vXlCMwI",
        "y_0": "CAADAgADp2UAAk2SaEmoCVHGcgdTtQI",
        "y_1": "CAADAgADoF4AAou7aElRVaTkOU18WwI",
        "y_2": "CAADAgADF1QAAgOxaEnb8upzNW4xgAI",
        "y_3": "CAADAgADgFkAAqh_aUngp6xP4JXcPQI",
        "y_4": "CAADAgADzVcAAsLmaUm-PHHdJDTxEQI",
        "y_5": "CAADAgADYWMAArRoaElOqOjVhm_kvgI",
        "y_6": "CAADAgADM2IAApHRaUnqGYs6DsRCwgI",
        "y_7": "CAADAgADTVoAAuGzaEmUrXjZTeRAiQI",
        "y_8": "CAADAgADL2QAAnLiaEnovkFJevgaFwI",
        "y_9": "CAADAgADi1kAAtnsaElCTVZiHuCa8QI",
        "y_draw": "CAADAgADJGAAAnMXaEkIuKQWnVoHVAI",
        "y_reverse": "CAADAgAD514AAg0LaEmCIOaD-A2JiQI",
        "y_skip": "CAADAgADN1wAAi50aUnbZeAAAUpdIN0C"
    }
}


class Card(object):
    """Represents an UNO card."""

    def __init__(self, color, value, special=None):
        self.color = color
        self.value = value
        self.special = special

    def __str__(self):
        if self.special:
            return self.special
        else:
            return '%s_%s' % (self.color, self.value)

    def __repr__(self):
        if self.special:
            return '%s%s%s' % (COLOR_ICONS.get(self.color, ''),
                               COLOR_ICONS[BLACK],
                               ' '.join([s.capitalize()
                                         for s in self.special.split('_')]))
        else:
            return '%s%s' % (COLOR_ICONS[self.color], self.value.capitalize())

    def __eq__(self, other):
        """Needed for sorting the cards."""
        return str(self) == str(other)

    def __lt__(self, other):
        """Needed for sorting the cards."""
        return str(self) < str(other)


def from_str(string):
    """Decodes a Card object from a string."""
    if string not in SPECIALS:
        color, value = string.split('_')
        return Card(color, value)
    else:
        return Card(None, None, string)
