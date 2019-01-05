#!/usr/bin/env python
#-*- coding:utf-8 -*-

from python_qt_binding import QtGui
from python_qt_binding.QtCore import QThread, Signal, Qt, pyqtSignal, pyqtSlot
from python_qt_binding import QtCore
from python_qt_binding.QtCore import QObject as object


import sys
import Tester_2
import time, serial, pyqtgraph, math, pylab, numpy

class AppThread(QThread):
    signal_1 = pyqtSignal(str)
    def __init__(self, started, ser):
        QThread.__init__(self)
        self.started = started
        self.ser = ser

    def __del__(self):
        self.wait()

    def _get_data(self, Ser):
        """
        Mediante esta función se recolectan los datos del arduino
        """

        Value = Ser.readline()
        return Value

    def run(self):

        data = numpy.array([])
        while True:
            if self.started==True:
                data = self._get_data(self.ser)
                #data = numpy.append(data, [Value])
                self.signal_1.emit(data)
            else:
                break

class TesterSignals(QtGui.QMainWindow, Tester_2.Ui_MainWindow):
    """
    En esta clase estara la interfaz
    """
    trigger = pyqtSignal(str)
    trigger_1 = pyqtSignal()

    def __init__(self):
        super(self.__class__,self).__init__()
        pyqtgraph.setConfigOption('background', 'w')
        pyqtgraph.setConfigOption('foreground', 'k')
        self.setupUi(self)
        self.pushButton.clicked.connect(self.StartObtainingData)
        self.data = numpy.array([])
        try:
            self.comboBox.setCurrentIndex(1)
            self.comboBox_2.setCurrentIndex(1)
        except ValueError:
            pass
        self.GuiDefault()
        self.plainTextEdit.setPlainText('Inicializando conexion...')

    def GuiDefault(self):
        # Se inicializa la interfaz
        self.graphicsView.plotItem.clear()
        self.graphicsView.plotItem.setLabel('left', text = 'Grados')
        self.graphicsView.plotItem.setLabel('bottom', text = u' # de Datos')
        self.graphicsView.plotItem.setLabel('right', text = u' ')
        self.graphicsView.plotItem.enableAutoRange()
        self.graphicsView.plotItem.setTitle('Codo')
        self.graphicsView_2.plotItem.setTitle(u'Muñeca')
        self.graphicsView_2.plotItem.setLabel('left', text = 'Grados')
        self.graphicsView_2.plotItem.setLabel('bottom', text = u' # de Datos')
        self.graphicsView_2.plotItem.setLabel('right', text = u' ')
        self.graphicsView_2.plotItem.enableAutoRange()
        self.graphicsView.plotItem.showGrid(True, True, 0.2)
        self.graphicsView_2.plotItem.showGrid(True, True, 0.2)
        self.lineEdit.setText(str(0.0))
        self.lineEdit_2.setText(str(0.0))
        self.lineEdit_3.setText(str(0.0))
        self.lineEdit_4.setText(str(0.0))
        self.lineEdit_5.setText(str(0.0))
        self.lineEdit_6.setText(str(0.0))
        self.plainTextEdit.clear()
        self.plainTextEdit.appendPlainText(u'Conexión establecida')

    def UsbPort(self):
        #Determinación del puerto de conexion con la tarjeta de desarrollo
        try:
            PortName = str(self.comboBox.currentText())
            BaudRate = str(self.comboBox_2.currentText())
            Ser = serial.Serial(PortName, int(BaudRate))
            return Ser

        except serial.serialutil.SerialException:
            self.plainTextEdit.appendPlainText('Puerto no disponible')
            Ser = None
            return Ser

    def StartObtainingData(self):
        Ser = self.UsbPort()
        if self.pushButton.isChecked()==True and Ser!=None:
            started = True
            self.get_thread = AppThread(started, Ser)
            self.get_thread.signal_1.connect(self.function)
            # self.trigger.connect(self.get_thread, Signal("function(QString)"), self.function)
            # self.trigger_1.connect(self.get_thread,Signal("finished()")
            self.get_thread.finished.connect(self.done)
            self.get_thread.start()
            self.pushButton_2.clicked.connect(self.get_thread.terminate)
        else:
            started = False
            QtGui.QMessageBox.critical(self, "Puerto no disponible",
                                       "El puerto solicitado no esta disponible",
                                       QtGui.QMessageBox.Ok)
            self.pushButton.setChecked(False)

    def probe(self):
        print 'Conexion establecida'

    def Graphs(self, data):
        x = numpy.arange(len(data))
        y = data
        pen = pyqtgraph.mkPen(color='k', width = 1)
        self.graphicsView.plot(x,y,pen=pen, clear = True)
        pass

    def ShowComunication(self, valor, puerto, frecuencia):
        try:
            self.plainTextEdit.appendPlainText('Obteniendo mensajes...' + '\n' + 'Puerto de comunicacion: ' +puerto + '\n' + 'Frecuencia(hz): ' + str(frecuencia) + '\n' + 'Mensaje recibido:' + '\n' + str(valor))
            self.plainTextEdit.appendPlainText('---')
        except TypeError:
            self.plainTextEdit.appendPlainText('Puerto no disponible')



    def function(self, data):
        self.ShowComunication(data, '/dev/ttyACM0', 9600)
        data = float(data)
        data = data * 360 / (2 * math.pi)
        data = "{0:.2f}".format(data)
        datos = numpy.append(self.data,[float(data)])
        self.data = datos
        max = numpy.max(datos)
        min = numpy.min(datos)
        actual = data
        self.lineEdit.setText(str(max)+ u'°')
        self.lineEdit_3.setText(str(min) + u'°')
        self.lineEdit_4.setText(str(data) + u'°')
        self.Graphs(datos)

    def done(self):
        self.pushButton.setChecked(False)
        self.pushButton_2.setChecked(False)
        QtGui.QMessageBox.information(self, "Finalizado", "Toma de datos finalizada!")
        self.data = numpy.array([])
        self.GuiDefault()

def main():
    app = QtGui.QApplication(sys.argv)
    form = TesterSignals()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
