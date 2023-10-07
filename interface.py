from PySide6.QtCore import QMimeData, Qt
from PySide6.QtWidgets import QLabel, QLineEdit, QWidget, QMainWindow, QPushButton, QHBoxLayout, QTableWidget, \
    QTabWidget, QStatusBar, QTableWidgetItem, QApplication,QMenu
from PySide6.QtGui import QPixmap, QIcon, QCursor, QColor
from sqlite import open_db, close_db, read_block, write_stream, read_stream
import numpy as np
import prop
from threading import Thread
import datetime
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import modules


class Window(QMainWindow):
    def __init__(self):
        # main
        super(Window, self).__init__()
        self.setWindowTitle("S-CO2 Брайтон")
        self.setWindowIcon(QIcon('src/logo.png'))
        self.setFixedSize(1400, 800)
        self.CentralWidget = QWidget()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()

        # central-tab
        self.tab_menu = QTabWidget(parent=self.CentralWidget)
        self.tab_menu.setGeometry(0, 0, 1400, 800)
        self.tab_menu.addTab(self.tab1, "Ввод данных")
        self.tab_menu.addTab(self.tab2, "Расчёт")
        self.tab_menu.addTab(self.tab3, "Оптимизация")
        self.setCentralWidget(self.CentralWidget)
        # status-bar
        self.status_img = QLabel('_')
        self.status_txt = QLabel('Ожидание запуска')
        self.status_time = QLabel('')
        statusbar = QStatusBar()
        statusbar.addWidget(self.status_img)
        statusbar.addWidget(self.status_txt)
        statusbar.addWidget(self.status_time)
        self.setStatusBar(statusbar)
        # tab-1
        self.img_input = QLabel(parent=self.tab1)
        self.img_input.setPixmap(QPixmap('src/S-CO2.png'))
        self.img_input.setGeometry(25, 25, 1000, 700)

        self.reactor_tin_input = QLineEdit(parent=self.tab1)
        self.reactor_tin_input.setGeometry(50+750, 425, 50, 20)
        self.reactor_tin_input.setText('540')
        self.reactor_tin_txt = QLabel('T =', parent=self.tab1)
        self.reactor_tin_txt.setGeometry(30+750, 425, 20, 20)

        self.reactor_tout_input = QLineEdit(parent=self.tab1)
        self.reactor_tout_input.setGeometry(50+750, 560, 50, 20)
        self.reactor_tout_input.setText('400')
        self.reactor_tout_txt = QLabel('T =', parent=self.tab1)
        self.reactor_tout_txt.setGeometry(30+750, 560, 20, 20)

        self.reactor_p_input = QLineEdit(parent=self.tab1)
        self.reactor_p_input.setGeometry(50+865, 350, 50, 20)
        self.reactor_p_input.setText('0.155')
        self.reactor_p_txt = QLabel('P =', parent=self.tab1)
        self.reactor_p_txt.setGeometry(30+865, 350, 20, 20)

        self.reactor_g_input = QLineEdit(parent=self.tab1)
        self.reactor_g_input.setGeometry(50+865, 330, 50, 20)
        self.reactor_g_input.setText('33784')
        self.reactor_g_txt = QLabel('G =', parent=self.tab1)
        self.reactor_g_txt.setGeometry(30+865, 330, 20, 20)

        self.reactor_x_input = QLineEdit(parent=self.tab1)
        self.reactor_x_input.setGeometry(50+865, 310, 50, 20)
        self.reactor_x_input.setText('Pb')
        self.reactor_x_txt = QLabel('X =', parent=self.tab1)
        self.reactor_x_txt.setGeometry(30+865, 310, 20, 20)

        self.reactor_cp_input = QLineEdit(parent=self.tab1)
        self.reactor_cp_input.setGeometry(50+950, 310, 50, 20)
        self.reactor_cp_input.setText('0.148')
        self.reactor_cp_txt = QLabel('cp =', parent=self.tab1)
        self.reactor_cp_txt.setGeometry(30+950, 310, 20, 20)

        self.cooler_tcool_input = QLineEdit(parent=self.tab1)
        self.cooler_tcool_input.setGeometry(175, 145, 50, 20)
        self.cooler_tcool_input.setText('33')
        self.cooler_tcool_txt = QLabel('T =', parent=self.tab1)
        self.cooler_tcool_txt.setGeometry(175-20, 145, 20, 20)

        self.cooler_tcool_in_input = QLineEdit(parent=self.tab1)
        self.cooler_tcool_in_input.setGeometry(55, 200, 50, 20)
        self.cooler_tcool_in_input.setText('15')
        self.cooler_tcool_in_txt = QLabel('T =', parent=self.tab1)
        self.cooler_tcool_in_txt.setGeometry(35, 200, 20, 20)

        self.cooler_pcool_in_input = QLineEdit(parent=self.tab1)
        self.cooler_pcool_in_input.setGeometry(55, 220, 50, 20)
        self.cooler_pcool_in_input.setText('0.15')
        self.cooler_pcool_in_txt = QLabel('P =', parent=self.tab1)
        self.cooler_pcool_in_txt.setGeometry(35, 220, 20, 20)

        self.cooler_fluid_input = QLineEdit(parent=self.tab1)
        self.cooler_fluid_input.setGeometry(55, 240, 50, 20)
        self.cooler_fluid_input.setText('WATER')
        self.cooler_fluid_txt = QLabel('X =', parent=self.tab1)
        self.cooler_fluid_txt.setGeometry(35, 240, 20, 20)

        self.RHE_dt_input = QLineEdit(parent=self.tab1)
        self.RHE_dt_input.setGeometry(725, 490, 50, 20)
        self.RHE_dt_input.setText('10')
        self.RHE_dt_txt = QLabel('ΔT =', parent=self.tab1)
        self.RHE_dt_txt.setGeometry(700, 490, 25, 20)

        self.HTR_dt_input = QLineEdit(parent=self.tab1)
        self.HTR_dt_input.setGeometry(575, 490, 50, 20)
        self.HTR_dt_input.setText('5')
        self.HTR_dt_txt = QLabel('ΔT =', parent=self.tab1)
        self.HTR_dt_txt.setGeometry(550, 490, 25, 20)

        self.LTR_dt_input = QLineEdit(parent=self.tab1)
        self.LTR_dt_input.setGeometry(325, 490, 50, 20)
        self.LTR_dt_input.setText('5')
        self.LTR_dt_txt = QLabel('ΔT =', parent=self.tab1)
        self.LTR_dt_txt.setGeometry(300, 490, 25, 20)

        self.C_dt_input = QLineEdit(parent=self.tab1)
        self.C_dt_input.setGeometry(175, 125, 50, 20)
        self.C_dt_input.setText('5')
        self.C_dt_txt = QLabel('ΔT =', parent=self.tab1)
        self.C_dt_txt.setGeometry(150, 125, 25, 20)

        self.MC_KPD_input = QLineEdit(parent=self.tab1)
        self.MC_KPD_input.setGeometry(150, 300, 50, 20)
        self.MC_KPD_input.setText('0.9')
        self.MC_KPD_txt = QLabel('η =', parent=self.tab1)
        self.MC_KPD_txt.setGeometry(125, 300, 25, 20)

        self.RC_KPD_input = QLineEdit(parent=self.tab1)
        self.RC_KPD_input.setGeometry(400, 300, 50, 20)
        self.RC_KPD_input.setText('0.9')
        self.RC_KPD_txt = QLabel('η =', parent=self.tab1)
        self.RC_KPD_txt.setGeometry(375, 300, 25, 20)

        self.T_KPD_input = QLineEdit(parent=self.tab1)
        self.T_KPD_input.setGeometry(675, 300, 50, 20)
        self.T_KPD_input.setText('0.9')
        self.T_KPD_txt = QLabel('η =', parent=self.tab1)
        self.T_KPD_txt.setGeometry(650, 300, 25, 20)


        self.cycle_pmin_input = QLineEdit(parent=self.tab1)
        self.cycle_pmin_input.setGeometry(1100, 100, 180, 25)
        self.cycle_pmin_input.setText('8')
        self.cycle_pmin_input_txt = QLabel('Минимальное давление:', parent=self.tab1)
        self.cycle_pmin_input_txt.setGeometry(1100, 75, 180, 25)

        self.cycle_pmax_input = QLineEdit(parent=self.tab1)
        self.cycle_pmax_input.setGeometry(1100, 150, 180, 25)
        self.cycle_pmax_input.setText('28')
        self.cycle_pmax_input_txt = QLabel('Максимальное давление:', parent=self.tab1)
        self.cycle_pmax_input_txt.setGeometry(1100, 125, 180, 25)

        self.cycle_xr_input = QLineEdit(parent=self.tab1)
        self.cycle_xr_input.setGeometry(1100, 200, 180, 25)
        self.cycle_xr_input.setText('0.9')
        self.cycle_xr_input_txt = QLabel('Доля рекомпрессии:', parent=self.tab1)
        self.cycle_xr_input_txt.setGeometry(1100, 175, 180, 25)

        self.cycle_x_input = QLineEdit(parent=self.tab1)
        self.cycle_x_input.setGeometry(1100, 250, 180, 25)
        self.cycle_x_input.setText('CO2')
        self.cycle_x_input_txt = QLabel('Теплоноситель:', parent=self.tab1)
        self.cycle_x_input_txt.setGeometry(1100, 225, 180, 25)

        self.cycle_tolerance_input = QLineEdit(parent=self.tab1)
        self.cycle_tolerance_input.setGeometry(1100, 300, 180, 25)
        self.cycle_tolerance_input.setText('10**-4')
        self.cycle_tolerance_input_txt = QLabel('Сходимость по балансу:', parent=self.tab1)
        self.cycle_tolerance_input_txt.setGeometry(1100, 275, 180, 25)

        self.cycle_tolerance_root = QLineEdit(parent=self.tab1)
        self.cycle_tolerance_root.setGeometry(1100, 350, 180, 25)
        self.cycle_tolerance_root.setText('10**-6')
        self.cycle_tolerance_root_txt = QLabel('Точность поиска корней:', parent=self.tab1)
        self.cycle_tolerance_root_txt.setGeometry(1100, 325, 180, 25)

        self.cycle_step_h = QLineEdit(parent=self.tab1)
        self.cycle_step_h.setGeometry(1100, 400, 180, 25)
        self.cycle_step_h.setText('20')
        self.cycle_step_h_txt = QLabel('Шагов в T-Q анализе:', parent=self.tab1)
        self.cycle_step_h_txt.setGeometry(1100, 375, 180, 25)

        self.start_button = QPushButton("го", parent=self.tab1)
        self.start_button.clicked.connect(self.start)
        self.start_button.setGeometry(1100, 550, 180, 25)

        self.stop_button = QPushButton("стоп", parent=self.tab1)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setGeometry(1100, 600, 180, 25)
        # tab-2
        self.img_input = QLabel(parent=self.tab2)
        self.img_input.setPixmap(QPixmap('src/S-CO2.png'))
        self.img_input.setGeometry(25, 25, 1000, 700)

        self.calc_R_IN_T = QLabel('T = ?', parent=self.tab2)
        self.calc_R_IN_P = QLabel('P = ?', parent=self.tab2)
        self.calc_R_IN_G = QLabel('G = ?', parent=self.tab2)
        self.calc_R_IN_T.setGeometry(800, 330+70, 100, 20)
        self.calc_R_IN_P.setGeometry(800, 330+85, 100, 20)
        self.calc_R_IN_G.setGeometry(800, 330+100, 100, 20)

        self.calc_RHE_OUT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_RHE_OUT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_RHE_OUT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_RHE_OUT_T.setGeometry(800, 480+70, 100, 20)
        self.calc_RHE_OUT_P.setGeometry(800, 480+85, 100, 20)
        self.calc_RHE_OUT_G.setGeometry(800, 480+100, 100, 20)

        self.calc_RHE_dT = QLabel('ΔT = ?', parent=self.tab2)
        self.calc_RHE_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_RHE_dT.setGeometry(725, 410+70, 100, 20)
        self.calc_RHE_Q.setGeometry(725, 410+85, 100, 20)

        self.calc_RHE_T_T = QLabel('T = ?', parent=self.tab2)
        self.calc_RHE_T_P = QLabel('P = ?', parent=self.tab2)
        self.calc_RHE_T_G = QLabel('G = ?', parent=self.tab2)
        self.calc_RHE_T_T.setGeometry(650, 330+70, 100, 20)
        self.calc_RHE_T_P.setGeometry(650, 330+85, 100, 20)
        self.calc_RHE_T_G.setGeometry(650, 330+100, 100, 20)

        self.calc_T_N = QLabel('N = ?', parent=self.tab2)
        self.calc_T_N.setGeometry(680, 290, 100, 20)

        self.calc_MC_N = QLabel('N = ?', parent=self.tab2)
        self.calc_MC_N.setGeometry(125, 290, 100, 20)

        self.calc_RC_N = QLabel('N = ?', parent=self.tab2)
        self.calc_RC_N.setGeometry(400, 290, 100, 20)

        self.calc_HTR_RHE_T = QLabel('T = ?', parent=self.tab2)
        self.calc_HTR_RHE_P = QLabel('P = ?', parent=self.tab2)
        self.calc_HTR_RHE_G = QLabel('G = ?', parent=self.tab2)
        self.calc_HTR_RHE_T.setGeometry(650, 410+70, 100, 20)
        self.calc_HTR_RHE_P.setGeometry(650, 410+85, 100, 20)
        self.calc_HTR_RHE_G.setGeometry(650, 410+100, 100, 20)

        self.calc_T_HTR_T = QLabel('T = ?', parent=self.tab2)
        self.calc_T_HTR_P = QLabel('P = ?', parent=self.tab2)
        self.calc_T_HTR_G = QLabel('G = ?', parent=self.tab2)
        self.calc_T_HTR_T.setGeometry(675, 50+70, 100, 20)
        self.calc_T_HTR_P.setGeometry(675, 50+85, 100, 20)
        self.calc_T_HTR_G.setGeometry(675, 50+100, 100, 20)

        self.calc_HTR_dT = QLabel('ΔT = ?', parent=self.tab2)
        self.calc_HTR_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_HTR_dT.setGeometry(550, 550+70, 100, 20)
        self.calc_HTR_Q.setGeometry(550, 550+85, 100, 20)

        self.calc_LTR_dT = QLabel('ΔT = ?', parent=self.tab2)
        self.calc_LTR_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_LTR_dT.setGeometry(300, 550+70, 100, 20)
        self.calc_LTR_Q.setGeometry(300, 550+85, 100, 20)

        self.calc_C_dT = QLabel('ΔT = ?', parent=self.tab2)
        self.calc_C_Q = QLabel('Q = ?', parent=self.tab2)
        self.calc_C_dT.setGeometry(150, 70+70, 100, 20)
        self.calc_C_Q.setGeometry(150, 70+85, 100, 20)

        self.calc_HTR_LTR_T = QLabel('T = ?', parent=self.tab2)
        self.calc_HTR_LTR_P = QLabel('P = ?', parent=self.tab2)
        self.calc_HTR_LTR_G = QLabel('G = ?', parent=self.tab2)
        self.calc_HTR_LTR_T.setGeometry(430, 520+70, 100, 20)
        self.calc_HTR_LTR_P.setGeometry(430, 520+85, 100, 20)
        self.calc_HTR_LTR_G.setGeometry(430, 520+100, 100, 20)

        self.calc_LTR_SPLIT_T = QLabel('T = ?', parent=self.tab2)
        self.calc_LTR_SPLIT_P = QLabel('P = ?', parent=self.tab2)
        self.calc_LTR_SPLIT_G = QLabel('G = ?', parent=self.tab2)
        self.calc_LTR_SPLIT_T.setGeometry(50, 400+70, 100, 20)
        self.calc_LTR_SPLIT_P.setGeometry(50, 400+85, 100, 20)
        self.calc_LTR_SPLIT_G.setGeometry(50, 400+100, 100, 20)

        self.calc_SPLIT_C_T = QLabel('T = ?', parent=self.tab2)
        self.calc_SPLIT_C_P = QLabel('P = ?', parent=self.tab2)
        self.calc_SPLIT_C_G = QLabel('G = ?', parent=self.tab2)
        self.calc_SPLIT_C_T.setGeometry(140, 20+70, 100, 20)
        self.calc_SPLIT_C_P.setGeometry(140, 20+85, 100, 20)
        self.calc_SPLIT_C_G.setGeometry(140, 20+100, 100, 20)

        self.calc_SPLIT_RC_T = QLabel('T = ?', parent=self.tab2)
        self.calc_SPLIT_RC_P = QLabel('P = ?', parent=self.tab2)
        self.calc_SPLIT_RC_G = QLabel('G = ?', parent=self.tab2)
        self.calc_SPLIT_RC_T.setGeometry(375, 20+70, 100, 20)
        self.calc_SPLIT_RC_P.setGeometry(375, 20+85, 100, 20)
        self.calc_SPLIT_RC_G.setGeometry(375, 20+100, 100, 20)

        self.calc_C_MC_T = QLabel('T = ?', parent=self.tab2)
        self.calc_C_MC_P = QLabel('P = ?', parent=self.tab2)
        self.calc_C_MC_G = QLabel('G = ?', parent=self.tab2)
        self.calc_C_MC_T.setGeometry(140, 120+70, 100, 20)
        self.calc_C_MC_P.setGeometry(140, 120+85, 100, 20)
        self.calc_C_MC_G.setGeometry(140, 120+100, 100, 20)

        self.calc_MC_LTR_T = QLabel('T = ?', parent=self.tab2)
        self.calc_MC_LTR_P = QLabel('P = ?', parent=self.tab2)
        self.calc_MC_LTR_G = QLabel('G = ?', parent=self.tab2)
        self.calc_MC_LTR_T.setGeometry(225, 350+70, 100, 20)
        self.calc_MC_LTR_P.setGeometry(225, 350+85, 100, 20)
        self.calc_MC_LTR_G.setGeometry(225, 350+100, 100, 20)

        self.calc_RC_MIX_T = QLabel('T = ?', parent=self.tab2)
        self.calc_RC_MIX_P = QLabel('P = ?', parent=self.tab2)
        self.calc_RC_MIX_G = QLabel('G = ?', parent=self.tab2)
        self.calc_RC_MIX_T.setGeometry(500, 330+70, 100, 20)
        self.calc_RC_MIX_P.setGeometry(500, 330+85, 100, 20)
        self.calc_RC_MIX_G.setGeometry(500, 330+100, 100, 20)

        self.calc_LTR_MIX_T = QLabel('T = ?', parent=self.tab2)
        self.calc_LTR_MIX_P = QLabel('P = ?', parent=self.tab2)
        self.calc_LTR_MIX_G = QLabel('G = ?', parent=self.tab2)
        self.calc_LTR_MIX_T.setGeometry(410, 390+70, 100, 20)
        self.calc_LTR_MIX_P.setGeometry(410, 390+85, 100, 20)
        self.calc_LTR_MIX_G.setGeometry(410, 390+100, 100, 20)

        self.calc_MIX_HTR_T = QLabel('T = ?', parent=self.tab2)
        self.calc_MIX_HTR_P = QLabel('P = ?', parent=self.tab2)
        self.calc_MIX_HTR_G = QLabel('G = ?', parent=self.tab2)
        self.calc_MIX_HTR_T.setGeometry(500, 390+70, 100, 20)
        self.calc_MIX_HTR_P.setGeometry(500, 390+85, 100, 20)
        self.calc_MIX_HTR_G.setGeometry(500, 390+100, 100, 20)


        self.graph_balance = FigureCanvasQTAgg(plt.Figure(dpi=75))
        self.balance_ax = self.graph_balance.figure.subplots()
        self.balance_ax.grid(True)
        self.balance_ax.set_title('Баланс')
        self.balance_ax.set_xlabel('Итерация')
        self.balance_ax.semilogy()
        self.graph_balance.draw()
        self.graph_balance_cont = QWidget(parent=self.tab2)
        graph_balance_lay = QHBoxLayout()
        graph_balance_lay.addWidget(self.graph_balance)
        self.graph_balance_cont.setLayout(graph_balance_lay)
        self.graph_balance_cont.setGeometry(1050, 0, 300, 300)

        self.calc_balance = QLabel('Δ = ?', parent=self.tab2)
        self.calc_balance.setGeometry(1100, 290, 200, 25)

        self.kpd_output_text = QLabel('η =', parent=self.tab2)
        self.kpd_output_text.setGeometry(1080, 500, 25, 25)
        self.kpd_output = QLineEdit(parent=self.tab2)
        self.kpd_output.setGeometry(1100, 500, 180, 25)
        self.kpd_output.setText(' ')

        self.start_button = QPushButton("го", parent=self.tab2)
        self.start_button.clicked.connect(self.start)
        self.start_button.setGeometry(1100, 550, 180, 25)

        self.stop_button = QPushButton("стоп", parent=self.tab2)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setGeometry(1100, 600, 180, 25)


        # ###############tab-3############### #
        self.opt_pkmin_txt = QLabel('Начальное Pк:', parent=self.tab3)
        self.opt_pkmin_txt.setGeometry(300, 75 + 100, 180, 25)
        self.opt_pkmin = QLineEdit(parent=self.tab3)
        self.opt_pkmin.setGeometry(300, 100 + 100, 180, 25)
        self.opt_pkmin.setText('8')

        self.opt_pkmax_txt = QLabel('Конечное Pк:', parent=self.tab3)
        self.opt_pkmax_txt.setGeometry(300, 125 + 100, 180, 25)
        self.opt_pkmax = QLineEdit(parent=self.tab3)
        self.opt_pkmax.setGeometry(300, 150 + 100, 180, 25)
        self.opt_pkmax.setText('10')

        self.opt_pkstep_txt = QLabel('Шаг изменения Pк:', parent=self.tab3)
        self.opt_pkstep_txt.setGeometry(300, 175 + 100, 180, 25)
        self.opt_pkstep = QLineEdit(parent=self.tab3)
        self.opt_pkstep.setGeometry(300, 200 + 100, 180, 25)
        self.opt_pkstep.setText('0.1')

        self.opt_p0min_txt = QLabel('Начальное P0:', parent=self.tab3)
        self.opt_p0min_txt.setGeometry(50, 75 + 100, 180, 25)
        self.opt_p0min = QLineEdit(parent=self.tab3)
        self.opt_p0min.setGeometry(50, 100 + 100, 180, 25)
        self.opt_p0min.setText('20')

        self.opt_p0max_txt = QLabel('Конечное P0:', parent=self.tab3)
        self.opt_p0max_txt.setGeometry(50, 125 + 100, 180, 25)
        self.opt_p0max = QLineEdit(parent=self.tab3)
        self.opt_p0max.setGeometry(50, 150 + 100, 180, 25)
        self.opt_p0max.setText('30')

        self.opt_p0step_txt = QLabel('Шаг изменения P0:', parent=self.tab3)
        self.opt_p0step_txt.setGeometry(50, 175 + 100, 180, 25)
        self.opt_p0step = QLineEdit(parent=self.tab3)
        self.opt_p0step.setGeometry(50, 200 + 100, 180, 25)
        self.opt_p0step.setText('1')

        self.opt_xmin_txt = QLabel('Начальное x:', parent=self.tab3)
        self.opt_xmin_txt.setGeometry(600, 75 + 100, 180, 25)
        self.opt_xmin = QLineEdit(parent=self.tab3)
        self.opt_xmin.setGeometry(600, 100 + 100, 180, 25)
        self.opt_xmin.setText('0.5')

        self.opt_xmax_txt = QLabel('Конечное x:', parent=self.tab3)
        self.opt_xmax_txt.setGeometry(600, 125 + 100, 180, 25)
        self.opt_xmax = QLineEdit(parent=self.tab3)
        self.opt_xmax.setGeometry(600, 150 + 100, 180, 25)
        self.opt_xmax.setText('1')

        self.opt_xstep_txt = QLabel('Шаг изменения x:', parent=self.tab3)
        self.opt_xstep_txt.setGeometry(600, 175 + 100, 180, 25)
        self.opt_xstep = QLineEdit(parent=self.tab3)
        self.opt_xstep.setGeometry(600, 200 + 100, 180, 25)
        self.opt_xstep.setText('0.05')


        self.start_optimus_button = QPushButton("го", parent=self.tab3)
        self.start_optimus_button.clicked.connect(self.optimus_start)
        self.start_optimus_button.setGeometry(60, 350, 175, 25)

        self.stop_optimus_button = QPushButton("стоп", parent=self.tab3)
        self.stop_optimus_button.clicked.connect(self.stop)
        self.stop_optimus_button.setGeometry(60, 400, 175, 25)

        self.skip_optimus_button = QPushButton("Пропуск итерации", parent=self.tab3)
        self.skip_optimus_button.clicked.connect(self.skip_iter)
        self.skip_optimus_button.setGeometry(60, 450, 175, 25)

        self.optimus_table = QTableWidget(parent=self.tab3)
        self.optimus_table.setGeometry(900, 50, 415, 400)
        self.optimus_table.setColumnCount(7)
        self.optimus_table.setRowCount(15)
        self.optimus_table.setHorizontalHeaderLabels(["P0", "Pk", "x", "dT RHE", "dT HTR", "dT LTR", "KPD"])
        self.optimus_table.setColumnWidth(0, 50)
        self.optimus_table.setColumnWidth(1, 50)
        self.optimus_table.setColumnWidth(2, 50)
        self.optimus_table.setColumnWidth(3, 50)
        self.optimus_table.setColumnWidth(4, 50)
        self.optimus_table.setColumnWidth(5, 50)
        self.optimus_table.setColumnWidth(6, 50)
        self.optimus_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.optimus_table.customContextMenuRequested.connect(self.contextMenuev)
        # ###############tab-5-end############### #

    def skip_iter(self):
        print('skip')
        self.opt_iter_Flag = False

    def contextMenuev(self, pos):
        context_menu = QMenu(self)
        action1 = context_menu.addAction("Копировать")
        action1.triggered.connect(self.context_menu_copy)
        context_menu.exec(QCursor.pos())

    def context_menu_copy(self):
        html = '<table><tbody>'
        selectedItems = self.optimus_table.selectedItems()
        if selectedItems != []:
            column_list = []
            for item in selectedItems:
                column_list.append(item.column())
            items = [item.text() for item in self.optimus_table.selectedItems()]
            for j in range(int(len(items) / (max(column_list) - min(column_list) + 1))):
                html += '<tr>'
                x = max(column_list) - min(column_list) + 1
                for k in range(x):
                    html += '<td>%s</td>' % items[x * j + k]
                html += '</tr>'
        html += '</tbody></table>'
        mime = QMimeData()
        mime.setHtml(html)
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(mime)

    def optimus_start(self):
        print('start opt')
        self.balance_ax.clear()
        self.balance_ax.set_title('Баланс')
        self.balance_ax.set_xlabel('Итерация')
        self.balance_ax.semilogy()

        self.balance_ax.grid(True)
        self.balance_cumm = []
        self.balance_ax.plot(self.balance_cumm)
        self.balance_ax.set_ylim([float(eval(self.cycle_tolerance_input.text())) / 10, 1])
        self.balance_ax.axhline(float(eval(self.cycle_tolerance_input.text())), color='red', linestyle='--')

        self.graph_balance.draw()
        self.graph_balance.flush_events()

        self.status_img.setText('⏳')
        self.status_txt.setText('Запущен расчёт')
        self.kpd_output.setText(" ")
        self.time_flag = True
        self.time_start = datetime.datetime.now()
        self.calc_Flag = True
        self.opt_iter_Flag = True
        self.thread_calc = Thread(target=self.calc_optimus)
        self.thread_calc.start()
        self.thread_timer = Thread(target=self.timer)
        self.thread_timer.start()

    def calc_optimus(self):
        Tin_hot = float(self.reactor_tin_input.text())
        Tout_hot = float(self.reactor_tout_input.text())
        P_hot = float(self.reactor_p_input.text())
        fluid_hot = self.reactor_x_input.text()
        cp_hot = float(self.reactor_cp_input.text())
        G_hot = float(self.reactor_g_input.text())
        fluid = self.cycle_x_input.text()
        h_steps = float(self.cycle_step_h.text())
        fluid_cond = self.cooler_fluid_input.text()
        Tcond = float(self.cooler_tcool_input.text())
        Tfcond = float(self.cooler_tcool_in_input.text())
        Pcond = float(self.cooler_pcool_in_input.text())
        dt_RHE = float(self.RHE_dt_input.text())
        dt_C = float(self.C_dt_input.text())
        dt_HTR = float(self.HTR_dt_input.text())
        dt_LTR = float(self.LTR_dt_input.text())
        KPD_T = float(self.T_KPD_input.text())
        KPD_MC = float(self.MC_KPD_input.text())
        KPD_RC = float(self.RC_KPD_input.text())
        cycle_tolerance = float(eval(self.cycle_tolerance_input.text()))
        root_tolerance = float(eval(self.cycle_tolerance_root.text()))
        tolerance_exp = abs(int(np.log10(cycle_tolerance)))

        P0min = float(self.opt_p0min.text())
        P0max =float(self.opt_p0max.text())
        P0step =float(self.opt_p0step.text())

        Pkmin = float(self.opt_pkmin.text())
        Pkmax = float(self.opt_pkmax.text())
        Pkstep =float(self.opt_pkstep.text())

        xrmin = float(self.opt_xmin.text())
        xrmax = float(self.opt_xmax.text())
        xrstep =float(self.opt_xstep.text())



        i = 0
        for P in np.arange(P0min,P0max,P0step):
            for p_out in np.arange(Pkmin,Pkmax,Pkstep):
                for x in np.arange(xrmin,xrmax,xrstep):
                    self.optimus_table.insertRow(i)
                    self.optimus_table.setItem(i, 0, QTableWidgetItem(str(round(P,5))))
                    self.optimus_table.setItem(i, 1, QTableWidgetItem(str(round(p_out, 5))))
                    self.optimus_table.setItem(i, 2, QTableWidgetItem(str(round(x,5))))
                    self.optimus_table.setItem(i, 3, QTableWidgetItem(' '))
                    self.optimus_table.setItem(i, 4, QTableWidgetItem(' '))
                    self.optimus_table.setItem(i, 5, QTableWidgetItem(' '))
                    self.optimus_table.setItem(i, 6, QTableWidgetItem(' '))
                    i = i + 1

        i = 0
        for P in np.arange(P0min,P0max,P0step):
            for p_out in np.arange(Pkmin,Pkmax,Pkstep):
                for x in np.arange(xrmin,xrmax,xrstep):

                    if i > 0:
                        self.optimus_table.item(i - 1, 0).setBackground(QColor(255, 255, 255))
                        self.optimus_table.item(i - 1, 1).setBackground(QColor(255, 255, 255))
                        self.optimus_table.item(i - 1, 2).setBackground(QColor(255, 255, 255))
                        self.optimus_table.item(i - 1, 3).setBackground(QColor(255, 255, 255))
                        self.optimus_table.item(i - 1, 4).setBackground(QColor(255, 255, 255))
                        self.optimus_table.item(i - 1, 5).setBackground(QColor(255, 255, 255))
                        self.optimus_table.item(i - 1, 6).setBackground(QColor(255, 255, 255))

                    self.optimus_table.item(i, 0).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 1).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 2).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 3).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 4).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 5).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 6).setBackground(QColor(0, 204, 102))

                    open_db()
                    write_stream('R-RHE', Tin_hot, P_hot, Tin_hot * cp_hot, 0, 0, G_hot, fluid_hot)
                    write_stream('HTR-RHE', Tout_hot - dt_RHE, P, prop.t_p(Tout_hot - dt_RHE, P, fluid)['H'],
                                 prop.t_p(Tout_hot - dt_RHE, P, fluid)['S'], prop.t_p(Tout_hot - dt_RHE, P, fluid)['Q'], 1000,
                                 fluid)

                    RHE = modules.RHE('R-RHE', 'RHE-R', 'HTR-RHE', 'RHE-T', Tout_hot, dt_RHE, root_tolerance, h_steps)
                    HTR = modules.HTR('T-HTR', 'HTR-LTR', 'MIX-HTR', 'HTR-RHE', dt_HTR, root_tolerance, h_steps, dt_RHE)
                    LTR = modules.LTR('HTR-LTR', 'LTR-SPLIT', 'MC-LTR', 'LTR-MIX', dt_LTR, root_tolerance, h_steps)
                    MC = modules.MC('C-MC', 'MC-LTR', P, KPD_MC)
                    RC = modules.RC('SPLIT-RC', 'RC-MIX', P, KPD_RC)
                    T = modules.Turb('RHE-T', 'T-HTR', p_out, KPD_T)
                    C = modules.C('SPLIT-C', 'C-MC', 'IN-C', 'C-OUT', Tcond, dt_C, root_tolerance, h_steps)
                    MIX = modules.MIX('LTR-MIX', 'RC-MIX', 'MIX-HTR')
                    SPLIT = modules.SPLIT('LTR-SPLIT', 'SPLIT-C', 'SPLIT-RC', x)

                    for j in range(9999):
                        if self.calc_Flag is False:
                            self.time_flag = False
                            self.status_img.setText('🛑')
                            self.status_txt.setText('Расчёт остановлен')
                            break

                        self.calc_R_IN_T.setText(f'T = {round(float(read_stream("R-RHE")["T"]), tolerance_exp)}')
                        self.calc_R_IN_P.setText(f'P = {round(float(read_stream("R-RHE")["P"]), tolerance_exp)}')
                        self.calc_R_IN_G.setText(f'G = {round(float(read_stream("R-RHE")["G"]), tolerance_exp)}')
                        self.calc_HTR_RHE_T.setText(f'T = {round(float(read_stream("HTR-RHE")["T"]), tolerance_exp)}')
                        self.calc_HTR_RHE_P.setText(f'P = {round(float(read_stream("HTR-RHE")["P"]), tolerance_exp)}')
                        self.calc_HTR_RHE_G.setText(f'G = {round(float(read_stream("HTR-RHE")["G"]), tolerance_exp)}')

                        RHE.calc()

                        self.calc_RHE_OUT_T.setText(f'T = {round(float(read_stream("RHE-R")["T"]), tolerance_exp)}')
                        self.calc_RHE_OUT_P.setText(f'P = {round(float(read_stream("RHE-R")["P"]), tolerance_exp)}')
                        self.calc_RHE_OUT_G.setText(f'G = {round(float(read_stream("RHE-R")["G"]), tolerance_exp)}')
                        self.calc_RHE_T_T.setText(f'T = {round(float(read_stream("RHE-T")["T"]), tolerance_exp)}')
                        self.calc_RHE_T_P.setText(f'P = {round(float(read_stream("RHE-T")["P"]), tolerance_exp)}')
                        self.calc_RHE_T_G.setText(f'G = {round(float(read_stream("RHE-T")["G"]), tolerance_exp)}')

                        self.calc_RHE_Q.setText(f'Q = {round(float(read_block("RHE")["Q"]), tolerance_exp)}')
                        self.calc_RHE_dT.setText(f'ΔT = {round(float(read_block("RHE")["DT"]), tolerance_exp)}')

                        T.calc()

                        self.calc_T_HTR_T.setText(f'T = {round(float(read_stream("T-HTR")["T"]), tolerance_exp)}')
                        self.calc_T_HTR_P.setText(f'P = {round(float(read_stream("T-HTR")["P"]), tolerance_exp)}')
                        self.calc_T_HTR_G.setText(f'G = {round(float(read_stream("T-HTR")["G"]), tolerance_exp)}')
                        self.calc_T_N.setText(f'N = {round(float(read_block("T")["Q"]), tolerance_exp)}')

                        if j == 0:
                            write_stream('HTR-LTR', read_stream('T-HTR')['T'], read_stream('T-HTR')['P'], read_stream('T-HTR')['H'],
                                         read_stream('T-HTR')['S'], read_stream('T-HTR')['Q'], read_stream('T-HTR')['G'],
                                         read_stream('T-HTR')['X'])

                            self.calc_HTR_LTR_T.setText(f'T = {round(float(read_stream("HTR-LTR")["T"]), tolerance_exp)}')
                            self.calc_HTR_LTR_P.setText(f'P = {round(float(read_stream("HTR-LTR")["P"]), tolerance_exp)}')
                            self.calc_HTR_LTR_G.setText(f'G = {round(float(read_stream("HTR-LTR")["G"]), tolerance_exp)}')

                            write_stream('LTR-SPLIT', read_stream('T-HTR')['T'], read_stream('T-HTR')['P'],
                                         read_stream('T-HTR')['H'], read_stream('T-HTR')['S'], read_stream('T-HTR')['Q'],
                                         read_stream('T-HTR')['G'], read_stream('T-HTR')['X'])

                            self.calc_LTR_SPLIT_T.setText(f'T = {round(float(read_stream("LTR-SPLIT")["T"]), tolerance_exp)}')
                            self.calc_LTR_SPLIT_P.setText(f'P = {round(float(read_stream("LTR-SPLIT")["P"]), tolerance_exp)}')
                            self.calc_LTR_SPLIT_G.setText(f'G = {round(float(read_stream("LTR-SPLIT")["G"]), tolerance_exp)}')
                            self.calc_LTR_Q.setText(f'Q = 0')
                            self.calc_LTR_dT.setText(f'ΔT = 0')
                            self.calc_HTR_Q.setText(f'Q = 0')
                            self.calc_HTR_dT.setText(f'ΔT = 0')

                        else:
                            HTR.calc()

                            self.calc_HTR_LTR_T.setText(f'T = {round(float(read_stream("HTR-LTR")["T"]), tolerance_exp)}')
                            self.calc_HTR_LTR_P.setText(f'P = {round(float(read_stream("HTR-LTR")["P"]), tolerance_exp)}')
                            self.calc_HTR_LTR_G.setText(f'G = {round(float(read_stream("HTR-LTR")["G"]), tolerance_exp)}')
                            self.calc_HTR_RHE_T.setText(f'T = {round(float(read_stream("HTR-RHE")["T"]), tolerance_exp)}')
                            self.calc_HTR_RHE_P.setText(f'P = {round(float(read_stream("HTR-RHE")["P"]), tolerance_exp)}')
                            self.calc_HTR_RHE_G.setText(f'G = {round(float(read_stream("HTR-RHE")["G"]), tolerance_exp)}')
                            self.calc_HTR_Q.setText(f'Q = {round(float(read_block("HTR")["Q"]), tolerance_exp)}')
                            self.calc_HTR_dT.setText(f'ΔT = {round(float(read_block("HTR")["DT"]), tolerance_exp)}')

                            LTR.calc()

                            self.calc_LTR_SPLIT_T.setText(f'T = {round(float(read_stream("LTR-SPLIT")["T"]), tolerance_exp)}')
                            self.calc_LTR_SPLIT_P.setText(f'P = {round(float(read_stream("LTR-SPLIT")["P"]), tolerance_exp)}')
                            self.calc_LTR_SPLIT_G.setText(f'G = {round(float(read_stream("LTR-SPLIT")["G"]), tolerance_exp)}')
                            self.calc_LTR_MIX_T.setText(f'T = {round(float(read_stream("LTR-MIX")["T"]), tolerance_exp)}')
                            self.calc_LTR_MIX_P.setText(f'P = {round(float(read_stream("LTR-MIX")["P"]), tolerance_exp)}')
                            self.calc_LTR_MIX_G.setText(f'G = {round(float(read_stream("LTR-MIX")["G"]), tolerance_exp)}')
                            self.calc_LTR_Q.setText(f'Q = {round(float(read_block("LTR")["Q"]), tolerance_exp)}')
                            self.calc_LTR_dT.setText(f'ΔT = {round(float(read_block("LTR")["DT"]), tolerance_exp)}')

                        SPLIT.calc()

                        self.calc_SPLIT_C_T.setText(f'T = {round(float(read_stream("SPLIT-C")["T"]), tolerance_exp)}')
                        self.calc_SPLIT_C_P.setText(f'P = {round(float(read_stream("SPLIT-C")["P"]), tolerance_exp)}')
                        self.calc_SPLIT_C_G.setText(f'G = {round(float(read_stream("SPLIT-C")["G"]), tolerance_exp)}')
                        self.calc_SPLIT_RC_T.setText(f'T = {round(float(read_stream("SPLIT-RC")["T"]), tolerance_exp)}')
                        self.calc_SPLIT_RC_P.setText(f'P = {round(float(read_stream("SPLIT-RC")["P"]), tolerance_exp)}')
                        self.calc_SPLIT_RC_G.setText(f'G = {round(float(read_stream("SPLIT-RC")["G"]), tolerance_exp)}')

                        write_stream('IN-C', Tcond, Pcond, prop.t_p(Tfcond, Pcond, fluid_cond)['H'],
                                     prop.t_p(Tfcond, Pcond, fluid_cond)['S'], 0, 1000, fluid_cond)
                        #не вывожу холодный

                        C.calc()

                        self.calc_C_MC_T.setText(f'T = {round(float(read_stream("C-MC")["T"]), tolerance_exp)}')
                        self.calc_C_MC_P.setText(f'P = {round(float(read_stream("C-MC")["P"]), tolerance_exp)}')
                        self.calc_C_MC_G.setText(f'G = {round(float(read_stream("C-MC")["G"]), tolerance_exp)}')
                        self.calc_C_Q.setText(f'Q = {round(float(read_block("C")["Q"]), tolerance_exp)}')
                        self.calc_C_dT.setText(f'ΔT = {round(float(read_block("C")["DT"]), tolerance_exp)}')

                        MC.calc()

                        self.calc_MC_LTR_T.setText(f'T = {round(float(read_stream("MC-LTR")["T"]), tolerance_exp)}')
                        self.calc_MC_LTR_P.setText(f'P = {round(float(read_stream("MC-LTR")["P"]), tolerance_exp)}')
                        self.calc_MC_LTR_G.setText(f'G = {round(float(read_stream("MC-LTR")["G"]), tolerance_exp)}')
                        self.calc_MC_N.setText(f'N = {round(float(read_block("MC")["Q"]), tolerance_exp)}')

                        RC.calc()

                        self.calc_RC_MIX_T.setText(f'T = {round(float(read_stream("RC-MIX")["T"]), tolerance_exp)}')
                        self.calc_RC_MIX_P.setText(f'P = {round(float(read_stream("RC-MIX")["P"]), tolerance_exp)}')
                        self.calc_RC_MIX_G.setText(f'G = {round(float(read_stream("RC-MIX")["G"]), tolerance_exp)}')
                        self.calc_RC_N.setText(f'N = {round(float(read_block("RC")["Q"]), tolerance_exp)}')

                        LTR.calc()
                        self.calc_LTR_SPLIT_T.setText(f'T = {round(float(read_stream("LTR-SPLIT")["T"]), tolerance_exp)}')
                        self.calc_LTR_SPLIT_P.setText(f'P = {round(float(read_stream("LTR-SPLIT")["P"]), tolerance_exp)}')
                        self.calc_LTR_SPLIT_G.setText(f'G = {round(float(read_stream("LTR-SPLIT")["G"]), tolerance_exp)}')
                        self.calc_LTR_MIX_T.setText(f'T = {round(float(read_stream("LTR-MIX")["T"]), tolerance_exp)}')
                        self.calc_LTR_MIX_P.setText(f'P = {round(float(read_stream("LTR-MIX")["P"]), tolerance_exp)}')
                        self.calc_LTR_MIX_G.setText(f'G = {round(float(read_stream("LTR-MIX")["G"]), tolerance_exp)}')
                        self.calc_LTR_Q.setText(f'Q = {round(float(read_block("LTR")["Q"]), tolerance_exp)}')
                        self.calc_LTR_dT.setText(f'ΔT = {round(float(read_block("LTR")["DT"]), tolerance_exp)}')

                        MIX.calc()
                        self.calc_MIX_HTR_T.setText(f'T = {round(float(read_stream("MIX-HTR")["T"]), tolerance_exp)}')
                        self.calc_MIX_HTR_P.setText(f'P = {round(float(read_stream("MIX-HTR")["P"]), tolerance_exp)}')
                        self.calc_MIX_HTR_G.setText(f'G = {round(float(read_stream("MIX-HTR")["G"]), tolerance_exp)}')

                        HTR.calc()
                        self.calc_HTR_LTR_T.setText(f'T = {round(float(read_stream("HTR-LTR")["T"]), tolerance_exp)}')
                        self.calc_HTR_LTR_P.setText(f'P = {round(float(read_stream("HTR-LTR")["P"]), tolerance_exp)}')
                        self.calc_HTR_LTR_G.setText(f'G = {round(float(read_stream("HTR-LTR")["G"]), tolerance_exp)}')
                        self.calc_HTR_RHE_T.setText(f'T = {round(float(read_stream("HTR-RHE")["T"]), tolerance_exp)}')
                        self.calc_HTR_RHE_P.setText(f'P = {round(float(read_stream("HTR-RHE")["P"]), tolerance_exp)}')
                        self.calc_HTR_RHE_G.setText(f'G = {round(float(read_stream("HTR-RHE")["G"]), tolerance_exp)}')
                        self.calc_HTR_Q.setText(f'Q = {round(float(read_block("HTR")["Q"]), tolerance_exp)}')
                        self.calc_HTR_dT.setText(f'ΔT = {round(float(read_block("HTR")["DT"]), tolerance_exp)}')

                        balance = abs(
                            read_block('RHE')["Q"] + read_block('MC')["Q"] + read_block('RC')["Q"] - read_block('T')["Q"] -
                            read_block('C')["Q"]) / read_block('RHE')["Q"]

                        self.calc_balance.setText(f"Δ = {balance}")
                        self.balance_cumm.append(balance)
                        self.balance_ax.clear()
                        self.balance_ax.set_title('Баланс')
                        self.balance_ax.set_xlabel('Итерация')
                        self.balance_ax.semilogy()
                        self.balance_ax.set_ylim([cycle_tolerance/10,1])
                        self.balance_ax.axhline(cycle_tolerance, color='red', linestyle='--')
                        self.balance_ax.plot(self.balance_cumm)
                        self.balance_ax.grid(True)
                        self.graph_balance.draw()
                        self.graph_balance.flush_events()

                        if balance < cycle_tolerance:
                            break

                    if self.opt_iter_Flag is False:
                        self.kpd_output.setText("Итерация пропущена")
                        self.optimus_table.setItem(i, 2, QTableWidgetItem(str('-')))
                        self.optimus_table.setItem(i, 3, QTableWidgetItem(str('-')))
                        self.optimus_table.setItem(i, 4, QTableWidgetItem(str('-')))
                        self.optimus_table.setItem(i, 5, QTableWidgetItem(str('-')))
                        i = i + 1
                        close_db()
                        continue

                    KPD = (read_block('T')["Q"] - read_block('MC')["Q"] - read_block('RC')["Q"]) / read_block('RHE')["Q"]
                    self.kpd_output.setText(str(round(KPD, tolerance_exp+2)))

                    print(round(P, 5), round(p_out, tolerance_exp + 2), round(x, tolerance_exp + 2), round(KPD, tolerance_exp + 2))
                    self.kpd_output.setText(str(round(KPD, tolerance_exp + 2)))

                    self.optimus_table.setItem(i, 6, QTableWidgetItem(str(round(KPD, 5))))
                    self.optimus_table.setItem(i, 5, QTableWidgetItem(
                        str(round(float(read_block("LTR")["DT"]), tolerance_exp))))
                    self.optimus_table.setItem(i, 4, QTableWidgetItem(
                        str(round(float(read_block("HTR")["DT"]), tolerance_exp))))
                    self.optimus_table.setItem(i, 3, QTableWidgetItem(
                        str(round(float(read_block("RHE")["DT"]), tolerance_exp))))

                    self.optimus_table.item(i, 0).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 1).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 2).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 3).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 4).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 5).setBackground(QColor(0, 204, 102))
                    self.optimus_table.item(i, 6).setBackground(QColor(0, 204, 102))
                    i = i + 1
                    close_db()

        self.time_flag = False
        if self.calc_Flag is True:
            self.status_img.setText('✔️')
            self.status_txt.setText('Расчёт завершён успешно')
        else:
            self.status_img.setText('🛑')
            self.status_txt.setText('Расчёт остановлен')
        print('end opt')


    def start(self):
        self.tab_menu.setCurrentIndex(1)
        self.balance_ax.clear()
        self.balance_ax.set_title('Баланс')
        self.balance_ax.set_xlabel('Итерация')
        self.balance_ax.semilogy()
        self.balance_ax.set_ylim([float(eval(self.cycle_tolerance_input.text())) / 10, 1])
        self.balance_ax.axhline(float(eval(self.cycle_tolerance_input.text())), color='red', linestyle='--')

        self.balance_ax.grid(True)
        self.balance_cumm = []
        self.balance_ax.plot(self.balance_cumm)
        self.graph_balance.draw()
        self.graph_balance.flush_events()

        print('start')
        self.status_img.setText('⏳')
        self.status_txt.setText('Запущен расчёт')
        self.kpd_output.setText(" ")

        self.time_flag = True
        self.time_start = datetime.datetime.now()

        self.calc_Flag = True
        self.thread_calc = Thread(target=self.calc)
        self.thread_calc.start()

        self.thread_timer = Thread(target=self.timer)
        self.thread_timer.start()

    def stop(self):
        print('stop')
        self.calc_Flag = False
        self.status_img.setText('🛑')
        self.status_txt.setText('Остановка расчёта')
        if self.thread_calc.is_alive() is False:
            self.status_img.setText('🛑')
            self.status_txt.setText('Расчёт остановлен')

    def timer(self):
        while self.time_flag is True:
            self.status_time.setText(f'Время расчёта: {(datetime.datetime.now() - self.time_start).seconds} с')
            self.update()
            time.sleep(0.5)

    def calc(self):
        print('calc')
        Tin_hot = float(self.reactor_tin_input.text())
        Tout_hot = float(self.reactor_tout_input.text())
        P_hot = float(self.reactor_p_input.text())
        fluid_hot = self.reactor_x_input.text()
        cp_hot = float(self.reactor_cp_input.text())
        G_hot = float(self.reactor_g_input.text())
        fluid = self.cycle_x_input.text()
        P = float(self.cycle_pmax_input.text())
        p_out = float(self.cycle_pmin_input.text())
        x = float(self.cycle_xr_input.text())
        h_steps = float(self.cycle_step_h.text())
        fluid_cond = self.cooler_fluid_input.text()
        Tcond = float(self.cooler_tcool_input.text())
        Tfcond = float(self.cooler_tcool_in_input.text())
        Pcond = float(self.cooler_pcool_in_input.text())
        dt_RHE = float(self.RHE_dt_input.text())
        dt_C = float(self.C_dt_input.text())
        dt_HTR = float(self.HTR_dt_input.text())
        dt_LTR = float(self.LTR_dt_input.text())
        KPD_T = float(self.T_KPD_input.text())
        KPD_MC = float(self.MC_KPD_input.text())
        KPD_RC = float(self.RC_KPD_input.text())
        cycle_tolerance = float(eval(self.cycle_tolerance_input.text()))
        root_tolerance = float(eval(self.cycle_tolerance_root.text()))
        tolerance_exp = abs(int(np.log10(cycle_tolerance)))

        open_db()
        write_stream('R-RHE', Tin_hot, P_hot, Tin_hot * cp_hot, 0, 0, G_hot, fluid_hot)
        write_stream('HTR-RHE', Tout_hot - dt_RHE, P, prop.t_p(Tout_hot - dt_RHE, P, fluid)['H'],
                     prop.t_p(Tout_hot - dt_RHE, P, fluid)['S'], prop.t_p(Tout_hot - dt_RHE, P, fluid)['Q'], 1000,
                     fluid)

        RHE = modules.RHE('R-RHE', 'RHE-R', 'HTR-RHE', 'RHE-T', Tout_hot, dt_RHE, root_tolerance, h_steps)
        HTR = modules.HTR('T-HTR', 'HTR-LTR', 'MIX-HTR', 'HTR-RHE', dt_HTR, root_tolerance, h_steps, dt_RHE)
        LTR = modules.LTR('HTR-LTR', 'LTR-SPLIT', 'MC-LTR', 'LTR-MIX', dt_LTR, root_tolerance, h_steps)
        MC = modules.MC('C-MC', 'MC-LTR', P, KPD_MC)
        RC = modules.RC('SPLIT-RC', 'RC-MIX', P, KPD_RC)
        T = modules.Turb('RHE-T', 'T-HTR', p_out, KPD_T)
        C = modules.C('SPLIT-C', 'C-MC', 'IN-C', 'C-OUT', Tcond, dt_C, root_tolerance, h_steps)
        MIX = modules.MIX('LTR-MIX', 'RC-MIX', 'MIX-HTR')
        SPLIT = modules.SPLIT('LTR-SPLIT', 'SPLIT-C', 'SPLIT-RC', x)

        for j in range(9999):
            if self.calc_Flag is False:
                self.time_flag = False
                self.status_img.setText('🛑')
                self.status_txt.setText('Расчёт остановлен')
                break

            self.calc_R_IN_T.setText(f'T = {round(float(read_stream("R-RHE")["T"]), tolerance_exp)}')
            self.calc_R_IN_P.setText(f'P = {round(float(read_stream("R-RHE")["P"]), tolerance_exp)}')
            self.calc_R_IN_G.setText(f'G = {round(float(read_stream("R-RHE")["G"]), tolerance_exp)}')
            self.calc_HTR_RHE_T.setText(f'T = {round(float(read_stream("HTR-RHE")["T"]), tolerance_exp)}')
            self.calc_HTR_RHE_P.setText(f'P = {round(float(read_stream("HTR-RHE")["P"]), tolerance_exp)}')
            self.calc_HTR_RHE_G.setText(f'G = {round(float(read_stream("HTR-RHE")["G"]), tolerance_exp)}')

            RHE.calc()

            self.calc_RHE_OUT_T.setText(f'T = {round(float(read_stream("RHE-R")["T"]), tolerance_exp)}')
            self.calc_RHE_OUT_P.setText(f'P = {round(float(read_stream("RHE-R")["P"]), tolerance_exp)}')
            self.calc_RHE_OUT_G.setText(f'G = {round(float(read_stream("RHE-R")["G"]), tolerance_exp)}')
            self.calc_RHE_T_T.setText(f'T = {round(float(read_stream("RHE-T")["T"]), tolerance_exp)}')
            self.calc_RHE_T_P.setText(f'P = {round(float(read_stream("RHE-T")["P"]), tolerance_exp)}')
            self.calc_RHE_T_G.setText(f'G = {round(float(read_stream("RHE-T")["G"]), tolerance_exp)}')

            self.calc_RHE_Q.setText(f'Q = {round(float(read_block("RHE")["Q"]), tolerance_exp)}')
            self.calc_RHE_dT.setText(f'ΔT = {round(float(read_block("RHE")["DT"]), tolerance_exp)}')

            T.calc()

            self.calc_T_HTR_T.setText(f'T = {round(float(read_stream("T-HTR")["T"]), tolerance_exp)}')
            self.calc_T_HTR_P.setText(f'P = {round(float(read_stream("T-HTR")["P"]), tolerance_exp)}')
            self.calc_T_HTR_G.setText(f'G = {round(float(read_stream("T-HTR")["G"]), tolerance_exp)}')
            self.calc_T_N.setText(f'N = {round(float(read_block("T")["Q"]), tolerance_exp)}')

            if j == 0:
                write_stream('HTR-LTR', read_stream('T-HTR')['T'], read_stream('T-HTR')['P'], read_stream('T-HTR')['H'],
                             read_stream('T-HTR')['S'], read_stream('T-HTR')['Q'], read_stream('T-HTR')['G'],
                             read_stream('T-HTR')['X'])

                self.calc_HTR_LTR_T.setText(f'T = {round(float(read_stream("HTR-LTR")["T"]), tolerance_exp)}')
                self.calc_HTR_LTR_P.setText(f'P = {round(float(read_stream("HTR-LTR")["P"]), tolerance_exp)}')
                self.calc_HTR_LTR_G.setText(f'G = {round(float(read_stream("HTR-LTR")["G"]), tolerance_exp)}')

                write_stream('LTR-SPLIT', read_stream('T-HTR')['T'], read_stream('T-HTR')['P'],
                             read_stream('T-HTR')['H'], read_stream('T-HTR')['S'], read_stream('T-HTR')['Q'],
                             read_stream('T-HTR')['G'], read_stream('T-HTR')['X'])

                self.calc_LTR_SPLIT_T.setText(f'T = {round(float(read_stream("LTR-SPLIT")["T"]), tolerance_exp)}')
                self.calc_LTR_SPLIT_P.setText(f'P = {round(float(read_stream("LTR-SPLIT")["P"]), tolerance_exp)}')
                self.calc_LTR_SPLIT_G.setText(f'G = {round(float(read_stream("LTR-SPLIT")["G"]), tolerance_exp)}')
                self.calc_LTR_Q.setText(f'Q = 0')
                self.calc_LTR_dT.setText(f'ΔT = 0')
                self.calc_HTR_Q.setText(f'Q = 0')
                self.calc_HTR_dT.setText(f'ΔT = 0')

            else:
                HTR.calc()

                self.calc_HTR_LTR_T.setText(f'T = {round(float(read_stream("HTR-LTR")["T"]), tolerance_exp)}')
                self.calc_HTR_LTR_P.setText(f'P = {round(float(read_stream("HTR-LTR")["P"]), tolerance_exp)}')
                self.calc_HTR_LTR_G.setText(f'G = {round(float(read_stream("HTR-LTR")["G"]), tolerance_exp)}')
                self.calc_HTR_RHE_T.setText(f'T = {round(float(read_stream("HTR-RHE")["T"]), tolerance_exp)}')
                self.calc_HTR_RHE_P.setText(f'P = {round(float(read_stream("HTR-RHE")["P"]), tolerance_exp)}')
                self.calc_HTR_RHE_G.setText(f'G = {round(float(read_stream("HTR-RHE")["G"]), tolerance_exp)}')
                self.calc_HTR_Q.setText(f'Q = {round(float(read_block("HTR")["Q"]), tolerance_exp)}')
                self.calc_HTR_dT.setText(f'ΔT = {round(float(read_block("HTR")["DT"]), tolerance_exp)}')

                LTR.calc()

                self.calc_LTR_SPLIT_T.setText(f'T = {round(float(read_stream("LTR-SPLIT")["T"]), tolerance_exp)}')
                self.calc_LTR_SPLIT_P.setText(f'P = {round(float(read_stream("LTR-SPLIT")["P"]), tolerance_exp)}')
                self.calc_LTR_SPLIT_G.setText(f'G = {round(float(read_stream("LTR-SPLIT")["G"]), tolerance_exp)}')
                self.calc_LTR_MIX_T.setText(f'T = {round(float(read_stream("LTR-MIX")["T"]), tolerance_exp)}')
                self.calc_LTR_MIX_P.setText(f'P = {round(float(read_stream("LTR-MIX")["P"]), tolerance_exp)}')
                self.calc_LTR_MIX_G.setText(f'G = {round(float(read_stream("LTR-MIX")["G"]), tolerance_exp)}')
                self.calc_LTR_Q.setText(f'Q = {round(float(read_block("LTR")["Q"]), tolerance_exp)}')
                self.calc_LTR_dT.setText(f'ΔT = {round(float(read_block("LTR")["DT"]), tolerance_exp)}')

            SPLIT.calc()

            self.calc_SPLIT_C_T.setText(f'T = {round(float(read_stream("SPLIT-C")["T"]), tolerance_exp)}')
            self.calc_SPLIT_C_P.setText(f'P = {round(float(read_stream("SPLIT-C")["P"]), tolerance_exp)}')
            self.calc_SPLIT_C_G.setText(f'G = {round(float(read_stream("SPLIT-C")["G"]), tolerance_exp)}')
            self.calc_SPLIT_RC_T.setText(f'T = {round(float(read_stream("SPLIT-RC")["T"]), tolerance_exp)}')
            self.calc_SPLIT_RC_P.setText(f'P = {round(float(read_stream("SPLIT-RC")["P"]), tolerance_exp)}')
            self.calc_SPLIT_RC_G.setText(f'G = {round(float(read_stream("SPLIT-RC")["G"]), tolerance_exp)}')

            write_stream('IN-C', Tcond, Pcond, prop.t_p(Tfcond, Pcond, fluid_cond)['H'],
                         prop.t_p(Tfcond, Pcond, fluid_cond)['S'], 0, 1000, fluid_cond)
            #не вывожу холодный

            C.calc()

            self.calc_C_MC_T.setText(f'T = {round(float(read_stream("C-MC")["T"]), tolerance_exp)}')
            self.calc_C_MC_P.setText(f'P = {round(float(read_stream("C-MC")["P"]), tolerance_exp)}')
            self.calc_C_MC_G.setText(f'G = {round(float(read_stream("C-MC")["G"]), tolerance_exp)}')
            self.calc_C_Q.setText(f'Q = {round(float(read_block("C")["Q"]), tolerance_exp)}')
            self.calc_C_dT.setText(f'ΔT = {round(float(read_block("C")["DT"]), tolerance_exp)}')

            MC.calc()

            self.calc_MC_LTR_T.setText(f'T = {round(float(read_stream("MC-LTR")["T"]), tolerance_exp)}')
            self.calc_MC_LTR_P.setText(f'P = {round(float(read_stream("MC-LTR")["P"]), tolerance_exp)}')
            self.calc_MC_LTR_G.setText(f'G = {round(float(read_stream("MC-LTR")["G"]), tolerance_exp)}')
            self.calc_MC_N.setText(f'N = {round(float(read_block("MC")["Q"]), tolerance_exp)}')

            RC.calc()

            self.calc_RC_MIX_T.setText(f'T = {round(float(read_stream("RC-MIX")["T"]), tolerance_exp)}')
            self.calc_RC_MIX_P.setText(f'P = {round(float(read_stream("RC-MIX")["P"]), tolerance_exp)}')
            self.calc_RC_MIX_G.setText(f'G = {round(float(read_stream("RC-MIX")["G"]), tolerance_exp)}')
            self.calc_RC_N.setText(f'N = {round(float(read_block("RC")["Q"]), tolerance_exp)}')

            LTR.calc()
            self.calc_LTR_SPLIT_T.setText(f'T = {round(float(read_stream("LTR-SPLIT")["T"]), tolerance_exp)}')
            self.calc_LTR_SPLIT_P.setText(f'P = {round(float(read_stream("LTR-SPLIT")["P"]), tolerance_exp)}')
            self.calc_LTR_SPLIT_G.setText(f'G = {round(float(read_stream("LTR-SPLIT")["G"]), tolerance_exp)}')
            self.calc_LTR_MIX_T.setText(f'T = {round(float(read_stream("LTR-MIX")["T"]), tolerance_exp)}')
            self.calc_LTR_MIX_P.setText(f'P = {round(float(read_stream("LTR-MIX")["P"]), tolerance_exp)}')
            self.calc_LTR_MIX_G.setText(f'G = {round(float(read_stream("LTR-MIX")["G"]), tolerance_exp)}')
            self.calc_LTR_Q.setText(f'Q = {round(float(read_block("LTR")["Q"]), tolerance_exp)}')
            self.calc_LTR_dT.setText(f'ΔT = {round(float(read_block("LTR")["DT"]), tolerance_exp)}')

            MIX.calc()
            self.calc_MIX_HTR_T.setText(f'T = {round(float(read_stream("MIX-HTR")["T"]), tolerance_exp)}')
            self.calc_MIX_HTR_P.setText(f'P = {round(float(read_stream("MIX-HTR")["P"]), tolerance_exp)}')
            self.calc_MIX_HTR_G.setText(f'G = {round(float(read_stream("MIX-HTR")["G"]), tolerance_exp)}')

            HTR.calc()
            self.calc_HTR_LTR_T.setText(f'T = {round(float(read_stream("HTR-LTR")["T"]), tolerance_exp)}')
            self.calc_HTR_LTR_P.setText(f'P = {round(float(read_stream("HTR-LTR")["P"]), tolerance_exp)}')
            self.calc_HTR_LTR_G.setText(f'G = {round(float(read_stream("HTR-LTR")["G"]), tolerance_exp)}')
            self.calc_HTR_RHE_T.setText(f'T = {round(float(read_stream("HTR-RHE")["T"]), tolerance_exp)}')
            self.calc_HTR_RHE_P.setText(f'P = {round(float(read_stream("HTR-RHE")["P"]), tolerance_exp)}')
            self.calc_HTR_RHE_G.setText(f'G = {round(float(read_stream("HTR-RHE")["G"]), tolerance_exp)}')
            self.calc_HTR_Q.setText(f'Q = {round(float(read_block("HTR")["Q"]), tolerance_exp)}')
            self.calc_HTR_dT.setText(f'ΔT = {round(float(read_block("HTR")["DT"]), tolerance_exp)}')

            balance = abs(
                read_block('RHE')["Q"] + read_block('MC')["Q"] + read_block('RC')["Q"] - read_block('T')["Q"] -
                read_block('C')["Q"]) / read_block('RHE')["Q"]

            self.calc_balance.setText(f"Δ = {balance}")
            self.balance_cumm.append(balance)
            self.balance_ax.clear()
            self.balance_ax.set_title('Баланс')
            self.balance_ax.set_xlabel('Итерация')
            self.balance_ax.semilogy()
            self.balance_ax.set_ylim([cycle_tolerance/10,1])
            self.balance_ax.axhline(cycle_tolerance, color='red', linestyle='--')
            self.balance_ax.plot(self.balance_cumm)
            self.balance_ax.grid(True)
            self.graph_balance.draw()
            self.graph_balance.flush_events()

            if balance < cycle_tolerance:
                break
        KPD = (read_block('T')["Q"] - read_block('MC')["Q"] - read_block('RC')["Q"]) / read_block('RHE')["Q"]
        print(P,p_out,x, KPD)
        self.kpd_output.setText(str(round(KPD, tolerance_exp+2)))
        close_db()


        self.time_flag = False
        if self.calc_Flag is True:
            self.status_img.setText('✔️')
            self.status_txt.setText('Расчёт завершён успешно')
        else:
            self.status_img.setText('🛑')
            self.status_txt.setText('Расчёт остановлен')
        print('end calc')


app = QApplication([])
window = Window()
window.show()
app.exec()
