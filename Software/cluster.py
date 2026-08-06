import sys
import time
import logging
import math
from dataclasses import dataclass
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLabel, QStatusBar
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush

logging.basicConfig(level=logging.INFO)

# Clasă pentru stocarea parametrilor de care avem nevoie pentru afisare
@dataclass
class ClusterData:
    viteza: float = 0.0 
    turatie: float = 0.0
    curent: float = 0.0 
    tensiune: float = 0.0
    temp_motor: float = 0.0 
    temp_controller: float = 0.0 
    temp_baterie: float = 0.0
    soc: float = 0.0
    soh: float = 0.0
    autonomie: float = 0.0
    acceleratie: float = 0.0
    franare_regen: float = 0.0
    timestamp: str = ""

# Clasă folosită pentru recepționarea și prelucrarea datelor de pe magistrala CAN
class CANWorker(QObject):
    data_received = pyqtSignal(ClusterData)
    error_occurred = pyqtSignal(str)
    connection_status = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.bus = None
        self.data = ClusterData()
      
    # Conectare la modulul CAN pentru recepție
    def start(self):
        self.running = True
        try:
            import can
            self.bus = can.interface.Bus(interface='socketcan', channel='can0', bitrate=500000)
            self.connection_status.emit(True)
            self.read_messages()
        except Exception as e:
            self.connection_status.emit(False)
            self.error_occurred.emit(f"Eroare inițializare CAN: {e}")
            
    # Decodare mesaje CAN în funcție de ID-ul mesajului (0x601, 0x602, 0x502) 
    def read_messages(self):
        timeout_counter = 0
        was_connected = True  
        
        while self.running:
            try:
                msg = self.bus.recv(timeout=1.0)
                
                if msg:
                    if msg.is_error_frame:
                        continue
                        
                    if len(msg.data) >= 8:
                        timeout_counter = 0
                        
                        if not was_connected:
                            self.connection_status.emit(True)
                            was_connected = True
                    
                        d = msg.data
                        if msg.arbitration_id == 0x601:
                            self.data.turatie = float(int.from_bytes(d[0:2], 'big'))
                            self.data.viteza = self.data.turatie * 0.015
                            self.data.temp_motor = float(d[2])
                            self.data.temp_controller = float(d[3])
                            self.data.curent = int.from_bytes(d[4:6], 'big', signed=True) / 10.0
                            self.data.tensiune = int.from_bytes(d[6:8], 'big') / 10.0
                            
                        elif msg.arbitration_id == 0x602:
                            self.data.acceleratie = float(d[4])
                            self.data.franare_regen = float(d[5])
                            
                        elif msg.arbitration_id == 0x502:
                            self.data.temp_baterie = float(d[3])
                            self.data.soc = float(d[4]) / 2.0
                            self.data.autonomie = float(int.from_bytes(d[5:7], 'big'))
                            self.data.soh = float(d[7])
                            
                        self.data.timestamp = datetime.now().strftime("%H:%M:%S")
                        self.data_received.emit(self.data)
                else:
                    timeout_counter += 1
                    
                    if timeout_counter >= 2 and was_connected:
                        was_connected = False
                        self.connection_status.emit(False)
                        self.error_occurred.emit("Eroare: Conexiune CAN pierdută")
                        
            except Exception as e:
                print(f"Eroare în procesarea CAN: {e}")
                if was_connected:
                    was_connected = False
                    self.connection_status.emit(False)
                    self.error_occurred.emit(f"Eroare critică bus CAN: {e}")
                time.sleep(0.1)
   
          
    def stop(self):
        self.running = False
        if self.bus:
            self.bus.shutdown()

# Clasă de bază pentru desenarea cadranelor
# Desenează cercurile pentru cadranul stâng și cel din centru
class BaseDial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 250)
        
    def setup_painter(self, draw_full_circle=True):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy, r = w // 2, h // 2, min(w, h) // 2.2
    
        if draw_full_circle:
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor("#0a0a0a")))
            p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
            p.setPen(QPen(QColor("#333333"), 4))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
            
        return p, w, h, cx, cy, r

