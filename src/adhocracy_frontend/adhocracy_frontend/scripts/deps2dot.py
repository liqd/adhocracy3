"""Extract informaton about angular module dependencies.

For some of the concepts, see http://almossawi.com/firefox/
"""

import subprocess
import os
import re
import argparse

CATEGORIES = ['peripheral', 'control', 'shared', 'core']


def normpath(path):
    """Strip everything until 'Packages' from the beginning of the path."""
    parts = path.split('/')
    if 'Packages' in parts:
        parts = parts[parts.index('Packages') + 1:]
    return os.path.normpath('/'.join(parts))


def color(name):
    """Get pseudo-random color."""
    n = int.from_bytes(name.encode('utf8'), byteorder='big')
    h = (n % 41) / 41
    s = (n % 37) / 37
    return '"{:.4} {:.4} {:.4}"'.format(h, s, 0.5)


def get_modules():
    """Get a dictionary of existing modules and their dependencies."""
    modules = {}

    lines = subprocess.check_output(['git', 'grep', 'moduleName = '])

    for line in lines.decode('utf8').split('\n'):
        if 'ts:' in line:
            path, name = line.split(':export var moduleName = ')
            dirname = os.path.dirname(path)
            name = name.strip('";')
            imports = []

            with open(path) as fh:
                for line in fh:
                    match = re.match('import \* as .* from "(.*)";', line)
                    if match:
                        import_path = match.groups()[0] + '.ts'
                        if import_path.endswith('Module.ts'):
                            joined = os.path.join(dirname, import_path)
                            imports.append(normpath(joined))

            modules[normpath(path)] = {
                'name': name,
                'imports': imports,
                'color': color(name),
            }

    return modules


def add_counts(modules):
    """Add import_count/export_count to an existing dict of modules."""
    for module in modules.values():
        module['exports'] = set()

    for path, module in modules.items():
        for imp in module['imports']:
            modules[imp]['exports'].add(path)

    for path, module in modules.items():
        module['import_count'] = len(module['imports'])
        module['export_count'] = len(module['exports'])


def add_recursive_counts(modules):
    """Add fan_in/fan_out to an existing dict of modules.

    These are like import_count/export_count, but recursive.
    """
    def set_recursive_imports(module):
        k = 'recursive_imports'
        if k not in module:
            module[k] = set(module['imports'])
            for key in module['imports']:
                imp = modules[key]
                set_recursive_imports(imp)
                module[k] = module[k].union(imp[k])

    def set_recursive_exports(module):
        k = 'recursive_exports'
        if k not in module:
            module[k] = set(module['exports'])
            for key in module['exports']:
                exp = modules[key]
                set_recursive_exports(exp)
                module[k] = module[k].union(exp[k])

    for module in modules.values():
        set_recursive_imports(module)
        module['fan_in'] = len(module['recursive_imports'])
        set_recursive_exports(module)
        module['fan_out'] = len(module['recursive_exports'])


def add_rank(modules):
    """Add rank to an existing dict of modules.

    The rank of a module is always greater that that of its dependencies.
    """
    done = []

    while len(done) < len(modules):
        for path, module in modules.items():
            imports = module['imports']

            if path not in done and all((p in done for p in imports)):
                if not imports:
                    module['rank'] = 0
                else:
                    ranks = [modules[imp]['rank'] for imp in imports]
                    module['rank'] = max(ranks) + 1
                done.append(path)

    return max([m['rank'] for m in modules.values()])


def _filter(modules, args):
    """Remove some modules from the dict according to command line args."""
    remove = set()
    for key, module in modules.items():
        if not include(module, args):
            remove.add(key)

    for key in remove:
        del modules[key]

    for module in modules.values():
        module['imports'] = [i for i in module['imports'] if i in modules]


