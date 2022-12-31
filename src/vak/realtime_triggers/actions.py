def print_to_screen(trig, cur_stream, match):
    """
    A simple trigger action which prints the 10 symbols before and after the trigger.
    Parameters
    ----------
    cur_stream : str list
        The stream of lables currently assigned to the realtime audio stream.
    match: regex.match
        The match that triggered the trigger.
    """
    start = max(0, match.start()-10)
    end = min(len(cur_stream), match.end()+10)
    
    print(f"{trig} was triggered! State:\n\t\
        ...{'-'.join(cur_stream[start:end])}\n\t\
        ({len(cur_stream)-10} segments not printed).")

AVAILABLE_ACTIONS = {"print_to_screen": print_to_screen}