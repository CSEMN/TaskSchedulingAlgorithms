from tkinter import *
from tkinter import ttk 
from Task import Task as MyTask
from algorithms import sched_fifo,sched_rr,sched_edf,sched_dma,sched_rma,sched_lst
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from sched_test import first_test,second_test

ALGORITHMS = ["FIFO","RR","LST","EDF","DMA","RMA"]

class Application:
    def __init__(self,root:Tk):
        self.configWindow(root)
        self.mainFrame = Frame(root)
        self.mainFrame.pack(padx=10,pady=10)
        self.buildConfigFrame(self.mainFrame)

    def configWindow(self,window:Tk):
        window.title("Scheduling Simulator")
        window.geometry('1000x800')
        # window.resizable(0,0)

    def buildConfigFrame(self,parent):
        self.configFrame = LabelFrame(parent,text="Application Config")

        self.algoSelLbl = Label(self.configFrame,text="Algorithm")
        self.algo = StringVar(parent)
        self.algo.set(ALGORITHMS[0])
        self.algoComboBox = ttk.Combobox(self.configFrame, values = ALGORITHMS,width=6)
        self.algoComboBox.current(0)

        self.taskCountLbl = Label(self.configFrame,text="Task Count")
        self.taskCountSpinbox = ttk.Spinbox(self.configFrame,from_=1,to=6,width=3)
        self.taskCountSpinbox.set(1)

        self.configSetBtn = ttk.Button(self.configFrame,text="\nSet\n",command= lambda : self.buildTaskDefintionFrame(parent))

        self.sysWatch = ttk.Entry(self.configFrame,width=6)
        self.sysWatch.insert(0,"50")
        self.quantum = ttk.Entry(self.configFrame,width=6)
        self.quantum.insert(0,"0.25")
        self.runTime = ttk.Entry(self.configFrame,width=6)
        self.runTime.insert(0,"1")

        #Grid section
        self.configFrame.grid(row=0,column=0,columnspan=5,padx=20,pady=(0,10))

        self.algoSelLbl.grid(row=0,column=0,padx=(20,5),pady=(10,10))
        self.algoComboBox.grid(row=0,column=1,padx=(5,10),pady=(10,10))

        self.taskCountLbl.grid(row=0,column=2,padx=(20,5),pady=(10,10))
        self.taskCountSpinbox.grid(row=0,column=3,padx=(5,10),pady=(10,10))

        self.showTitleVar = IntVar()
        self.showTitleVar.set(1)
        self.showTaskTitle = ttk.Checkbutton(self.configFrame,text="Show Task Title",variable=self.showTitleVar)
        self.showTaskTitle.grid(row=0,column=4,columnspan=2,padx=(5,10),pady=(10,10))

        self.configSetBtn.grid(row=0,column=6,rowspan=2,padx=(20,20),pady=(10,10))

        Label(self.configFrame,text="Watch Time").grid(row=1,column=0,padx=(10,5),pady=(10,10))
        self.sysWatch.grid(row=1,column=1,padx=(5,10),pady=(10,10))

        Label(self.configFrame,text="Quantum Time").grid(row=1,column=2,padx=(10,5),pady=(10,10))
        self.quantum.grid(row=1,column=3,padx=(5,10),pady=(10,10))

        Label(self.configFrame,text="Run Time").grid(row=1,column=4,padx=(10,5),pady=(10,10))
        self.runTime.grid(row=1,column=5,padx=(5,10),pady=(10,10))

    
    def buildTaskDefintionFrame(self,parent):

        if hasattr(self,"taskDefLblFrame"):
            self.taskDefLblFrame.destroy()

        task_count = int(self.taskCountSpinbox.get())
        selected_algo = self.algoComboBox.get()

        self.taskDefList = list[dict]() # r , p , e , d 

        self.taskDefLblFrame = LabelFrame(parent,text="Tasks Definition")
        self.taskDefLblFrame.grid(row=1,column=0,columnspan=5)

        for i in range(task_count):
            lblFrame = LabelFrame(self.taskDefLblFrame,text=f"T {i+1}")
            lblFrame.grid(row=0,column=i,padx=5,pady=5)
            taskDefDict = dict()

            rlbl = Label(lblFrame,text="Release")

            plbl = Label(lblFrame,text="Period")
            plbl.grid(row=1,column=0,padx=5,pady=5,sticky=W)

            elbl = Label(lblFrame,text="Execution")
            elbl.grid(row=2,column=0,padx=5,pady=5,sticky=W)

            dlbl = Label(lblFrame,text="Deadline")

            taskDefDict['r']= ttk.Entry(lblFrame,width=4)
            taskDefDict['p']= ttk.Entry(lblFrame,width=4)
            taskDefDict['e']= ttk.Entry(lblFrame,width=4)
            taskDefDict['d']= ttk.Entry(lblFrame,width=4)

            if selected_algo == "FIFO" or selected_algo == "RR" or selected_algo == "DMA" :
                rlbl.grid(row=0,column=0,padx=5,pady=5,sticky=W)
                dlbl.grid(row=3,column=0,padx=5,pady=5,sticky=W)
                taskDefDict['r'].grid(row=0,column=1,padx=(0,5),pady=5)
                taskDefDict['d'].grid(row=3,column=1,padx=(0,5),pady=5)

            taskDefDict['p'].grid(row=1,column=1,padx=(0,5),pady=5)
            taskDefDict['e'].grid(row=2,column=1,padx=(0,5),pady=5)

            self.taskDefList.append(taskDefDict)

        self.actionFrame = LabelFrame(self.taskDefLblFrame,text="Actions")
        self.actionFrame.grid(row=5,column=0,columnspan=6,padx=10,pady=10)
        self.schedBtn = ttk.Button(self.actionFrame,text="SCHEDULE",padding=(10,8),command=self.schedule)
        self.firstTestBtn = ttk.Button(self.actionFrame,text="  First Test\n(Utilization)",command=lambda:self.applyFirstTest(parent))
        self.secondTestBtn = ttk.Button(self.actionFrame,text="      Second Test\n(Completion-time)",command=lambda:self.applySecondTest(parent))
        self.schedBtn.grid(row=0,column=0,padx=(10,5),pady=10)
        self.firstTestBtn.grid(row=0,column=1,padx=(5,5),pady=10)
        self.secondTestBtn.grid(row=0,column=2,padx=(5,10),pady=10)

    def getTasks(self):
        selected_algo = self.algoComboBox.get()
        tasks = list[MyTask]()
        for uiTask in self.taskDefList:
            p = float(uiTask['p'].get())
            e = float(uiTask['e'].get())

            index = self.taskDefList.index(uiTask)

            if selected_algo == "FIFO" or selected_algo == "RR" or selected_algo == "DMA":
                r = float(uiTask['r'].get())
                d = float(uiTask['d'].get())
                t = MyTask(id=index+1,p=p,e=e,r=r,d=d)
            else:
                t = MyTask(id=index+1,p=p,e=e)
            tasks.append(t)
        
        return tasks
    
    def getTasksIntValues(self):
        selected_algo = self.algoComboBox.get()
        tasks = list[MyTask]()
        for uiTask in self.taskDefList:
            p = int(uiTask['p'].get())
            e = int(uiTask['e'].get())

            index = self.taskDefList.index(uiTask)

            if selected_algo == "FIFO" or selected_algo == "RR" or selected_algo == "DMA":
                r = int(uiTask['r'].get())
                d = int(uiTask['d'].get())
                t = MyTask(id=index+1,p=p,e=e,r=r,d=d)
            else:
                t = MyTask(id=index+1,p=p,e=e)
            tasks.append(t)
        
        return tasks
    
    def schedule(self):
        quantumval = float(self.quantum.get())
        syswatch = float(self.sysWatch.get())
        runtime = float(self.runTime.get())

        if self.showTitleVar.get() == 0:
            showTitle = False
        else:
            showTitle = True
        selected_algo = self.algoComboBox.get()
        tasks = self.getTasks()
        # for t in tasks:
        #     print(t.id," , ",t.releaseTime," , ",t.period," , ",t.executionTime," , ",t.deadline)
        logs=''

        if(selected_algo == "FIFO"):
            logs = sched_fifo(tasks,syswatch,runtime)
        elif selected_algo == "RR":
            logs = sched_rr(tasks,syswatch,quantumval)
        elif selected_algo == "EDF":
            logs = sched_edf(tasks,syswatch,runtime,quantumval)
        elif selected_algo == "DMA":
            logs = sched_dma(tasks)
        elif selected_algo == "LST":
            logs = sched_lst(tasks,syswatch,runtime)
        elif selected_algo == "RMA":
            tasks = self.getTasksIntValues()
            logs = sched_rma(tasks)

        print_logs(logs)
        draw_timing_diagram(logs,tasks,showTaskTitle=showTitle)
    
    def applyFirstTest(self,parent):
        tasks = self.getTasks()
        result = first_test(tasks)

        if hasattr(self,"testResultFrame"):
            self.testResultFrame.destroy()

        self.testResultFrame = LabelFrame(parent,text="Test Result")
        self.testResultFrame.grid(row=3,column=0,columnspan=5,pady=10,padx=10)
        if result[0]:
            #Scheduable
            Label(self.testResultFrame,text=f"Utility ( {result[1]} ) < Bound ( {result[2]} )").pack(padx=10,pady=10)
            Label(self.testResultFrame,text=f"Task Set is Schedulable",fg='green').pack(padx=10,pady=10)
        else:
            Label(self.testResultFrame,text=f"Utility ( {result[1]} ) > Bound ( {result[2]} )").pack(padx=10,pady=10)
            Label(self.testResultFrame,text=f"Task Set is not schedulable",fg='red').pack(padx=10,pady=10)
        
        return result[0]
    
    
    def applySecondTest(self,parent):
        firstRes = self.applyFirstTest(parent)
        if firstRes : 
            Label(self.testResultFrame,text=f"No Need for second Test").pack(padx=10,pady=10)
        else:
            Label(self.testResultFrame,text="Applying Second Test ...").pack(padx=10,pady=10)
            tasks = self.getTasks()
            result = second_test(tasks)

            counter = 0
            for res in result:
                counter+=1
                if res:
                    Label(self.testResultFrame,text=f"Task {counter} is schedulable",fg="green").pack(padx=10,pady=10)
                else:
                    Label(self.testResultFrame,text=f"Task {counter} is not schedulable",fg="red").pack(padx=10,pady=10)

            if result[len(result)-1]:
                Label(self.testResultFrame,text="Task Set is schedulable",fg="green").pack(padx=10,pady=10)
            else:
                Label(self.testResultFrame,text="Task Set is not schedulable",fg="red").pack(padx=10,pady=10)



