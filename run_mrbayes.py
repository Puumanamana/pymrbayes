import yaml
import argparse
from pathlib import Path
import subprocess


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--msa', type=str)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--outdir', type=str)

    with open('CLI.yaml') as cfg_file:
        cfg = yaml.safe_load(cfg_file)

    for group, args in cfg.items():
        parser_gr = parser.add_argument_group(group)
        for name, vals in args.items():
            del vals['type']
            # vals['type'] = eval(vals['type'])
            parser_gr.add_argument(f'--{name}', **vals)

    args = parser.parse_args()

    args_dict = {'set': dict(autoclose='yes', nowarn='no', autoreplace='yes', dir=args.outdir)}
    args_dict.update({group: {k: getattr(args, k) for k, v in options.items()
                              if getattr(args, k) != v['default']}
                      for group, options in cfg.items()})

    args_dict.update(msa=args.msa, run=args.run, outdir=args.outdir)

    return args_dict

def main():

    args_dict = parse_args()

    msa = Path(args_dict.pop('msa'))
    run = args_dict.pop('run')
    outdir = args_dict.pop('outdir')
    output = Path(outdir, 'mrbayes.nex')

    output.parent.mkdir()
    mrbayes(msa, output, args_dict)

    if run:
        subprocess.run(['mb', output], check=True)

def mrbayes(msa, output, options):
    with open(output, 'w') as writer:
        lines = ['begin mrbayes;', f'execute {msa};']

        for k, v in options.items():
            if v:
                args = format_args(v)
                lines += [f'{k} {args};']

        writer.write('\n\t'.join(lines))
        writer.write('\nend;\n')

def format_args(mapping):
    return ' '.join([f'{k}={v}' for (k, v) in mapping.items()])

if __name__ == '__main__':
    main()
