import tables as tb
import pandas as pd
from tables import NoSuchNodeError
import warnings

def load_dst(filename, group, node):
    with tb.open_file(filename) as h5in:
        try:
            table = getattr(getattr(h5in.root, group), node).read()
            return pd.DataFrame.from_records(table)
        except NoSuchNodeError:
            warnings.warn(f' warning: could no load  {filename}')


def load_dsts(dst_list, group, node):
    dsts = [load_dst(filename, group, node) for filename in dst_list]
    return pd.concat(dsts)
