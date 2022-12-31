from pathlib import Path
import json
from distutils.util import strtobool
from .realtime_triggers.triggers import TRIGGER_TYPES, TransitionTrigger
from .realtime_triggers.actions import AVAILABLE_ACTIONS



def bool_from_str(value):
    if type(value) == bool:
        return value
    elif type(value) == str:
        return bool(strtobool(value))


def comma_separated_list(value):
    if type(value) is list:
        return value
    elif type(value) is str:
        return [element.strip() for element in value.split()]
    else:
        raise TypeError(
            f"unexpected type when converting to comma-separated list: {type(value)}"
        )


def expanded_user_path(value):
    return Path(value).expanduser()


def range_str(range_str, sort=True):
    """Generate range of ints from a formatted string,
    then convert range from int to str

    Examples
    --------
    >>> range_str('1-4,6,9-11')
    ['1','2','3','4','6','9','10','11']

    Takes a range in form of "a-b" and returns
    a list of numbers between a and b inclusive.
    Also accepts comma separated ranges like "a-b,c-d,f"  which will
    return a list with numbers from a to b, c to d, and f.

    Parameters
    ----------
    range_str : str
        of form 'a-b,c', where a hyphen indicates a range
        and a comma separates ranges or single numbers
    sort : bool
        If True, sort output before returning. Default is True.

    Returns
    -------
    list_range : list
        of integer values converted to single-character strings, produced by parsing range_str
    """
    # adapted from
    # http://code.activestate.com/recipes/577279-generate-list-of-numbers-from-hyphenated-and-comma/
    s = "".join(range_str.split())  # removes white space
    list_range = []
    for substr in range_str.split(","):
        subrange = substr.split("-")
        if len(subrange) not in [1, 2]:
            raise SyntaxError(
                "unable to parse range {} in labelset {}.".format(subrange, substr)
            )
        list_range.extend([int(subrange[0])]) if len(
            subrange
        ) == 1 else list_range.extend(range(int(subrange[0]), int(subrange[1]) + 1))

    if sort:
        list_range.sort()

    return [str(list_int) for list_int in list_range]


def labelset_to_set(labelset):
    """convert value for 'labelset' argument into a Python set.
    Used by ``vak`` internally to convert

    Parameters
    ----------
    labelset : str, list
        string or list specifying a unique set of labels
        used to annotate a dataset of vocalizations.
        See Notes for details on valid values.

    Returns
    -------
    labelset : set
        of strings, labels used to annotate segments.

    Notes
    -----
    If ``labelset```` is a str, and it starts with "range:", then everything after range is converted to
    some range of integers, by passing the string to ``vak.config.converters.range_str``,
    and the returned list is converted to a set. E.g. "range: 1-5" becomes {'1', '2', '3', '4', '5'}.
    Other strings that do not start with "range:" are just converted to a set. E.g. "abc" becomes {'a', 'b', 'c'}.

    If ``labelset`` is a list, then all values in the list must strings or integers.
    Any that begin with "range:" will be passed to vak.config.converters.range_str.
    Any other multiple-character strings in a list are **not** split,
    unlike when the value for the ``labelset`` option is just a single string
    with multiple characters.
    If you have segments annotated with multiple characters,
    you should specify them using a list, e.g., ['en', 'ab', 'cd']

    If ``labelset`` is a set, it is returned as is, so that this function does not return ``None``,
    which would cause other functions to behave as if no ``labelset`` were specified.

    Examples
    --------
    >>> labelset_from_toml_value('abc')
    {'a', 'b', 'c'}
    >>> labelset_from_toml_value('1235')
    {'1', '2', '3', '5'}
    >>> labelset_from_toml_value('range: 1-3, 5')
    {'1', '2', '3', '5'}
    >>> labelset_from_toml_value([1, 2, 3, 5])
    {'1', '2', '3'}
    >>> labelset_from_toml_value(['a', 'b', 'c'])
    {'a', 'b', 'c'}
    >>> labelset_from_toml_value(['range: 1-3', 'noise'])
    {'1', '2', '3', 'noise'}
    """
    if type(labelset) not in (str, list, set):
        raise TypeError(
            "labelset must be specified as a string, list, or set, "
            f"but the type of labelset was: {type(labelset)}"
        )

    if type(labelset) is set:
        return labelset
    elif type(labelset) is str:
        if labelset.startswith("range:"):
            labelset = labelset.replace("range:", "")
            return set(range_str(labelset))
        else:
            return set(labelset)
    elif type(labelset) is list:
        labelset_out = []
        for label in labelset:
            if isinstance(label, int):
                labelset_out.append(str(label))
            elif isinstance(label, str):
                if label.startswith("range:"):
                    label = label.replace("range:", "")
                    labelset_out.extend(range_str(label))
                else:
                    labelset_out.append(label)
            else:
                raise TypeError(
                    f"label '{label}' specified in labelset is invalid type: {type(label)}."
                    "Labels must be strings or integers."
                )
        return set(labelset_out)

def json_path_to_trigger_list(json_path):
    """Opens the path to the json file, and uses it to create rules. 
    Raises type errors if the file is not formatted as triggers - 
    as you can't validate after converting (the convertion will fail or the validation message will be very ambigious).
    """
    triggers_file = open(Path(json_path).expanduser(), 'r')
    triggers_json = json.load(triggers_file)

    if not "triggers" in triggers_json:
        raise TypeError("No trigger list in this JSON! Please refer to the example file.")
    
    for trig in triggers_json["triggers"]:
        if not "type" in trig:
            raise TypeError(f"'{trig}' has no type! Please refer to the example file.")
        if not trig["type"] in TRIGGER_TYPES:
            raise TypeError(f"No such trigger type as {trig['type']}")
        if not "callback" in trig:
            raise TypeError(f"'{trig}' has no callback! Please refer to the example file.")
        if not trig["callback"] in AVAILABLE_ACTIONS:
            raise TypeError(f"{trig['callback']} is an unknown callback! Please refer to the example file.")

        # TODO: This is ugly. Maybe create a trigger factory.
        if trig["type"] == "Transition":
            if not "from" in trig:
                raise TypeError("Transision triggers should have a 'from' field")
            if not "to" in trig and len(trig["to"]) == 1:
                raise TypeError("Transision triggers should have a 'to' field")

    trig_list = []
    for trigger_json in triggers_json["triggers"]:
        if trigger_json["type"] == "transition":
            trig_list.append(TransitionTrigger(AVAILABLE_ACTIONS[trigger_json["callback"]], trigger_json["from"], trigger_json["to"]))
    
    return trig_list