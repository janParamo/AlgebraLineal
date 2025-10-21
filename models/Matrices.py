from typing import List, Tuple, Dict, Any
from fractions import Fraction
import json
import os

EPS = 1e-10

class GaussResult:
    def __init__(self, pasos: List[str], augmented: List[List[float]], pivotes: List[Tuple[int,int]]):
        self.pasos = pasos
        self.augmented = augmented
        self.pivotes = pivotes

def format_val(x):
    if abs(x) < EPS:
        return "0"
    elif x == int(x):
        return str(int(x))
    else:
        return str(Fraction(x).limit_denominator())

class Matrices:
    @staticmethod
    def _is_identity(mat: List[List[float]], tol: float = 1e-8) -> bool:
        if not mat:
            return False
        n = len(mat)
        m = len(mat[0])
        if n != m:
            return False
        for i in range(n):
            for j in range(m):
                if i == j:
                    if abs(mat[i][j] - 1.0) > tol:
                        return False
                else:
                    if abs(mat[i][j]) > tol:
                        return False
        return True
    @staticmethod
    def _aug_to_str(aug: List[List[float]], split: int) -> str:
        """Formatea una matriz aumentada mostrando claramente [Matriz | Matriz reducida].

        split indica el índice de separación entre el bloque izquierdo (A) y el derecho (I o A^{-1}).
        """
        lines = []
        for i in range(len(aug)):
            left = " ".join(f"{aug[i][j]:8.4f}" for j in range(split))
            right = " ".join(f"{aug[i][j]:8.4f}" for j in range(split, len(aug[i])))
            lines.append(f"[ {left} | {right} ]")
        return "\n".join(lines)

    @staticmethod
    def _mat_to_str_frac(mat: List[List[float]]) -> str:
        """Formatea una matriz usando fracciones simplificadas para cada entrada."""
        return "\n".join(
            "[ " + " ".join(format_val(x) for x in row) + " ]" for row in mat
        )

    @staticmethod
    def _aug_to_str_frac(aug: List[List[float]], split: int) -> str:
        """Formatea una matriz aumentada usando fracciones: [Matriz | Matriz reducida]."""
        lines = []
        for i in range(len(aug)):
            left = " ".join(format_val(aug[i][j]) for j in range(split))
            right = " ".join(format_val(aug[i][j]) for j in range(split, len(aug[i])))
            lines.append(f"[ {left} | {right} ]")
        return "\n".join(lines)
    @staticmethod
    def _validate_a_b(a: List[List[float]], b: List[List[float]]):
        if not isinstance(a, list) or not a or not isinstance(b, list) or not b:
            raise ValueError("Las matrices A y B no pueden estar vacías.")
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        if len(b) != len(a):
            raise ValueError("El número de filas de B debe coincidir con A.")
        if any(len(row) != 1 for row in b):
            raise ValueError("B debe ser un vector columna (nx1).")
        if m < 2:
            raise ValueError("A debe tener al menos 2 columnas (2 incógnitas).")

    @staticmethod
    def gauss(a: List[List[float]], b: List[List[float]]) -> GaussResult:
        Matrices._validate_a_b(a, b)
        n = len(a)
        m = len(a[0])
        augmented = [a[i][:] + b[i][:] for i in range(n)]
        pasos = []
        pivotes = []
        for col in range(min(n, m)):
            max_row = max(range(col, n), key=lambda r: abs(augmented[r][col]))
            if abs(augmented[max_row][col]) < EPS:
                pasos.append(f"No hay pivote en columna {col+1}, se salta.")
                continue
            if max_row != col:
                augmented[col], augmented[max_row] = augmented[max_row], augmented[col]
                pasos.append(f"Intercambio de fila {col+1} con fila {max_row+1}")
            pivotes.append((col, col))
            piv = augmented[col][col]
            if abs(piv - 1) > EPS:
                for j in range(m+1):
                    augmented[col][j] /= piv
                pasos.append(f"f{col+1} --> (1/{piv:.4f})*f{col+1}")
                pasos.append(Matrices._mat_to_str(augmented))
            for row in range(col+1, n):
                factor = augmented[row][col]
                if abs(factor) > EPS:
                    for j in range(m+1):
                        augmented[row][j] -= factor * augmented[col][j]
                    signo = "+" if factor > 0 else "-"
                    pasos.append(f"f{row+1} --> f{row+1} {signo} ({abs(factor):.4f})*f{col+1}")
                    pasos.append(Matrices._mat_to_str(augmented))
        pasos.append("Estado final:\n" + Matrices._mat_to_str(augmented))
        return GaussResult(pasos, augmented, pivotes)

    @staticmethod
    def gauss_jordan(a: List[List[float]], b: List[List[float]]) -> GaussResult:
        Matrices._validate_a_b(a, b)
        n = len(a)
        m = len(a[0])
        augmented = [a[i][:] + b[i][:] for i in range(n)]
        pasos = []
        pivotes = []
        row = 0
        for col in range(m):
            sel = None
            for r in range(row, n):
                if abs(augmented[r][col]) > EPS:
                    sel = r
                    break
            if sel is None:
                pasos.append(f"No hay pivote en columna {col+1}, se salta.")
                continue
            if sel != row:
                augmented[row], augmented[sel] = augmented[sel], augmented[row]
                pasos.append(f"Intercambio de fila {row+1} con fila {sel+1}")
                pasos.append(Matrices._mat_to_str(augmented))
            pivotes.append((row, col))
            piv = augmented[row][col]
            if abs(piv - 1) > EPS:
                for j in range(m+1):
                    augmented[row][j] /= piv
                pasos.append(f"f{row+1} --> (1/{piv:.4f})*f{row+1}")
                pasos.append(Matrices._mat_to_str(augmented))
            for r in range(n):
                if r != row and abs(augmented[r][col]) > EPS:
                    factor = augmented[r][col]
                    for j in range(m+1):
                        augmented[r][j] -= factor * augmented[row][j]
                    signo = "+" if factor > 0 else "-"
                    pasos.append(f"f{r+1} --> f{r+1} {signo} ({abs(factor):.4f})*f{row+1}")
                    pasos.append(Matrices._mat_to_str(augmented))
            row += 1
            if row == n:
                break
        pasos.append("Estado final:\n" + Matrices._mat_to_str(augmented))
        return GaussResult(pasos, augmented, pivotes)

    @staticmethod
    def clasificar_y_resolver_from_rref(gauss_result: GaussResult) -> Dict[str, Any]:
        mat = gauss_result.augmented
        n = len(mat)
        m = len(mat[0]) - 1
        tipo = "determinada"
        solucion = [0.0] * m
        libres = []
        for row in mat:
            if all(abs(x) < EPS for x in row[:-1]) and abs(row[-1]) > EPS:
                return {"tipo": "incompatible"}
        pivote_col = [-1] * n
        for i in range(n):
            for j in range(m):
                if abs(mat[i][j]) > EPS:
                    pivote_col[i] = j
                    break
        usados = set([c for c in pivote_col if c != -1])
        libres = [j for j in range(m) if j not in usados]
        if len(usados) < m:
            tipo = "indeterminada"
        if tipo == "determinada":
            for i in range(n):
                if pivote_col[i] != -1:
                    solucion[pivote_col[i]] = mat[i][-1]
            return {"tipo": tipo, "solucion": solucion, "libres": libres}
        else:
            return {"tipo": tipo, "solucion_parametrica": ["paramétrica"], "libres": libres}

    @staticmethod
    def _mat_to_str(mat: List[List[float]]) -> str:
        # Formato tipo [1.0000 | 0.0625 | ... ]
        return "\n".join(
            " | ".join(f"{x:8.4f}" for x in row)
            for row in mat
        )

    # -------------------- Nuevas utilidades --------------------
    @staticmethod
    def multiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        """Multiplica dos matrices a (n x m) y b (m x p) devolviendo (n x p)."""
        if not a or not b:
            raise ValueError("Ambas matrices deben ser no vacías.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        mb = len(b)
        pb = len(b[0])
        if any(len(row) != pb for row in b):
            raise ValueError("Todas las filas de B deben tener la misma longitud.")
        if m != mb:
            raise ValueError(f"Dimensiones incompatibles: A es {n}x{m} pero B es {mb}x{pb}.")
        # resultado n x p
        res = [[0.0 for _ in range(pb)] for _ in range(n)]
        for i in range(n):
            for j in range(pb):
                s = 0.0
                for k in range(m):
                    s += a[i][k] * b[k][j]
                res[i][j] = s
        return res

    @staticmethod
    def multiply_with_steps(a: List[List[float]], b: List[List[float]]) -> Tuple[List[List[float]], List[str]]:
        """Multiplica dos matrices y devuelve (resultado, pasos) donde pasos es una lista
        de strings describiendo cómo se calculó cada elemento del resultado.
        """
        if not a or not b:
            raise ValueError("Ambas matrices deben ser no vacías.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        mb = len(b)
        pb = len(b[0])
        if any(len(row) != pb for row in b):
            raise ValueError("Todas las filas de B deben tener la misma longitud.")
        if m != mb:
            raise ValueError(f"Dimensiones incompatibles: A es {n}x{m} pero B es {mb}x{pb}.")
        res = [[0.0 for _ in range(pb)] for _ in range(n)]
        pasos: List[str] = []
        pasos.append(f"Multiplicando A ({n}x{m}) por B ({mb}x{pb}):")
        for i in range(n):
            for j in range(pb):
                terms = []
                s = 0.0
                for k in range(m):
                    aij = float(a[i][k])
                    bjk = float(b[k][j])
                    terms.append(f"{format_val(aij)}*{format_val(bjk)}")
                    s += aij * bjk
                res[i][j] = s
                pasos.append(f"C[{i+1},{j+1}] = " + " + ".join(terms) + f" = {format_val(s)}")
        pasos.append("Resultado final:")
        pasos.append(Matrices._mat_to_str(res))
        return res, pasos

    @staticmethod
    def transpose(a: List[List[float]]) -> List[List[float]]:
        """Devuelve la transpuesta de A."""
        if not a:
            return []
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        return [[a[r][c] for r in range(len(a))] for c in range(m)]

    @staticmethod
    def transpose_with_steps(a: List[List[float]]) -> Tuple[List[List[float]], List[str]]:
        """Devuelve la transpuesta y una lista de pasos que muestran cómo se obtuvieron
        los elementos de la transpuesta (mapeo de índices).
        """
        if not a:
            return [], ["Matriz vacía -> transpuesta vacía"]
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        t = [[a[r][c] for r in range(len(a))] for c in range(m)]
        pasos: List[str] = []
        pasos.append(f"Transponiendo matriz {len(a)}x{m}:")
        pasos.append("Matriz original:")
        pasos.append(Matrices._mat_to_str(a))
        pasos.append("Pasos (mapeo de índices):")
        for i in range(len(a)):
            for j in range(m):
                pasos.append(f"T[{j+1},{i+1}] = A[{i+1},{j+1}] = {format_val(a[i][j])}")
        pasos.append("Transpuesta resultante:")
        pasos.append(Matrices._mat_to_str(t))
        return t, pasos

    @staticmethod
    def _get_storage_path() -> str:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_dir = os.path.join(base, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, 'matrices.json')

    @staticmethod
    def load_saved_matrices() -> dict:
        """Carga todas las matrices guardadas desde data/matrices.json -> dict nombre -> matrix"""
        path = Matrices._get_storage_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # validar estructura esperada: dict nombre -> lista de filas
            res = {}
            for k, v in data.items():
                # convertir elementos a float
                res[k] = [[float(x) for x in row] for row in v]
            return res
        except Exception:
            return {}

    @staticmethod
    def save_matrix(name: str, matrix: List[List[float]]):
        """Guarda (o sobrescribe) una matriz con el nombre proporcionado en el archivo JSON."""
        if not name or not isinstance(name, str):
            raise ValueError("El nombre debe ser una cadena no vacía.")
        path = Matrices._get_storage_path()
        cur = Matrices.load_saved_matrices()
        cur[name] = matrix
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cur, f, indent=2)

    @staticmethod
    def delete_saved_matrix(name: str):
        path = Matrices._get_storage_path()
        cur = Matrices.load_saved_matrices()
        if name in cur:
            del cur[name]
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cur, f, indent=2)

    @staticmethod
    def multiply_scalar(a: List[List[float]], scalar: float) -> List[List[float]]:
        """Multiplica cada elemento de la matriz por el escalar dado."""
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de la matriz deben tener la misma longitud.")
        return [[float(x) * float(scalar) for x in row] for row in a]
    
    @staticmethod
    def add(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        """Suma dos matrices A y B del mismo tamaño y devuelve la matriz resultado."""
        if not a or not b:
            raise ValueError("Ambas matrices deben ser no vacías.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        if len(b) != n or any(len(row) != m for row in b):
            raise ValueError(f"Dimensiones incompatibles: A es {n}x{m} pero B tiene forma distinta.")
        return [[float(a[i][j]) + float(b[i][j]) for j in range(m)] for i in range(n)]

    @staticmethod
    def subtract(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        """Resta la matriz B de A (A - B) y devuelve la matriz resultado."""
        if not a or not b:
            raise ValueError("Ambas matrices deben ser no vacías.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de A deben tener la misma longitud.")
        if len(b) != n or any(len(row) != m for row in b):
            raise ValueError(f"Dimensiones incompatibles: A es {n}x{m} pero B tiene forma distinta.")
        return [[float(a[i][j]) - float(b[i][j]) for j in range(m)] for i in range(n)]

    @staticmethod
    def inverse(a: List[List[float]]) -> List[List[float]]:
        """Calcula la inversa de una matriz cuadrada A por reducción por filas.

        Algoritmo: construir la matriz aumentada [A | I] y aplicar operaciones
        elementales de fila simultáneamente a ambas mitades hasta intentar llevar
        A a la identidad. Si al finalizar la reducción la parte izquierda es I, la
        parte derecha será A^{-1}. Si no, A no es invertible.

        Lanza ValueError si la matriz no es cuadrada o no es invertible.
        Devuelve una nueva matriz (lista de listas) con valores float.
        """
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de la matriz deben tener la misma longitud.")
        if n != m:
            raise ValueError("Solo se puede invertir una matriz cuadrada.")

        # crear copia y matriz identidad a la derecha
        # usar floats para cálculos
        aug = [ [float(x) for x in row] + [1.0 if i==j else 0.0 for j in range(n)] for i, row in enumerate(a) ]

        # aplicar Gauss-Jordan sobre [A | I]
        for col in range(n):
            # encontrar pivote (mayor absoluto) para estabilidad
            pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
            if abs(aug[pivot_row][col]) < EPS:
                raise ValueError("La matriz es singular y no tiene inversa.")
            # intercambiar si es necesario
            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
            piv = aug[col][col]
            # normalizar fila del pivote
            if abs(piv - 1.0) > EPS:
                for j in range(2*n):
                    aug[col][j] /= piv
            # eliminar otras filas en la columna actual
            for r in range(n):
                if r == col:
                    continue
                factor = aug[r][col]
                if abs(factor) > EPS:
                    for j in range(2*n):
                        aug[r][j] -= factor * aug[col][j]

        # verificación explícita: la parte izquierda debe ser la identidad
        for i in range(n):
            for j in range(n):
                if i == j:
                    if abs(aug[i][j] - 1.0) > 1e-8:
                        raise ValueError("La matriz no se redujo a la identidad; no es invertible.")
                else:
                    if abs(aug[i][j]) > 1e-8:
                        raise ValueError("La matriz no se redujo a la identidad; no es invertible.")

        # extraer la parte derecha como inversa
        inv = [ [aug[i][n + j] for j in range(n)] for i in range(n) ]
        return inv

    @staticmethod
    def inverse_with_steps(a: List[List[float]]) -> Tuple[List[List[float]], List[str]]:
        """Calcula la inversa de A por reducción por filas y devuelve (inversa, pasos).

        Pasos incluye mensajes de operaciones elementales y estados intermedios
        de la matriz aumentada [A | I]. Lanza ValueError si A no es invertible.
        """
        if not a:
            raise ValueError("La matriz no puede estar vacía.")
        n = len(a)
        m = len(a[0])
        if any(len(row) != m for row in a):
            raise ValueError("Todas las filas de la matriz deben tener la misma longitud.")
        if n != m:
            raise ValueError("Solo se puede invertir una matriz cuadrada.")

        aug = [[float(x) for x in row] + [1.0 if i == j else 0.0 for j in range(n)]
               for i, row in enumerate(a)]
        pasos: List[str] = []
        pasos.append(f"Calculando inversa de matriz {n}x{n} por reducción por filas")
        pasos.append("[Matriz | Matriz reducida] inicial:")
        pasos.append(Matrices._aug_to_str_frac(aug, n))

        pivot_positions: List[Tuple[int, int]] = []
        for col in range(n):
            # pivoteo parcial
            pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
            if abs(aug[pivot_row][col]) < EPS:
                pasos.append(f"No se encontró pivote distinto de 0 en la columna {col+1}. A es singular.")
                raise ValueError("La matriz es singular y no tiene inversa.")
            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
                pasos.append(f"f{col+1} <-> f{pivot_row+1}")
                pasos.append(Matrices._aug_to_str_frac(aug, n))
            piv = aug[col][col]
            pivot_positions.append((col, col))
            if abs(piv - 1.0) > EPS:
                for j in range(2*n):
                    aug[col][j] /= piv
                coef = format_val(1.0/piv)
                pasos.append(f"f{col+1} --> {coef}*f{col+1}")
                pasos.append(Matrices._aug_to_str_frac(aug, n))
            # eliminación en otras filas
            for r in range(n):
                if r == col:
                    continue
                factor = aug[r][col]
                if abs(factor) > EPS:
                    for j in range(2*n):
                        aug[r][j] -= factor * aug[col][j]
                    pasos.append(f"f{r+1} --> f{r+1} - {format_val(abs(factor))}*f{col+1}")
                    pasos.append(Matrices._aug_to_str_frac(aug, n))

        # Verificar parte izquierda == I
        ok = True
        for i in range(n):
            for j in range(n):
                if i == j:
                    if abs(aug[i][j] - 1.0) > 1e-8:
                        ok = False
                        break
                else:
                    if abs(aug[i][j]) > 1e-8:
                        ok = False
                        break
            if not ok:
                break
        if not ok:
            pasos.append("La parte izquierda no se redujo a la identidad; A no es invertible.")
            raise ValueError("La matriz no se redujo a la identidad; no es invertible.")

        inv = [[aug[i][n + j] for j in range(n)] for i in range(n)]
        pasos.append("Parte izquierda reducida a I; extraemos A^{-1} de la derecha:")
        pasos.append(Matrices._mat_to_str_frac(inv))
        
        # Verificaciones finales
        pasos.append("\nVerificaciones de invertibilidad:")
        # 1) Comprobar A * A^{-1} = I
        try:
            prod = Matrices.multiply(a, inv)
            is_I = Matrices._is_identity(prod)
            max_err = 0.0
            for i in range(len(prod)):
                for j in range(len(prod[0])):
                    target = 1.0 if i == j else 0.0
                    max_err = max(max_err, abs(prod[i][j] - target))
            estado = "CUMPLE" if is_I else "NO CUMPLE"
            pasos.append(f"1) A·A^{-1} = I  -> {estado} (error máx: {max_err:.2e})")
            if is_I:
                pasos.append("Producto A·A^{-1} (aprox. identidad):")
                pasos.append(Matrices._mat_to_str_frac(prod))
        except Exception as e:
            pasos.append(f"1) A·A^{-1} = I  -> NO VERIFICADO ({e})")

        # 2) (c) A tiene n posiciones pivote
        pasos.append(f"2) (c) A tiene n posiciones pivote -> {'CUMPLE' if len(pivot_positions)==n else 'NO CUMPLE'}; pivotes: "
                     + ", ".join(f"(f{r+1},c{c+1})" for r,c in pivot_positions))
        # 3) (d) Ax=0 solo tiene la solución trivial (equivalente a invertible)
        pasos.append("3) (d) Ax = 0 solo tiene la solución trivial -> CUMPLE (A es invertible)")
        # 4) (e) Columnas de A son L.I. (equivalente a invertible)
        pasos.append("4) (e) Las columnas de A forman un conjunto L.I. -> CUMPLE (A es invertible)")
        return inv, pasos