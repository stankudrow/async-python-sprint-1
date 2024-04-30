from typing import TextIO

import click

from src.tasks import main_task


@click.command()
@click.argument(
    "cities",
    nargs=-1,
    type=str,
)
@click.option(
    "-o",
    "--out",
    "fout",
    default="-",
    type=click.File(mode="w"),
    help="the output file or stream (specify '-' for the stdout)",
)
def main(cities: tuple[str], fout: TextIO):
    main_task(city_names=cities, file_object=fout)


main()
