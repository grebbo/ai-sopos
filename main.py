import argparse
import random
import sys
from config import THEMES, LENGTHS
from generator import generate_story
from output import save_story


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fiaba",
        description="Genera fiabe per bambini tramite OpenAI.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--random",
        action="store_true",
        help="genera una fiaba con tema casuale",
    )
    mode.add_argument(
        "--tema",
        choices=list(THEMES.keys()),
        metavar="TEMA",
        help="tema della fiaba: " + ", ".join(THEMES.keys()),
    )
    mode.add_argument(
        "--temi",
        action="store_true",
        help="mostra i temi disponibili ed esci",
    )

    parser.add_argument(
        "--parole-chiave",
        metavar="PAROLE",
        help='parole chiave di ispirazione, separate da virgola (es. "mare, conchiglia, amicizia")',
    )
    parser.add_argument(
        "--lunghezza",
        choices=list(LENGTHS.keys()),
        default="media",
        help="lunghezza della fiaba (default: media)",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="nome del file di output (salvato in output/); default: <titolo>_<timestamp>.txt",
    )
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="non mostrare la fiaba in console, salva solo su file",
    )

    return parser


def _print_story(title: str, body: str) -> None:
    sep = "─" * 60
    print(f"\n{sep}")
    print(f"  {title}")
    print(sep)
    print(body)
    print(sep)


def _ask_regenerate() -> bool:
    while True:
        answer = input("\nVuoi rigenerare la fiaba? (s/n): ").strip().lower()
        if answer in ("s", "si", "sì", "y", "yes"):
            return True
        if answer in ("n", "no"):
            return False


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.temi:
        print("Temi disponibili:")
        for nome, descrizione in THEMES.items():
            print(f"  {nome:12} — {descrizione}")
        sys.exit(0)

    theme = random.choice(list(THEMES.keys())) if args.random else args.tema

    keywords = []
    if args.parole_chiave:
        keywords = [k.strip() for k in args.parole_chiave.split(",") if k.strip()]

    print(f"Generazione fiaba in corso...")
    print(f"  Tema:      {theme}")
    print(f"  Lunghezza: {args.lunghezza} (~{LENGTHS[args.lunghezza]} parole)")
    if keywords:
        print(f"  Ispirazione: {', '.join(keywords)}")

    while True:
        try:
            title, body = generate_story(theme, keywords, args.lunghezza)
        except EnvironmentError as e:
            print(f"\nErrore: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\nErrore durante la generazione: {e}", file=sys.stderr)
            sys.exit(1)

        if not args.no_preview:
            _print_story(title, body)
            if _ask_regenerate():
                print("\nRigenerazione in corso...")
                continue

        break

    filepath = save_story(title, body, theme, args.output)
    print(f"\nFiaba salvata in: {filepath}")


if __name__ == "__main__":
    main()