def print_logs(logs):
    for log in logs:
        print("TASK " ,log[0].id, ", Job ",log[0].jobNum,", ",log[1],log[2],log[3])

def draw_timing_diagram(logs:list,tasks:list[MyTask],showTaskTitle = True):
    colors = ['orange','blue','grey','green',"brown",'pink','yellow','red']
    fig, ax = plt.subplots()
    fig.set_figwidth(12)
    fig.set_figheight(8)
    ax.plot([0, 0],[0, 0],color='white')
    for log in logs:
        x = log[1]
        y = 4+ ((log[0].id - 1) * 4)
        ax.add_patch(Rectangle((x, y), log[2]-log[1], 3,facecolor = colors[log[0].id - 1],))

        if showTaskTitle:
            ax.text(x+((log[2]-log[1])/2), y+1.5, f"T{log[0].id}{log[0].jobNum}",
                horizontalalignment='center', verticalalignment='center',**{'size'   : 8})
            
        ax.add_patch(Rectangle((x, 0), log[2]-log[1], 3,facecolor = colors[log[0].id - 1],))
        if log[3] == "DEADLINE":
            font = {'weight' : 'bold','size'   : 8,'color':"red"}
            ax.text(x+((log[2]-log[1])/2), 1.5, f"T{log[0].id}{log[0].jobNum}\ndeadline\nbroken",
                horizontalalignment='center', verticalalignment='center',**font)
        else:
            if showTaskTitle:
                ax.text(x+((log[2]-log[1])/2), 1.5, f"T{log[0].id}{log[0].jobNum}",
                horizontalalignment='center', verticalalignment='center',**{'size'   : 8})
        
        
    labels = ['time line']
    for task in tasks:
        labels.append(f'Task {task.id}')

    ax.set_yticklabels('')
    ax.set_title('Timing Diagram')
    plt.show()

