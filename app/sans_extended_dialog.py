"""SANS partial cable-factor and protective earthing reviews."""
from PySide6.QtWidgets import QDialog,QVBoxLayout,QFormLayout,QComboBox,QLineEdit,QPushButton,QTextEdit,QMessageBox,QScrollArea,QWidget,QLabel
from calculations.sans_extended_checks import buried_cable_extended,protective_earthing_review

CABLE_FIELDS=(('Area mm2','2.5'),('Cores (2, 3, 4)','3'),('Soil temperature C','25'),('Depth m','0.5'),('Soil resistivity K.m/W','1.2'),('Number of grouped cables','2'))
PROTECTION_FIELDS=(('Supply voltage V','230'),('Design current A','20'),('Corrected ampacity A','25'),('Device rated current A','20'),('Device breaking capacity kA','6'),('Prospective short circuit kA','3'),('Earth-loop impedance ohms (AC)','0.8'),('Device trip threshold A (AC)','100'),('Verified trip time seconds (AC)','0.2'),('Required time seconds (AC, externally verified)','0.4'),('RCD rating mA (0 if not applicable)','30'))

class SANSExtendedDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('SANS 10142-1 Ed 2 - Cable Factors / Protection Review')
        self.resize(800,720)
        layout=QVBoxLayout(self)
        self.mode=QComboBox()
        self.mode.addItems(('Buried cable factors','Protection and earthing review'))
        self.mode.currentIndexChanged.connect(self.configure)
        layout.addWidget(self.mode)
        self.supply=QComboBox()
        self.supply.addItems(('AC','DC'))
        layout.addWidget(self.supply)
        self.installation=QComboBox()
        self.installation.addItems(('direct','pipe'))
        layout.addWidget(self.installation)
        self.spacing=QComboBox()
        self.spacing.addItems(('0','300'))
        layout.addWidget(QLabel('Cable grouping spacing (mm): touching=0 or 300'))
        layout.addWidget(self.spacing)
        self.multi_dc=QComboBox()
        self.multi_dc.addItems(('Single source','Multiple DC sources'))
        layout.addWidget(self.multi_dc)
        scroll=QScrollArea()
        scroll.setWidgetResizable(True)
        body=QWidget()
        self.form=QFormLayout(body)
        scroll.setWidget(body)
        layout.addWidget(scroll)
        self.fields=[]
        run=QPushButton('Calculate partial checks')
        run.clicked.connect(self.calculate)
        layout.addWidget(run)
        self.result=QTextEdit()
        self.result.setReadOnly(True)
        layout.addWidget(self.result)
        self.configure()

    def configure(self,*_):
        while self.form.rowCount():
            self.form.removeRow(0)
        self.fields=[]
        for name,default in (CABLE_FIELDS if self.mode.currentIndex()==0 else PROTECTION_FIELDS):
            entry=QLineEdit(default)
            self.form.addRow(name,entry)
            self.fields.append(entry)
        self.calculate()

    def calculate(self):
        try:
            values=[float(x.text()) for x in self.fields]
            if self.mode.currentIndex()==0:
                area,cores,temp,depth,resistivity,count=values
                if not cores.is_integer() or not count.is_integer():
                    raise ValueError('Cores and cable count must be integers')
                result=buried_cable_extended(area,int(cores),self.installation.currentText(),temp,depth,resistivity,int(count),int(self.spacing.currentText()))
            else:
                voltage,load,ampacity,rating,breaking,fault,loop,threshold,trip,limit,rcd=values
                result=protective_earthing_review(self.supply.currentText(),voltage,load,ampacity,rating,breaking,fault,loop,threshold,trip,limit,rcd if rcd else None,self.multi_dc.currentIndex()==1)
        except (ValueError,OverflowError,ZeroDivisionError) as exc:
            QMessageBox.warning(self,'Invalid input',str(exc))
            return
        lines=[]
        for key,value in result.items():
            if isinstance(value,dict):
                lines.append(key+':')
                lines.extend('  '+name+': '+('PASS' if ok else 'REVIEW') for name,ok in value.items())
            else:
                lines.append(key+': '+str(value))
        self.result.setPlainText('\n'.join(lines))