# Clasă pentru desenarea cadranului din stânga 
class LeftDisplay(BaseDial):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current = 0.0
        self.time_str = "00:00"
        
    def paintEvent(self, event):
        p, w, h, cx, cy, r = self.setup_painter()
        start_angle, total_span = 210, 240
        
        p.setPen(QPen(QColor("#00ff66"), 4))
        p.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), start_angle * 16, int(-total_span / 6 * 16))

        p.setPen(QPen(QColor("#ffffff"), 2))
        p.setFont(QFont("Arial", 10, QFont.Bold))
        for i in range(7):
            rad = math.radians(start_angle - (i / 6) * total_span)
            cos_a, sin_a = math.cos(rad), math.sin(rad)
            p.drawLine(int(cx + (r - 10) * cos_a), int(cy - (r - 10) * sin_a), int(cx + r * cos_a), int(cy - r * sin_a))
            p.drawText(int(cx + (r - 22) * cos_a - 15), int(cy - (r - 22) * sin_a - 15), 30, 30, Qt.AlignCenter, str(i - 1))
            
        c_rad = math.radians(start_angle - ((max(-100, min(500, self.current)) + 100) / 600.0) * total_span)
        c_cos, c_sin = math.cos(c_rad), math.sin(c_rad)
        
        p.setPen(QPen(QColor("#33bbff"), 3))
        p.drawLine(int(cx + (r - 30) * c_cos), int(cy - (r - 30) * c_sin), int(cx + (r + 5) * c_cos), int(cy - (r + 5) * c_sin))
        
        ir = r * 0.6
        p.setPen(QPen(QColor("#222222"), 2))
        p.drawEllipse(int(cx - ir), int(cy - ir), int(ir * 2), int(ir * 2))
        
        p.setPen(QPen(QColor("#aaaaaa")))
        p.setFont(QFont("Arial", 8, QFont.Bold))
        p.drawText(0, int(cy - 30), w, 20, Qt.AlignCenter, "CURENT")
        p.setPen(QPen(QColor("#ffffff")))
        p.setFont(QFont("Arial", 22, QFont.Bold))
        p.drawText(0, int(cy - 15), w, 40, Qt.AlignCenter, f"{self.current:.1f}")
        p.setFont(QFont("Arial", 9, QFont.Bold))
        p.drawText(0, int(cy + 20), w, 20, Qt.AlignCenter, "AMPERI")
        
        p.setPen(QPen(QColor("#ffffff")))
        p.setFont(QFont("Arial", 9))
        p.drawText(0, int(cy + r + 10), w, 20, Qt.AlignCenter, self.time_str)

# Clasă pentru desenarea cadranului din stânga 
class CenterDisplay(BaseDial):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.speed = 0
        self.rpm = 0.0
        self.ev_range = "-"
        
    def paintEvent(self, event):
        p, w, h, cx, cy, r = self.setup_painter()
        start_angle, total_span = 210, 240
        
        p.setPen(QPen(QColor("#ff1a1a"), 4))
        p.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), int((210 - (7 / 8) * total_span) * 16), int(-total_span / 8 * 16))
        
        p.setFont(QFont("Arial", 11, QFont.Bold))
        for i in range(9):
            rad = math.radians(start_angle - (i / 8) * total_span)
            cos_a, sin_a = math.cos(rad), math.sin(rad)
            p.setPen(QPen(QColor("#ff1a1a" if i >= 8 else "#ffffff"), 2))
            p.drawLine(int(cx + (r - 10) * cos_a), int(cy - (r - 10) * sin_a), int(cx + r * cos_a), int(cy - r * sin_a))
            p.drawText(int(cx + (r - 22) * cos_a - 15), int(cy - (r - 22) * sin_a - 15), 30, 30, Qt.AlignCenter, str(i))
            
        r_rad = math.radians(start_angle - (max(0, min(8, self.rpm)) / 8) * total_span)
        r_cos, r_sin = math.cos(r_rad), math.sin(r_rad)
        
        p.setPen(QPen(QColor("#ffffff"), 3))
        p.drawLine(int(cx + (r - 30) * r_cos), int(cy - (r - 30) * r_sin), int(cx + (r + 5) * r_cos), int(cy - (r + 5) * r_sin))
        
        ir = r * 0.6
        p.setPen(QPen(QColor("#222222"), 2))
        p.drawEllipse(int(cx - ir), int(cy - ir), int(ir * 2), int(ir * 2))
        
        p.setPen(QPen(QColor("#aaaaaa")))
        p.setFont(QFont("Arial", 8, QFont.Bold))
        p.drawText(0, int(cy - 55), w, 20, Qt.AlignCenter, "Viteza motor\nx1000 RPM")
        p.setPen(QPen(QColor("#ffffff")))
        p.setFont(QFont("Arial", 32, QFont.Bold))
        p.drawText(0, int(cy - 20), w, 40, Qt.AlignCenter, str(int(self.speed)))
        p.setFont(QFont("Arial", 10, QFont.Bold))
        p.drawText(0, int(cy + 20), w, 20, Qt.AlignCenter, "km/h")
        
        p.setPen(QPen(QColor("#00ff66")))
        p.setFont(QFont("Arial", 8, QFont.Bold))
        p.drawText(0, int(cy + 70), w, 20, Qt.AlignCenter, "Autonomie")
        p.setPen(QPen(QColor("#ffffff")))
        p.setFont(QFont("Arial", 9, QFont.Bold))
        p.drawText(0, int(cy + 85), w, 20, Qt.AlignCenter, f"{self.ev_range} km")

