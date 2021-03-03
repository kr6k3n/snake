from multiprocessing import Pool
from tqdm import tqdm
PROCESSES=4

import fastrand

r_number = lambda : fastrand.pcg32bounded(1E4)


def fastmap(function, iterable, display_progress=False):
    with Pool(processes=PROCESSES) as p:
        max_ = len(iterable)
        with tqdm(total=max_) as pbar:
            result = None
            for i, _ in (result := enumerate(p.imap_unordered(func=function, iterable=iterable))):
                pbar.update()

