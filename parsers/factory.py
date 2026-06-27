from .base import BaseParser

class ParserFactory:
    @staticmethod
    def iter_parsers(fpath: str, meta: dict[str]):
        provided = False
        for parcer_cls in BaseParser.__subclasses__():
            if parcer_cls.can_parse(fpath):
                provided = True
                yield parcer_cls(fpath, meta)
        if not provided:
            raise ValueError('Unable to parse any data from the file.')