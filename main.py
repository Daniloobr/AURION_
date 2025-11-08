# main.py
import aurion
from interface import iniciar_sistema

def main():
    aurion.inicializar_banco()
    # Se quiser rodar a interface gráfica:
    iniciar_sistema()
    # Se preferir CLI, poderia chamar aurion.menu() — mas aurion.menu() foi removido do backend para evitar execução em import.

if __name__ == "__main__":
    main()
