import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QTextEdit, QLineEdit, QMessageBox, QSizePolicy, QGridLayout
)
from PyQt6.QtGui import QFont, QPainter, QColor, QIntValidator
from PyQt6.QtCore import Qt, QTimer

from models.Vectores import Vector, solucionMatrizVector, dependencia_lineal_pasos, analizar_sistema_vectores
from fractions import Fraction

class FondoAnimado(QWidget):
    # ...igual que tu código actual...

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_animacion)
        self.timer.start(70)
        self.simbolos = [
            "x", "y", "z", "λ", "μ", "α", "β", "Σ", "∑", "∈", "∉", "∩", "∪", "⊂", "⊆", "⊄", "⊇",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "+", "-", "=", "≠", "≤", "≥", "→", "←", "·", "⋅", "∥", "⊥", "det", "rank", "dim",
            "A", "B", "C", "v", "w", "u", "T", "M", "R", "ℝ", "ℤ", "ℚ", "ℂ"
        ]
        self.formulas = [
            "Ax = b", "det(A)", "rank(A)", "x ∈ ℝⁿ", "v · w", "||v||", "A⁻¹", "ker(T)", "Im(T)", "span{v₁,...,vₙ}",
            "λI - A", "Σvᵢ", "dim(V)", "A·B", "v⊥w", "x = A⁻¹b"
        ]
        self.columns = []
        self.init_columns()

    def resizeEvent(self, event):
        self.init_columns()

    def init_columns(self):
        ancho = self.width()
        alto = self.height()
        font_size = 28
        col_width = font_size + 8
        n_cols = max(1, ancho // col_width)
        self.columns = []
        for i in range(n_cols):
            x = i * col_width
            y = random.randint(-alto, alto)
            speed = random.uniform(2.0, 4.0)
            self.columns.append({
                "x": x,
                "y": y,
                "speed": speed,
                "trail": random.randint(6, 16),
                "chars": [self.random_symbol_or_formula() for _ in range(alto // font_size + 2)]
            })

    def random_symbol_or_formula(self):
        if random.random() < 0.7:
            return random.choice(self.simbolos)
        else:
            return random.choice(self.formulas)

    def actualizar_animacion(self):
        alto = self.height()
        font_size = 28
        for col in self.columns:
            col["y"] += col["speed"]
            if col["y"] > alto + font_size * 2:
                col["y"] = random.randint(-alto // 2, 0)
                col["speed"] = random.uniform(2.0, 4.0)
                col["trail"] = random.randint(6, 16)
                col["chars"] = [self.random_symbol_or_formula() for _ in range(alto // font_size + 2)]
            else:
                for i in range(len(col["chars"])):
                    if random.random() < 0.08:
                        col["chars"][i] = self.random_symbol_or_formula()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        font_size = 28
        painter.setFont(QFont("Consolas", font_size, QFont.Weight.Bold))
        alto = self.height()
        for col in self.columns:
            x = col["x"]
            y = col["y"]
            for i in range(col["trail"]):
                yy = y - i * font_size
                if 0 <= yy < alto:
                    if i == 0:
                        color = QColor(180, 255, 180, 255)
                    else:
                        color = QColor(0, 255, 70, max(40, 180 - i * 18))
                    painter.setPen(color)
                    txt = col["chars"][int(yy // font_size) % len(col["chars"])]
                    painter.drawText(int(x), int(yy), font_size + 10, font_size + 10, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, txt)

class VectoresGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Álgebra Lineal - Operaciones con Vectores')
        self.resize(1200, 800)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.setLayout(self.layout)
        self.fondo = FondoAnimado(self)
        self.fondo.lower()
        self._crear_barra_superior()
        self._crear_grid_vectores()
        self._crear_operaciones()
        self._crear_resultado()
        self.showFullScreen()

    def resizeEvent(self, event):
        if hasattr(self, "fondo"):
            self.fondo.resize(self.size())
        super().resizeEvent(event)

    def _crear_barra_superior(self):
        barra_superior = QHBoxLayout()
        self.btn_home = QPushButton("🏠")
        self.btn_home.setFixedSize(60, 60)
        self.btn_home.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.btn_home.setStyleSheet("""
            QPushButton {
                background: #222;
                color: #b6ffb6;
                border-radius: 30px;
                border: 2px solid #b6ffb6;
            }
            QPushButton:hover {
                background: #333;
                color: #fff;
            }
        """)
        self.btn_home.clicked.connect(self.ir_a_menu)
        barra_superior.addWidget(self.btn_home)
        barra_superior.addSpacing(20)

        # Entradas numéricas para cantidad de vectores, filas y columnas (máximo 10)
        lbl_vec = QLabel("Cantidad de vectores:")
        barra_superior.addWidget(lbl_vec)
        self.input_cant_vectores = QLineEdit()
        self.input_cant_vectores.setValidator(QIntValidator(1, 10, self))
        self.input_cant_vectores.setPlaceholderText("No se admite una cantidad mayor a 10 vectores")
        self.input_cant_vectores.setFixedWidth(220)
        self.input_cant_vectores.setStyleSheet("background: #222; color: #b6ffb6; border-radius: 6px;")
        self.input_cant_vectores.textChanged.connect(self._sincronizar_columnas)
        self.input_cant_vectores.textChanged.connect(self.actualizar_campos_vectores)
        barra_superior.addWidget(self.input_cant_vectores)

        barra_superior.addSpacing(16)

        lbl_filas = QLabel("Filas:")
        barra_superior.addWidget(lbl_filas)
        self.input_filas = QLineEdit()
        self.input_filas.setValidator(QIntValidator(1, 10, self))
        self.input_filas.setPlaceholderText("No se admiten vectores con mas de 10 filas")
        self.input_filas.setFixedWidth(260)
        self.input_filas.setStyleSheet("background: #222; color: #b6ffb6; border-radius: 6px;")
        self.input_filas.textChanged.connect(self.actualizar_campos_vectores)
        barra_superior.addWidget(self.input_filas)

        barra_superior.addSpacing(16)

        # Para mantener la solicitud del usuario, mostramos también "Columnas" y lo sincronizamos con la cantidad de vectores
        lbl_cols = QLabel("Columnas:")
        barra_superior.addWidget(lbl_cols)
        self.input_columnas = QLineEdit()
        self.input_columnas.setValidator(QIntValidator(1, 10, self))
        self.input_columnas.setPlaceholderText("No se admiten vectores con mas de 10 columnas")
        self.input_columnas.setFixedWidth(290)
        self.input_columnas.setStyleSheet("background: #222; color: #b6ffb6; border-radius: 6px;")
        self.input_columnas.textChanged.connect(self._sincronizar_vectores)
        self.input_columnas.textChanged.connect(self.actualizar_campos_vectores)
        barra_superior.addWidget(self.input_columnas)

        # Valores por defecto
        self.input_cant_vectores.setText("2")
        self.input_filas.setText("3")
        self.input_columnas.setText("2")
        self.layout.addLayout(barra_superior)

    def _sincronizar_columnas(self):
        # Mantener sincronizadas columnas con cantidad de vectores
        txt = self.input_cant_vectores.text()
        if txt != self.input_columnas.text():
            self.input_columnas.blockSignals(True)
            self.input_columnas.setText(txt)
            self.input_columnas.blockSignals(False)

    def _sincronizar_vectores(self):
        # Mantener sincronizadas cantidad de vectores con columnas
        txt = self.input_columnas.text()
        if txt != self.input_cant_vectores.text():
            self.input_cant_vectores.blockSignals(True)
            self.input_cant_vectores.setText(txt)
            self.input_cant_vectores.blockSignals(False)

    def _crear_grid_vectores(self):
        self.vectores_grid = QGridLayout()
        self.layout.addLayout(self.vectores_grid)
        self.campos_vectores = []
        self.campos_b = []
        self.actualizar_campos_vectores()

    def _crear_operaciones(self):
        oper_layout = QHBoxLayout()
        oper_layout.addWidget(QLabel('Operación:'))
        self.combo_oper = QComboBox()
        self.combo_oper.addItems([
            'Suma', 'Resta', 'Multiplicación', 'Escalar', 'Eliminar coma y punto',
            'Solución Matriz de Vectores', 'Dependencia/Independencia Lineal'
        ])
        oper_layout.addWidget(self.combo_oper)
        # Checkbox para mostrar/ocultar pasos detallados
        from PyQt6.QtWidgets import QCheckBox
        self.chk_mostrar_pasos = QCheckBox('Mostrar pasos')
        self.chk_mostrar_pasos.setChecked(True)
        self.chk_mostrar_pasos.setStyleSheet("color: #b6ffb6;")
        oper_layout.addWidget(self.chk_mostrar_pasos)
        self.btn_ejecutar = QPushButton('Ejecutar')
        self.btn_ejecutar.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.btn_ejecutar.setStyleSheet("background: #222; color: #b6ffb6; border-radius: 10px;")
        self.btn_ejecutar.clicked.connect(self.ejecutar_operacion)
        oper_layout.addWidget(self.btn_ejecutar)
        self.btn_limpiar = QPushButton('Limpiar')
        self.btn_limpiar.setFont(QFont("Segoe UI", 14))
        self.btn_limpiar.setStyleSheet("background: #333; color: #b6ffb6; border-radius: 10px;")
        self.btn_limpiar.clicked.connect(self.limpiar_campos)
        oper_layout.addWidget(self.btn_limpiar)
        self.layout.addLayout(oper_layout)

    def _crear_resultado(self):
        self.resultado_label = QLabel('Solución paso a paso:')
        self.resultado_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.resultado_label.setStyleSheet("color: #b6ffb6;")
        self.layout.addWidget(self.resultado_label)
        self.resultado_texto = QTextEdit()
        self.resultado_texto.setReadOnly(True)
        self.resultado_texto.setFont(QFont("Consolas", 16))
        self.resultado_texto.setFixedHeight(350)
        self.resultado_texto.setStyleSheet("""
            background: #111;
            color: #b6ffb6;
            border-radius: 12px;
            border: 1px solid #b6ffb6;
        """)
        self.resultado_texto.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.resultado_texto)

    def limpiar_campos(self):
        for fila in self.campos_vectores:
            for campo in fila:
                campo.clear()
        for campo in getattr(self, "campos_b", []):
            campo.clear()
        self.resultado_texto.clear()

    def _parse_number(self, texto: str) -> Fraction:
        t = (texto or "").strip()
        if '/' in t:
            num, den = t.split('/', 1)
            return Fraction(int(num.strip()), int(den.strip()))
        # reemplazar coma decimal por punto si viene así
        t = t.replace(',', '.')
        return Fraction(t)

    def _format_val(self, val) -> str:
        if isinstance(val, Fraction):
            if val.denominator == 1:
                return str(val.numerator)
            return f"{val.numerator}/{val.denominator}"
        try:
            fr = Fraction(val).limit_denominator()
            if fr.denominator == 1:
                return str(fr.numerator)
            return f"{fr.numerator}/{fr.denominator}"
        except Exception:
            return str(val)

    def _procedimiento_suma(self, vectores):
        # vectores: list[list[Fraction]] columnas, todas del mismo tamaño
        n = len(vectores[0]) if vectores else 0
        pasos = []
        for i in range(n):
            terminos = [self._format_val(v[i]) for v in vectores]
            expr = " + ".join(terminos)
            total = sum(v[i] for v in vectores)
            pasos.append(f"x{i+1}: {expr} = {self._format_val(total)}")
        return "\n".join(pasos)

    def _procedimiento_resta(self, vectores):
        n = len(vectores[0]) if vectores else 0
        pasos = []
        for i in range(n):
            if len(vectores) == 1:
                total = vectores[0][i]
                pasos.append(f"x{i+1}: {self._format_val(total)} = {self._format_val(total)}")
                continue
            expr = self._format_val(vectores[0][i])
            total = vectores[0][i]
            for v in vectores[1:]:
                expr += f" - {self._format_val(v[i])}"
                total -= v[i]
            pasos.append(f"x{i+1}: {expr} = {self._format_val(total)}")
        return "\n".join(pasos)

    def _procedimiento_producto(self, vectores):
        n = len(vectores[0]) if vectores else 0
        pasos = []
        for i in range(n):
            expr = " · ".join(self._format_val(v[i]) for v in vectores)
            prod = Fraction(1, 1)
            for v in vectores:
                prod *= v[i]
            pasos.append(f"x{i+1}: {expr} = {self._format_val(prod)}")
        return "\n".join(pasos)

    def _procedimiento_escalar(self, vector, esc):
        n = len(vector)
        pasos = []
        for i in range(n):
            pasos.append(f"x{i+1}: {self._format_val(esc)} · {self._format_val(vector[i])} = {self._format_val(esc * vector[i])}")
        return "\n".join(pasos)

    def actualizar_campos_vectores(self):
        # Evitar ejecución antes de que el grid exista (puede dispararse por textChanged inicial)
        if not hasattr(self, "vectores_grid"):
            return
        for fila in getattr(self, "campos_vectores", []):
            for campo in fila:
                campo.deleteLater()
        for campo in getattr(self, "campos_b", []):
            campo.deleteLater()
        self.campos_vectores = []
        self.campos_b = []
        while self.vectores_grid.count():
            item = self.vectores_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # Leer valores desde inputs (permitir vacío mientras el usuario escribe)
        txt_cant = (self.input_cant_vectores.text() or "").strip()
        txt_filas = (self.input_filas.text() or "").strip()
        if not txt_cant.isdigit() or not txt_filas.isdigit():
            return
        cant = int(txt_cant)
        filas = int(txt_filas)

        # Validaciones y mensajes
        if cant > 10:
            QMessageBox.warning(self, 'Límite', 'No se admite una cantidad mayor a 10 vectores')
            self.input_cant_vectores.setText('10')
            cant = 10
        if filas > 10:
            QMessageBox.warning(self, 'Límite', 'No se admiten vectores con mas de 10 filas')
            self.input_filas.setText('10')
            filas = 10
        # Columnas (sin uso funcional distinto a cantidad de vectores, pero validamos por consistencia)
        txt_cols = (self.input_columnas.text() or "").strip()
        if txt_cols.isdigit() and int(txt_cols) > 10:
            QMessageBox.warning(self, 'Límite', 'No se admiten vectores con mas de 10 columnas')
            self.input_columnas.setText('10')

        # Etiquetas de encabezado
        self.vectores_grid.addWidget(QLabel(""), 0, 0)
        for j in range(cant):
            lbl = QLabel(f"<b>Vector {j+1}</b>")
            lbl.setStyleSheet("color: #b6ffb6;")
            self.vectores_grid.addWidget(lbl, 0, j+1, alignment=Qt.AlignmentFlag.AlignCenter)
        lbl_b = QLabel("<b>b</b>")
        lbl_b.setStyleSheet("color: #b6ffb6;")
        self.vectores_grid.addWidget(lbl_b, 0, cant+1, alignment=Qt.AlignmentFlag.AlignCenter)

        # Campos de ingreso: cada columna es un vector, cada fila una componente
        for i in range(filas):
            lbl = QLabel(f"x{i+1}")
            lbl.setStyleSheet("color: #b6ffb6;")
            self.vectores_grid.addWidget(lbl, i+1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
            fila_campos = []
            for j in range(cant):
                campo = QLineEdit()
                campo.setFixedWidth(80)
                campo.setFont(QFont("Segoe UI", 14))
                campo.setStyleSheet("background: #222; color: #b6ffb6; border-radius: 6px;")
                self.vectores_grid.addWidget(campo, i+1, j+1)
                fila_campos.append(campo)
            self.campos_vectores.append(fila_campos)
            # Campo para término independiente
            campo_b = QLineEdit()
            campo_b.setFixedWidth(80)
            campo_b.setFont(QFont("Segoe UI", 14))
            campo_b.setStyleSheet("background: #222; color: #b6ffb6; border-radius: 6px;")
            self.vectores_grid.addWidget(campo_b, i+1, cant+1)
            self.campos_b.append(campo_b)

    def obtener_vectores_y_b(self):
        filas = len(self.campos_vectores)
        columnas = len(self.campos_vectores[0]) if filas > 0 else 0
        vectores = []
        for j in range(columnas):
            col = []
            for i in range(filas):
                campo = self.campos_vectores[i][j]
                if campo.isEnabled():
                    texto = campo.text()
                    if not texto:
                        raise ValueError(f"Falta un valor en el vector {j+1}, componente {i+1}.")
                    try:
                        col.append(self._parse_number(texto))
                    except ValueError:
                        raise ValueError(f"El valor '{texto}' en el vector {j+1}, componente {i+1} no es numérico.")
            vectores.append(col)
        b = []
        for i in range(filas):
            campo_b = self.campos_b[i]
            if campo_b.isEnabled():
                texto = campo_b.text()
                if not texto:
                    raise ValueError(f"Falta un valor en el término independiente de la ecuación {i+1}.")
                try:
                    b.append(self._parse_number(texto))
                except ValueError:
                    raise ValueError(f"El valor '{texto}' en el término independiente de la ecuación {i+1} no es numérico.")
        return vectores, b

    def ejecutar_operacion(self):
        self.resultado_texto.clear()
        oper = self.combo_oper.currentText()
        try:
            # Validación rápida de que hay un grid creado
            if len(self.campos_vectores) == 0 or len(self.campos_vectores[0]) == 0:
                QMessageBox.warning(self, 'Aviso', 'Por favor, ingresa cantidades numéricas válidas para filas y vectores (máximo 10).')
                return
            if oper == 'Solución Matriz de Vectores':
                vectores, b = self.obtener_vectores_y_b()
                # Armar matriz aumentada para solucionMatrizVector
                matriz_aumentada = [ [vectores[j][i] for j in range(len(vectores))] + [b[i]] for i in range(len(b)) ]
                pasos = solucionMatrizVector(matriz_aumentada)
                self.resultado_texto.setText(pasos)
            elif oper == 'Dependencia/Independencia Lineal':
                vectores, b = self.obtener_vectores_y_b()
                # Mostrar datos de entrada y los pasos de eliminación
                display = []
                display.append("Vectores de entrada:")
                for idx, v in enumerate(vectores):
                    display.append(f"Vector {idx+1}: [" + ", ".join(self._format_val(x) for x in v) + "]")
                display.append("")
                if self.chk_mostrar_pasos.isChecked():
                    display.append("Pasos (reducción por filas):")
                    display.append(dependencia_lineal_pasos(vectores))
                    display.append("")
                # Resumen del sistema con VB/VL y dependencia
                display.append("Resumen del sistema:")
                display.append(analizar_sistema_vectores(vectores, b))
                self.resultado_texto.setText("\n".join(display))
            else:
                vectores, _ = self.obtener_vectores_y_b()
                pasos = ""
                if oper == 'Suma':
                    if not all(len(v) == len(vectores[0]) for v in vectores):
                        raise ValueError("Todos los vectores deben tener el mismo tamaño para la suma.")
                    resultado = Vector(vectores[0])
                    for v in vectores[1:]:
                        resultado = resultado.suma(Vector(v))
                    pasos += "Suma de vectores:\n"
                    for idx, v in enumerate(vectores):
                        pasos += f"Vector {idx+1}: [" + ", ".join(self._format_val(x) for x in v) + "]\n"
                    if self.chk_mostrar_pasos.isChecked():
                        pasos += "\nProcedimiento por componente:\n" + self._procedimiento_suma(vectores) + "\n\n"
                    pasos += "Resultado: " + resultado.mostrar()
                    self.resultado_texto.setText(pasos)
                elif oper == 'Resta':
                    if not all(len(v) == len(vectores[0]) for v in vectores):
                        raise ValueError("Todos los vectores deben tener el mismo tamaño para la resta.")
                    resultado = Vector(vectores[0])
                    for v in vectores[1:]:
                        resultado = resultado.resta(Vector(v))
                    pasos += "Resta de vectores:\n"
                    for idx, v in enumerate(vectores):
                        pasos += f"Vector {idx+1}: [" + ", ".join(self._format_val(x) for x in v) + "]\n"
                    if self.chk_mostrar_pasos.isChecked():
                        pasos += "\nProcedimiento por componente:\n" + self._procedimiento_resta(vectores) + "\n\n"
                    pasos += "Resultado: " + resultado.mostrar()
                    self.resultado_texto.setText(pasos)
                elif oper == 'Multiplicación':
                    if not all(len(v) == len(vectores[0]) for v in vectores):
                        raise ValueError("Todos los vectores deben tener el mismo tamaño para la multiplicación.")
                    resultado = Vector(vectores[0])
                    for v in vectores[1:]:
                        resultado = resultado.multiplicacion(Vector(v))
                    pasos += "Multiplicación componente a componente:\n"
                    for idx, v in enumerate(vectores):
                        pasos += f"Vector {idx+1}: [" + ", ".join(self._format_val(x) for x in v) + "]\n"
                    if self.chk_mostrar_pasos.isChecked():
                        pasos += "\nProcedimiento por componente:\n" + self._procedimiento_producto(vectores) + "\n\n"
                    pasos += "Resultado: " + resultado.mostrar()
                    self.resultado_texto.setText(pasos)
                elif oper == 'Escalar':
                    from PyQt6.QtWidgets import QInputDialog
                    texto, ok = QInputDialog.getText(self, 'Escalar', 'Introduce el escalar (decimal o fracción a/b):', text='1')
                    if not ok:
                        return
                    try:
                        esc = self._parse_number(texto)
                    except Exception:
                        QMessageBox.warning(self, 'Error', f"Escalar inválido: {texto}")
                        return
                    resultado = Vector(vectores[0]).escalar(esc)
                    pasos += "Vector: [" + ", ".join(self._format_val(x) for x in vectores[0]) + "]\n"
                    pasos += f"Escalar: {self._format_val(esc)}\n\n"
                    if self.chk_mostrar_pasos.isChecked():
                        pasos += "Procedimiento por componente:\n" + self._procedimiento_escalar(vectores[0], esc) + "\n\n"
                    pasos += "Resultado: " + resultado.mostrar()
                    self.resultado_texto.setText(pasos)
                elif oper == 'Eliminar coma y punto':
                    # Operar con los textos crudos del primer vector
                    if len(self.campos_vectores) == 0:
                        QMessageBox.warning(self, 'Error', 'No hay datos para procesar.')
                        return
                    crudos = [self.campos_vectores[i][0].text() for i in range(len(self.campos_vectores))]
                    sin_puntuacion = []
                    for t in crudos:
                        s = (t or '').replace(',', '').replace('.', '')
                        if s.strip() == '':
                            QMessageBox.warning(self, 'Error', f"Entrada vacía tras eliminar puntuación: '{t}'")
                            return
                        try:
                            # intentar entero primero
                            sin_puntuacion.append(int(s))
                        except ValueError:
                            try:
                                sin_puntuacion.append(float(s))
                            except ValueError:
                                QMessageBox.warning(self, 'Error', f"Valor inválido tras limpiar: '{s}'")
                                return
                    pasos += "Vector original: [" + ", ".join(crudos) + "]\n"
                    pasos += "Vector sin comas ni puntos: [" + ", ".join(str(x) for x in sin_puntuacion) + "]"
                    self.resultado_texto.setText(pasos)
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e))

    def ir_a_menu(self):
        try:
            from gui.MenuGui import MenuGui
            self.menu = MenuGui()
            self.menu.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir MenuGui:\n{e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VectoresGui()
    window.show()
    sys.exit(app.exec())