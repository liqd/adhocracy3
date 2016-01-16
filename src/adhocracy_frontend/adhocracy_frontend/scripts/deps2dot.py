"""Extract graph of angular module dependencies in DOT format."""

import subprocess
import os
import re
import argparse


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
        module['recursive_import_count'] = len(module['recursive_imports'])
        set_recursive_exports(module)
        module['recursive_export_count'] = len(module['recursive_exports'])


def add_rank(modules):
    """Add rank to an existing dict of modules."""
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
    keys.sort(key=lambda k: (-modules[k]['recursive_export_count'], k))
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


def draw_matrix(matrix, names):
    density = sum([sum(row) for row in matrix]) / float(len(matrix) ** 2)
    s = 'P1\n'
    s += '# density: %f\n' % density
    for name in names:
        s += '# %s\n' % name
    n = len(matrix)
    s += '%i %i\n' % (n, n)
    for row in matrix:
        s += ' '.join([str(int(i)) for i in row]) + '\n'
    return s


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

    return parser.parse_args()


def main():
    """Print module graph in DOT format to stdout."""
    args = parse_args()
    modules = get_modules()
    add_counts(modules)
    add_recursive_counts(modules)
    max_rank = add_rank(modules)

    if args.matrix:
        m, names = adjacency_matrix(modules, direct=args.direct)
        print(draw_matrix(m, names))
    else:
        if args.max_rank is None:
            args.max_rank = max_rank

        print('digraph adhocracy_frontend {')
        print('  graph [splines=ortho];')

        for rank in range(args.min_rank, args.max_rank):
            print('  subgraph rank%i {' % rank)
            print('    rank = same;')
            for path, module in modules.items():
                if include(module, args) and module['rank'] == rank:
                    print(render_module(module))
            print('  }')

        for module in modules.values():
            if include(module, args):
                for imp in module['imports']:
                    if include(modules[imp], args):
                        print('  %s->%s [color=%s];' % (
                            modules[imp]['name'],
                            module['name'],
                            modules[imp]['color']))

        print('}')


if __name__ == '__main__':
    main()
