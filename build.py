import os
import subprocess
import argparse
import shutil
import sys


def run_command(command, working_dir=None):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=working_dir)
        output, error = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command, output=output, stderr=error)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.cmd}")
        print(f"Error message: {e.stderr.decode('utf-8')}")
        return False


def copy_bibliography(source_dir, output_dir):
    try:
        bib_file_src = os.path.join(source_dir, 'bibliography.bib')
        bib_file_dst = os.path.join(output_dir, 'bibliography.bib')
        shutil.copy(bib_file_src, bib_file_dst)
        return True
    except FileNotFoundError:
        print("Bibliography file not found.")
        return False


def compile_latex(tex_file, output_dir):
    xelatex_command = f"xelatex -output-directory={output_dir} {tex_file}"
    return run_command(xelatex_command)


def compile_bibtex(tex_file, output_dir):
    base_name = os.path.splitext(os.path.basename(tex_file))[0]
    os.chdir(output_dir)
    bibtex_command = f"bibtex {base_name}"
    success = run_command(bibtex_command)
    os.chdir(os.path.dirname(tex_file))  # Change back to the source directory
    return success


def parse_arguments():
    parser = argparse.ArgumentParser(description='Compile LaTeX project.')
    parser.add_argument('--outdir', default=None, help='Output directory (default: source_dir/out)')
    parser.add_argument('--file', default=None, help='Main LaTeX file (default: source_dir/main.tex)')
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.file is None:
        source_dir = os.path.dirname(os.path.abspath(__file__))
        tex_file = os.path.join(source_dir, 'main.tex')
    else:
        source_dir = os.path.dirname(os.path.abspath(args.file))
        tex_file = args.file

    if args.outdir is None:
        output_dir = os.path.join(source_dir, 'out')
    else:
        output_dir = args.outdir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not copy_bibliography(source_dir, output_dir):
        print("Failed to copy bibliography file.")
        sys.exit(1)

    if not compile_latex(tex_file, output_dir):
        print("Failed to compile LaTeX document.")
        sys.exit(1)

    if not compile_bibtex(tex_file, output_dir):
        print("Failed to compile BibTeX.")
        sys.exit(1)

    if not compile_latex(tex_file, output_dir):
        print("Failed to compile LaTeX document.")
        sys.exit(1)

    print("Build completed successfully.")


if __name__ == "__main__":
    main()
