import sys


def warning(*objs):
    """
    Write warnings to stderr.
    """
    print("WARNING: ", *objs, file=sys.stderr)
