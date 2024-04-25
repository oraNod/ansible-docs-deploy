import argparse
import dataclasses
import os
import shutil

DEFAULT_SOURCE_DIR = "docs-build"
DEFAULT_OUTPUT_DIR = "output"


@dataclasses.dataclass()
class Args:
    source: str
    output: str


def parse_args(args: list[str] | None = None) -> Args:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        help="Specify the name of the source directory. Default: %(default)s",
        default=DEFAULT_SOURCE_DIR,
    )
    parser.add_argument(
        "--output",
        help="Specify the name of the target directory. Default: %(default)s",
        default=DEFAULT_OUTPUT_DIR,
    )
    return Args(**vars(parser.parse_args(args)))


def main(args: Args):

    if os.path.exists(args.output):
        shutil.rmtree(args.output)

    shutil.copytree(args.source, args.output, symlinks=True)

    if os.path.exists(args.output):
        print("Build files copied successfully.")
    else:
        print("Failed to copy build files.")


if __name__ == "__main__":
    main(parse_args())
