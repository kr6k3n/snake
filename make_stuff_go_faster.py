from multiprocessing import Pool
from tqdm import tqdm


PROCESSES=10

import fastrand

r_number = lambda : fastrand.pcg32bounded(1E4)


def fastmap(function, iterable, display_progress=False):
    with Pool(processes=PROCESSES) as p:
        max_ = len(iterable)
        if display_progress:
            with tqdm(total=max_) as pbar:
                result = list()
                for res in p.imap_unordered(func=function, iterable=iterable):
                    pbar.update()
                    result.append(res)
                return result
        else:
            return list(p.imap_unordered(func=function, iterable=iterable))


#test
if __name__ == '__main__':
    def double(x):
        return x*2
    print(list(fastmap(double, range(10))))