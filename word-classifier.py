import sys
import csv
import curses
import logging
import argparse
import operator


# List of class names
KEYWORD = 'keyword'
NOISE = 'noise'
RELEVANT = 'relevant'
NOTRELEVANT = 'not-relevant'

keys = {
    KEYWORD: 'k',
    NOISE: 'n',
    RELEVANT:'r',
    NOTRELEVANT: 'x'
}


# FIXME: the key2class dict shall be obtained by "reversing" the keys dict
key2class = {
    'k': KEYWORD,
    'n': NOISE,
    'r': RELEVANT,
    'x': NOTRELEVANT
}

def init_argparser():
    """Initialize the command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument('datafile', action="store", type=str,
        help="input CSV data file")
    parser.add_argument('--dry-run', action='store_false', dest='dry_run',
        help='do not write the results on exit')
    return parser


def load_words(infile):
    with open(infile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        items = []
        for row in csv_reader:
            if line_count == 0:
                header = row
                line_count += 1
            else:
                items.append(row)
                line_count += 1
    return (header, items)


def write_words(outfile):
    with open(outfile, mode='w') as out:
        writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        for w in words:
            writer.writerow(w[:4])


class Win(object):
    """Contains the list of lines to display."""
    def __init__(self, key, title='', rows=3, cols=30, y=0, x=0):
        self.key = key
        self.title = title
        self.rows = rows
        self.cols = cols
        self.y = y
        self.x = x
        self.win_handler = curses.newwin(self.rows, self.cols, self.y, self.x)
        self.win_handler.border()
        self.win_handler.refresh()
        self.lines = []

    def display_lines(self, rev=True, highlight_word=None):
        if rev:
            word_list = reversed(self.lines)
        else:
            word_list = self.lines
        i = 0
        for w in word_list:
            trunc_w = w[:self.cols - 2]
            if highlight_word is None:
                self.win_handler.addstr(i + 1, 1, trunc_w + ' '*(self.cols - 2 - len(trunc_w)))
            else:
                tok = w.split(highlight_word)
                self.win_handler.addstr(i + 1, 1, '')
                for t in tok:
                    self.win_handler.addstr(t)
                    self.win_handler.addstr(highlight_word, curses.color_pair(1))
                self.win_handler.addstr(i + 1, len(trunc_w) + 1, ' '*(self.cols - 2 - len(trunc_w)))
            i += 1
            if i >= self.rows - 2:
                break
        while i < self.rows - 2:
            self.win_handler.addstr(i + 1, 1, ' '*(self.cols - 2))
            i += 1
        self.win_handler.border()
        self.win_handler.refresh()

    def assign_lines(self, lines):
        self.lines = [w[0] for w in lines if w[2] == self.key]
        #print(self.lines)


def avg_or_zero(num, den):
    """Safely calculatess an average, returning 0 if no elements are present."""
    if den > 0:
        avg = 100 * num / den
    else:
        avg = 0
    return avg


def get_stats_strings(words):
    stats_strings = []
    n_completed = len([w for w in words if w[2] != ''])
    n_keywords = len([w for w in words if w[2] == 'k'])
    n_noise = len([w for w in words if w[2] == 'n'])
    n_not_relevant = len([w for w in words if w[2] == 'x'])
    n_later = len([w for w in words if w[2] == 'p'])
    stats_strings.append('Total words:  {:7}'.format(len(words)))
    avg = avg_or_zero(n_completed, len(words))
    stats_strings.append('Completed:    {:7} ({:6.2f}%)'.format(n_completed, avg))
    avg = avg_or_zero(n_keywords, n_completed)
    stats_strings.append('Keywords:     {:7} ({:6.2f}%)'.format(n_keywords, avg))
    avg = avg_or_zero(n_noise, n_completed)
    stats_strings.append('Noise:        {:7} ({:6.2f}%)'.format(n_noise, avg))
    avg = avg_or_zero(n_not_relevant, n_completed)
    stats_strings.append('Not relevant: {:7} ({:6.2f}%)'.format(n_not_relevant, avg))
    avg = avg_or_zero(n_later, n_completed)
    stats_strings.append('Postponed:    {:7} ({:6.2f}%)'.format(n_later, avg))
    return stats_strings


def find_word(string, substring):
   return any([substring == word for word in string.split()])


def return_related_items(words, key):
    containing = []
    not_containing = []
    for w in words:
        if (w[2] != ''):
            continue
        if (find_word(w[0], key)):
            containing.append(w[0])
        else:
            not_containing.append(w[0])
    return containing, not_containing


def mark_word(words, word, marker, order):
    for w in words:
        if w[0] == word:
            w[2] = marker
            w[3] = order
            break
    return words


def init_curses():
    # create stdscr
    stdscr = curses.initscr()
    stdscr.clear()

    # allow echo, set colors
    curses.noecho()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

    return stdscr


def main(args, words, datafile):
    stdscr = init_curses()
    win_width = 40

    # define windows
    windows = {
        KEYWORD: Win(KEYWORD, title='Keywords', rows=12, cols=win_width, y=0, x=0),
        NOISE: Win(NOISE, title='Noise', rows=12, cols=win_width, y=12, x=0),
        NOTRELEVANT: Win(NOTRELEVANT, title='Not-relevant', rows=12, cols=win_width, y=24, x=0)
    }
    curses.ungetch(' ')
    c = stdscr.getch()
    for win in windows:
        windows[win].assign_lines(words)
        windows[win].display_lines()
    words_window = Win(None, rows=27, cols=win_width, y=9, x=win_width)
    stats_window = Win(None, rows=9, cols=win_width, y=0, x=win_width)
    stats_window.lines = get_stats_strings(words)
    stats_window.display_lines(rev=False)

    related_items_count = 0
    words_window.lines = [w[0] for w in words if w[2] == '']
    sort_word_key = None
    orders = [int(w[3]) for w in words if w[3] != '']
    if len(orders) == 0:
        order = 0
    else:
        order = max(orders)
    while True:
        evaluated_word = words_window.lines[0]
        words_window.display_lines(rev=False, highlight_word=sort_word_key)
        c = stdscr.getch()
        if c in [ord(keys[KEYWORD]), ord(keys[NOTRELEVANT])]:
            words = mark_word(words, evaluated_word, chr(c), order)
            order += 1
            win = windows[key2class[chr(c)]]
            win.lines.append(evaluated_word)
            words_window.lines = words_window.lines[1:]
            win.display_lines()
            related_items_count -= 1
        elif c == ord(keys[NOISE]):
            words = mark_word(words, evaluated_word, chr(c), order)
            order += 1
            win = windows[key2class[chr(c)]]
            win.lines.append(evaluated_word)
            win.display_lines()
            if related_items_count <= 0:
                sort_word_key = evaluated_word
            containing, not_containing = return_related_items(words, sort_word_key)
            if related_items_count <= 0:
                related_items_count = len(containing) + 1
            #logging.debug("related_items_count: {}".format(related_items_count))
            words_window.lines = containing
            words_window.lines.extend(not_containing)
            #logging.debug("words_window.lines: {}".format(words_window.lines))
            words_window.display_lines(rev=False, highlight_word=sort_word_key)
            related_items_count -= 1
        elif c == ord('p'):
            words = mark_word(words, evaluated_word, chr(c), order)
            order += 1
            words_window.lines = words_window.lines[1:]
            related_items_count -= 1
        elif c == ord('w'):
            write_words(datafile)
        elif c == ord('u'):
            orders = [int(w[3]) for w in words if w[3] != '']
            if len(orders) == 0:
                continue
            else:
                max_index, max_value = max(enumerate(orders), key=operator.itemgetter(1))
            w = words[max_index][0]
            logging.debug("{} {} {}".format(max_index, max_value, w))
            words = mark_word(words, w, '', '')
            order -= 1
            rwl = [w]
            rwl.extend(words_window.lines)
            words_window.lines = rwl
        elif c == ord('q'):
            break
        stats_window.lines = get_stats_strings(words)
        stats_window.lines.append('Related:      {:7}'.format(related_items_count if related_items_count >= 0 else 0))
        stats_window.display_lines(rev=False)


if __name__ == "__main__":
    logging.basicConfig(filename='slr-kit.log',
            filemode='a',
            format='%(asctime)s [%(levelname)s] %(message)s',
            level=logging.DEBUG)
    parser = init_argparser()
    args = parser.parse_args()

    (header, words) = load_words(args.datafile)

    curses.wrapper(main, words, args.datafile)
    curses.endwin()

    if args.dry_run:
        write_words(args.datafile)
