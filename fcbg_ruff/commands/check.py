import fnmatch
from pathlib import Path

import click

from ..check import validate_folder


@click.command(name="check")
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--output",
    help="Path to the output file.",
    type=click.Path(exists=False, dir_okay=False),
    prompt="Path to the output file",
)
@click.option(
    "--ignore",
    "-i",
    help="Ignore the provided file global pattern.",
    type=str,
    multiple=True,
)
@click.option("--jobs", help="Number of jobs running in parallel.", type=int, default=1)
def run(folder, output, ignore, jobs) -> None:
    """Run check() command."""
    folder = Path(folder)
    output = Path(output)
    if not output.parent.exists():
        raise FileNotFoundError(f"Parent folder '{output.parent}' does not exist.")
    violations = validate_folder(folder, jobs)
    # filter out ignored patterns
    for key in ("primary", "secondary"):
        violations[key] = {
            key: value
            for key, value in violations[key].items()
            if not any(fnmatch.fnmatch(key.as_posix(), pattern) for pattern in ignore)
        }
    # write results
    with open(output, "w") as f:
        for key in ("primary", "secondary"):
            f.write(f"\n{key.capitalize()} violations:\n\n")
            for elt, value in violations[key].items():
                f.write(f"{value}\t{elt.relative_to(folder)}\n")
