from dataclasses import dataclass


class TagSlug(str):
    pass


@dataclass
class Tag:
    name: str
    slug: TagSlug
    page_count: int = 0


def make_tag_slug(tag_name: str) -> TagSlug:
    from slugify import slugify

    return TagSlug(slugify(tag_name, lowercase=True))
