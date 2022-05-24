from dataclasses import dataclass
from pathlib import Path
from typing import Union

from calepin.models import Website
from calepin.utils.logger import Logger


@dataclass
class FileSystemWriter:
    output_directory: Union[str, Path]
    logger: Logger

    def write(self, website: Website):
        for page in website.pages:
            output_path = Path(self.output_directory) / page.url
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w") as f:
                f.write(page.content)
