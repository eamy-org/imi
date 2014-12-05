__all__ = ['main']


def main():
    from .bin.imi import main as entry
    entry()


if __name__ == '__main__':  # pragma: no cover
    main()
