from game import game
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

pos = [["Eddie Collins","Cy Young",'Buck Ewing',"Jake Beckley","Bid McPhee","Jimmy Collins","Bobby Wallace","Fred Clarke","Ty Cobb","Jim O'Rourke"],
       ["Eddie Collins","Christy Mathewson",'Buck Ewing',"Jake Beckley","Bid McPhee","Jimmy Collins","Bobby Wallace","Fred Clarke","Ty Cobb","Jim O'Rourke"]]
lineup = [[0,2,3,4,5,6,7,8,9],[0,2,3,4,5,6,7,8,9]]
G = game(positions=pos, lineups=lineup)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Strat-O-Matic")
        
        fig_scoreboard = Figure(figsize=[10, 1.8])
        self.ax_scoreboard = fig_scoreboard.add_subplot()
        self.ax_scoreboard.set_position([0.05,0,.9,1])
        
        fig_field = Figure(figsize=[10, 6])
        self.ax_field = fig_field.add_subplot()  # Adjust subplot position
        
        fig_boxscore = Figure(figsize=[10, 6])
        self.ax_boxscore = fig_boxscore.add_subplot()  # Adjust subplot position
        
        self.canvas_scoreboard = FigureCanvas(fig_scoreboard)
        self.canvas_field = FigureCanvas(fig_field)
        self.canvas_boxscore = FigureCanvas(fig_boxscore)
        
        self.button = QPushButton("Roll?")
        self.button.clicked.connect(self.roll_button_clicked)
        
        layout = QVBoxLayout()
        
        # Area 1: Scoreboard Area
        layout.addWidget(self.canvas_scoreboard)
        
        # Area 2: Field and Box Score Area
        hbox = QHBoxLayout()
        hbox.addWidget(self.canvas_field)
        hbox.addWidget(self.canvas_boxscore)
        layout.addLayout(hbox)
        
        # Area 3: Button Area
        layout.addWidget(self.button)
        
        widget = QWidget()
        widget.setLayout(layout)
        
        self.setCentralWidget(widget)
        self.display_figure()

    def display_figure(self):
        

        # Area 1: Scoreboard Area
        G.SB.display(ax = self.ax_scoreboard)
        self.canvas_scoreboard.draw()
        
        # Area 2: Field Area
        G.GS.display(ax=self.ax_field)
        self.canvas_field.draw()
        
        # Area 3: Box Score Area
        G.BS.display(ax = self.ax_boxscore)
        self.canvas_boxscore.draw()        

    def roll_button_clicked(self):
        G.PA()
        self.ax_scoreboard.clear()
        self.ax_field.clear()
        self.ax_boxscore.clear()
        self.display_figure()

app = QApplication([])
window = MainWindow()
window.show()
app.exec_()

