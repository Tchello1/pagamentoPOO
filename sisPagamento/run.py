import sys
import os

# Adiciona o caminho para o sisPagamento no sys.path pra forçar reconhecimento do pacote
sys.path.append(os.path.abspath("sisPagamento"))

from sisPagamento.main import main

if __name__ == "__main__":
    main()
