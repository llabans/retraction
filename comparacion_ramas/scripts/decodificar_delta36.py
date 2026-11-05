"""Decodifica una lista de PMIDs exportada desde el navegador (ver harness_navegador.js, encodeDelta36)
y verifica que coincidan el número de identificadores y su suma, que se anotan en el navegador.

Uso: python3 -I decodificar_delta36.py ENTRADA_delta36.txt SALIDA_pmids.txt N_ESPERADO SUMA_ESPERADA
"""
import sys


def main():
    entrada, salida, n_esp, suma_esp = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    tokens = open(entrada, encoding="utf-8").read().strip().split(",")
    v, ids = 0, []
    for t in tokens:
        v += int(t, 36)
        ids.append(v)
    ok = len(ids) == n_esp and sum(ids) == suma_esp
    print(f"n={len(ids)} suma={sum(ids)} verificado={ok}")
    if not ok:
        sys.exit(1)
    with open(salida, "w", encoding="utf-8") as f:
        f.write("\n".join(map(str, ids)) + "\n")


if __name__ == "__main__":
    main()
