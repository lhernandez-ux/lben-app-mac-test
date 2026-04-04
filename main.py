"""
main.py
=======
LBEn App — Resolución UPME 016/2024
Punto de entrada principal.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ui.theme import aplicar_tema
from ui.app import App


def main():
    aplicar_tema()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()