# Clasă pentru cadranul din dreapta
class RightDisplay(BaseDial):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = ClusterData()
        
    def paintEvent(self, event):
        p, w, h, cx, cy, r = self.setup_painter(draw_full_circle=False)
        
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("#aaaaaa"), 2))
        p.drawArc(int(cx - r), int(cy - r), int(r * 2), int(r * 2), 16 * -120, 16 * 240)
        
        p.setPen(QPen(QColor("#ffffff")))
        p.setFont(QFont("Arial", 8, QFont.Bold))
        p.drawText(0, int(cy - 70), w, 20, Qt.AlignCenter, f"SOC: {self.data.soc:.0f}%  |  SOH: {self.data.soh:.0f}%")
        p.drawText(0, int(cy - 55), w, 20, Qt.AlignCenter, f"Tensiune: {self.data.tensiune:.1f} V")
        
        # Funcție pentru a desena indicatoarele de progres 
        def draw_bar(x, y, bw, bh, pct, color, label, is_vert=False, top_label=False):
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor("#222222")))
            p.drawRect(int(x), int(y), int(bw), int(bh))
            
            fill = max(0, min(pct, 100)) / 100.0
            p.setBrush(QBrush(QColor(color)))
            if is_vert:
                fh = int(bh * fill)
                p.drawRect(int(x), int(y + bh - fh), int(bw), fh)
            else:
                p.drawRect(int(x), int(y), int(bw * fill), int(bh))
                
            p.setPen(QPen(QColor("#ffffff")))
            p.setFont(QFont("Arial", 7, QFont.Bold))
            ly = y - 12 if top_label else y + bh + 2
            p.drawText(int(x - (20 if is_vert else 0)), int(ly), int(bw + (40 if is_vert else 0)), 12, Qt.AlignCenter, label)

        hw, hh, vw, vh, gx, gy = 70, 8, 12, 60, 15, 10
        vy, hx = cy - vh / 2, cx - hw / 2
        
        draw_bar(cx - hw/2 - gx - vw, vy, vw, vh, self.data.temp_motor, "#ff9900", f"MOT {self.data.temp_motor:.0f}°C", True)
        draw_bar(cx + hw/2 + gx, vy, vw, vh, self.data.temp_baterie, "#ff3333", f"BAT {self.data.temp_baterie:.0f}°C", True)
        draw_bar(hx, cy - gy/2 - hh, hw, hh, self.data.acceleratie, "#33bbff", f"ACC {self.data.acceleratie:.0f}%", False, True)
        draw_bar(hx, cy + gy/2, hw, hh, self.data.franare_regen, "#00ff66", f"REG {self.data.franare_regen:.0f}%")
        
        p.setPen(QPen(QColor("#ffffff")))
        p.setFont(QFont("Arial", 8, QFont.Bold))
        p.drawText(0, int(cy + 55), w, 20, Qt.AlignCenter, f"Temp Ctrl: {self.data.temp_controller:.1f} °C")
        
# Clasă pentru fereastra principală a aplicatiei. 
# Aici se apelează cele 3 ceasuri intr-un layout orizontal și se pornește recepția de pe CAN.
class ClusterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cluster")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #050505;")
        
        central_w = QWidget() 
        self.setCentralWidget(central_w)
        
        layout = QHBoxLayout(central_w)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.displays = (LeftDisplay(), CenterDisplay(), RightDisplay())
        for display in self.displays: 
            layout.addWidget(display, 1)
        
        self.status_label = QLabel("Așteptare CAN...")
        self.status_label.setStyleSheet("color: #ffa500; padding: 2px; font-weight: bold; font-size: 10px;")
        self.statusBar().addWidget(self.status_label)
        
        self._setup_can()
        
    
    def _setup_can(self):
        self.thread = QThread()
        self.worker = CANWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.start)
        
        # Apelare funcție de actualizare
        
        self.worker.data_received.connect(self.update_display)
        self.worker.error_occurred.connect(lambda e: self._update_status(f" Eroare: {e}", "#ff0000"))
        self.worker.connection_status.connect(lambda c: self._update_status("CAN Conectat" if c else " Deconectat", "#00ff00" if c else "#ff0000"))
        
        self.thread.start()

    def _update_status(self, msg, color):
        self.status_label.setText(msg)
        self.status_label.setStyleSheet(f"color: {color}; padding: 2px; font-weight: bold; font-size: 10px;")

    # Funcția se execută de fiecare dată când sunt pachete noi pe CAN
    # Se transmit datele către fiecare cadran și se face actualizare la interfața grafică
    def update_display(self, data: ClusterData):
        self.displays[0].current = data.curent
        self.displays[0].time_str = data.timestamp or "00:00"
        self.displays[1].speed = data.viteza
        self.displays[1].rpm = data.turatie / 1000.0
        self.displays[1].ev_range = int(data.autonomie)
        self.displays[2].data = data
        
        for d in self.displays: 
            d.update()
            
    def closeEvent(self, event):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ClusterWindow()
    window.show()
    sys.exit(app.exec_())