def add_category(modules):
    """Mark a module as 'peripheral', 'control', 'shared', or 'core'."""
    n = len(modules)
    average_in = sum(m['fan_in'] for m in modules.values()) / float(n)
    average_out = sum(m['fan_out'] for m in modules.values()) / float(n)

    for module in modules.values():
        i = 0
        if module['fan_in'] > average_in:
            i += 1
        if module['fan_out'] > average_out:
            i += 2
        module['category'] = CATEGORIES[i]


def render_module(module):
    """Render a module to string."""
    opts = ['color=%s' % module['color']]

    if module['import_count'] == 0:
        opts.append('shape=box')
    if module['export_count'] == 0:
        opts.append('style=dotted')

    return '    %s [%s];' % (module['name'], ','.join(opts))


def include(module, args):
    """Return True if the module should be included in the output."""
    if not (args.min_rank <= module['rank'] <= args.max_rank):
        return False
    if any((re.search(x, module['name'], re.I) for x in args.exclude)):
        return False
    return True


def adjacency_matrix(modules, direct=False):
    keys = list(modules.keys())
    keys.sort(key=lambda k: (-modules[k]['fan_out'], k))
    names = [modules[key]['name'] for key in keys]

    m = []
    for row_key in keys:
        module = modules[row_key]
        row = []
        for column_key in keys:
            if direct:
                row.append(column_key in module['imports'])
            else:
                row.append(column_key in module['recursive_imports'])
        m.append(row)

    return m, names


def print_matrix(matrix, names):
    print('P1')
    for name in names:
        print('# %s' % name)
    n = len(matrix)
    print('%i %i' % (n, n))
    for row in matrix:
        print(' '.join([str(int(i)) for i in row]))


def print_stats(modules, verbose=True):
    n = len(modules)
    print('total modules: %i' % n)
    for category in CATEGORIES:
        mods = [m for m in modules.values() if m['category'] == category]
        k = len(mods)
        names = sorted([m['name'] for m in mods])
        print('%s modules: %i, %i%%' % (category, k, 100 * k / n))
        if verbose:
            for name in names:
                print('  %s' % name)
    matrix, _names = adjacency_matrix(modules)
    propagation_cost = sum([sum(row) for row in matrix]) / n
    print('propagation cost: %i, %i%%' % (propagation_cost, 100 * propagation_cost / n))
    print('max rank: %i' % max((m['rank'] for m in modules.values())))


def parse_args():
    """Parse command line argumants."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--min-rank', type=int, default=0)
    parser.add_argument('--max-rank', type=int, default=None)
    parser.add_argument('-x', '--exclude', nargs='*', default=[])

    parser.add_argument('--matrix', action='store_true', help='Output '
        'dependency matrix as PBM. If you want to only include direct '
        'dependencies, use the --direct switch')
    parser.add_argument('--direct', action='store_true')

    parser.add_argument('--stats', action='store_true', help='Output '
        'some general stats')
    parser.add_argument('-v', '--verbose', action='store_true')

    return parser.parse_args()


def main():
    """Print module graph in DOT format to stdout."""
    args = parse_args()
    modules = get_modules()
    max_rank = add_rank(modules)
    if args.max_rank is None:
        args.max_rank = max_rank
    _filter(modules, args)
    add_counts(modules)
    add_recursive_counts(modules)
    add_category(modules)

    if args.matrix:
        m, names = adjacency_matrix(modules, direct=args.direct)
        print_matrix(m, names)
    elif args.stats:
        print_stats(modules, verbose=args.verbose)
    else:
        print('digraph adhocracy_frontend {')
        print('  graph [splines=ortho];')

        for rank in range(args.min_rank, args.max_rank + 1):
            print('  subgraph rank%i {' % rank)
            print('    rank = same;')
            for path, module in modules.items():
                if module['rank'] == rank:
                    print(render_module(module))
            print('  }')

        for module in modules.values():
            for imp in module['imports']:
                print('  %s->%s [color=%s];' % (
                    modules[imp]['name'],
                    module['name'],
                    modules[imp]['color']))

        print('}')


if __name__ == '__main__':
    main()
