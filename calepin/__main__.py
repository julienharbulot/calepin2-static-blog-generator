import argparse
from pathlib import Path

from .formatters import MarkdownFormatter
from .loaders import FileSystemLoader
from .use_cases import CompileWebsiteUseCase
from .utils import Logger
from .writters import FileSystemWriter

parser = argparse.ArgumentParser(description="Calepin static website generator")

parser.add_argument(
    "input_dir", type=Path, help="input directory containing source files"
)

parser.add_argument(
    "output_dir",
    type=Path,
    help="output directory where to write the generated website",
)
args = parser.parse_args()

logger = Logger()
loader = FileSystemLoader(args.input_dir, logger)
writer = FileSystemWriter(args.output_dir, logger)

compiler = CompileWebsiteUseCase(loader, [MarkdownFormatter()], writer, logger)

compiler.compile()
