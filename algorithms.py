from typing import List
from math import gcd,ceil
import sys
from Task import Task as MyTask
import copy

def sched_fifo(tasks:list[MyTask],watchTime,runTime):
    system_log = list() #(task,startTime,endTime,notes)
    system_time = 0
    system_queue = tasks
    def sorted_queue():
        return sorted(system_queue,key=lambda task:task.releaseTime)
    #run system
    while (system_time <= watchTime):
        if(len(system_queue) == 0):
            system_time+= runTime
            continue

        system_queue = sorted_queue()
        task = system_queue[0]
        
        if(system_time>= task.releaseTime):
            try:
                task.run(task.executionTime,systemTime=system_time)
            except:
                print("Task ",task.id,f"(Job {task.jobNum}) Excedded Deadline")
                system_log.append((task,system_time,system_time+task.executionTime,"DEADLINE"))
                break
            system_queue.pop(0)
            system_queue.append(task.get_next_job())
            system_log.append((task,system_time,system_time+task.executionTime,''))
            system_time+=task.executionTime
        else:
            system_time+= runTime
    return system_log

def sched_rr(tasks:list[MyTask],watchTime,quantumTime,beginingSystemTime=0):
    system_log = list() #(task,startTime,endTime)
    system_time = beginingSystemTime
    system_queue = tasks

    #run system
    while (system_time <= watchTime):
        if(len(system_queue) == 0):
            system_time+= quantumTime
            continue

        #num of ready tasks
        readyTasksCount = 0
        for tas in system_queue:
            if tas.releaseTime <= system_time :
                readyTasksCount+=1
            if(tas.releaseTime == system_time):
                system_queue.remove(tas)
                system_queue.insert(0,tas)
        task = system_queue[0]
        
        if(system_time>= task.releaseTime):
            try:
                task.run(quantumTime,systemTime=system_time)
            except:
                print("Task ",task.id,f"(Job {task.jobNum}) Excedded Deadline")
                system_log.append((task,system_time,system_time+quantumTime,"DEADLINE"))
                break
            
            if(task.remainingTime == 0 ):
                system_queue.pop(0)
                system_queue.append(task.get_next_job())
            else:
                tas = system_queue.pop(0)
                system_queue.insert(readyTasksCount-1,tas)
            system_log.append((task,system_time,system_time+quantumTime,''))
            system_time+=quantumTime

        else:
            system_time+= quantumTime
    return system_log

def sched_lst(tasks:list[MyTask],watchTime,runTime):
    system_log = list() #(task,startTime,endTime)
    system_time = 0
    system_queue = tasks
    def sorted_queue():
        #sort by least slack time
        return sorted(system_queue,key=lambda task:(task.deadline - system_time - task.remainingTime))
    #run system
    while (system_time <= watchTime):
        if(len(system_queue) == 0):
            system_time+= runTime
            continue
        # print("Before sorting :" ,system_queue)
        system_queue = sorted_queue()
        # print("After sorting :" ,system_queue)
        # print()
        task = None
        for t in system_queue :
            if t.releaseTime <= system_time:
                task = t
                break 
        if task == None:
            system_time+= runTime
            continue
        
        if(system_time>= task.releaseTime):
            try:
                task.run(runTime,systemTime=system_time)
            except:
                print("Task ",task.id,f"(Job {task.jobNum}) Excedded Deadline")
                system_log.append((task,system_time,system_time+runTime,"DEADLINE"))
                break
            if task.remainingTime == 0:
                system_queue.remove(task)
                system_queue.append(task.get_next_job())
            system_log.append((task,system_time,system_time+runTime,''))
            system_time+=runTime
        else:
            system_time+= runTime
    return system_log


def sched_rma(tasks:list[MyTask]):
    return RMA.main(tasks)

def sched_rr_followup(tasks:list[MyTask],watchTime,quantumTime,beginingSystemTime=0):
    system_log = list() #(task,startTime,endTime)
    system_time = beginingSystemTime
    system_queue = tasks

    #run system
    while (system_time <= watchTime):
        if(len(system_queue) == 0):
            system_time+= quantumTime
            continue

        #num of ready tasks
        readyTasksCount = 0
        for tas in system_queue:
            if tas.releaseTime <= system_time :
                readyTasksCount+=1
            if(tas.releaseTime == system_time):
                system_queue.remove(tas)
                system_queue.insert(0,tas)
        task = system_queue[0]
        
        if(system_time>= task.releaseTime):
            try:
                task.run(quantumTime,systemTime=system_time)
            except:
                print("Task ",task.id,f"(Job {task.jobNum}) Excedded Deadline")
                system_log.append((task,system_time,system_time+quantumTime,"DEADLINE"))
                break
            
            if(task.remainingTime == 0 ):
                system_queue.pop(0)
                system_queue.append(task.get_next_job())
            else:
                tas = system_queue.pop(0)
                system_queue.insert(readyTasksCount-1,tas)
            system_log.append((task,system_time,system_time+quantumTime,''))
            system_time+=quantumTime

        else:
            system_time+= quantumTime
    return (system_log,system_queue,system_time)

def sched_edf(tasks:list[MyTask],watchTime,runTime,quantumTime=0.25):
    system_log = list() #(task,startTime,endTime)
    system_time = 0
    system_queue = tasks
    def sorted_queue():
        return sorted(system_queue,key=lambda task:task.deadline)
    #run system
    while (system_time <= watchTime):
        if(len(system_queue) == 0):
            system_time+= runTime
            continue

        system_queue = sorted_queue()
        
        if(len(system_queue)>1):
            if(system_queue[0].deadline == system_queue[1].deadline and  system_time >= system_queue[0].releaseTime and system_time >= system_queue[1].releaseTime ):
                #if equal deadline round robin 
                troubleDeadline = system_queue[0].deadline
                roundRobinTasks = list[MyTask]()
                for tas in system_queue:
                    if tas.deadline == troubleDeadline and system_time >= tas.releaseTime:
                        roundRobinTasks.append(tas)
                
                for tas in roundRobinTasks:
                    system_queue.remove(tas)

                rr_logs,rr_tasks,rr_time = sched_rr_followup(roundRobinTasks,troubleDeadline,quantumTime,system_time)
                system_time = rr_time
                for tas in rr_tasks:
                    system_queue.append(tas)
                
                for log in rr_logs:
                    system_log.append(log)
                if(system_log[len(system_log)-1][3]=="DEADLINE"):
                    return system_log
                
        
        task = None
        for tas in system_queue :
            if tas.releaseTime <= system_time:
                task = tas
                break

        if task == None:
            task = system_queue[0]
        
        if(system_time>= task.releaseTime):
            try:
                task.run(runTime,systemTime=system_time)
            except:
                print("Task ",task.id,f"(Job {task.jobNum}) Excedded Deadline")
                system_log.append((task,system_time,system_time+task.executionTime,"DEADLINE"))
                break
            if(task.remainingTime== 0):
                system_queue.pop(0)
                system_queue.append(task.get_next_job())
            system_log.append((task,system_time,system_time+runTime,''))
            system_time+=runTime
        else:
            system_time+= runTime
    return system_log


class RMA:
            
    class Task:
        def __init__(self, period, cTime, identification):
            self.p = period
            self.c = cTime
            self.r = cTime
            self.id = identification
            self.entryTime = 0

    class ReadyQueue:
        def __init__(self):
            self.lastExecutedTask = None
            self.TheQueue = []
            self.timeLapsed = 0

            self.LogsList = [] # ("S|C|D",task,time) 

        def executeOneUnit(self):
            if not self.TheQueue:
                self.timeLapsed += 1
                return 0

            self.timeLapsed += 1
            
            T = self.TheQueue[0]
            
            if T.r <= 0:
                raise Exception("Remaining time of the task became negative or is 0 from first")
                
            T.r -= 1
            
            if (T.r + 1 == T.c) or (T != self.lastExecutedTask and self.lastExecutedTask is not None):
                # print(f"Time {self.timeLapsed - 1}, Task {T.id} Started")
                self.LogsList.append(('S',T.id,self.timeLapsed - 1))

            self.lastExecutedTask = T
            
            if T.r == 0:
                if T.entryTime + T.p >= self.timeLapsed:
                    # print(f"Time {self.timeLapsed}, Task {T.id} Completed")
                    self.LogsList.append(('C',T.id,self.timeLapsed))
                    self.TheQueue.pop(0)
                    return 2
                else:
                    # print(f"Task {self.TheQueue[0].id} finished at time {self.timeLapsed} thus, missing it's deadline of time {(self.TheQueue[0].entryTime + self.TheQueue[0].p)}.")
                    self.LogsList.append(('D',T.id,self.timeLapsed ))
                    self.TheQueue.pop(0)
                    return -1
                
            return 99

        def addNewTask(self, T):
            if not self.TheQueue:
                self.TheQueue.append(T)
                T.entryTime = self.timeLapsed
                return 0
            
            if T.p == self.TheQueue[0].p:
                self.TheQueue.insert(1, T)
                T.entryTime = self.timeLapsed
                return 1
            
            if T.p < self.TheQueue[0].p:
                tFlag = self.TheQueue[0].c == self.TheQueue[0].r
                self.TheQueue.insert(0, T)
                T.entryTime = self.timeLapsed
                
                if tFlag:
                    return 2
                else:
                    print(f"Time {self.timeLapsed}, Task {self.TheQueue[1].id} has been preempted.")
                    return 3
            
            if T.p > self.TheQueue[0].p:
                if len(self.TheQueue) == 1:
                    self.TheQueue.append(T)
                    T.entryTime = self.timeLapsed
                    return 4
                
                for i in range(1, len(self.TheQueue)):
                    if T.p < self.TheQueue[i].p:
                        self.TheQueue.insert(i, T)
                        T.entryTime = self.timeLapsed
                        return 5
                    
                    if T.p > self.TheQueue[i].p:
                        if i == len(self.TheQueue) - 1:
                            self.TheQueue.append(T)
                            T.entryTime = self.timeLapsed
                            return 6

            return 7

    @staticmethod
    def sigma(taskList):
        returnValue = 0.00
        for eachTask in taskList:
            returnValue = returnValue + (((float(eachTask.c)) / (float(eachTask.p))))
        return returnValue

    @staticmethod
    def muSigma(n):
        return ((float(n)) * ((2 ** ((1 / (float(n)))) - 1)))

    @staticmethod
    def gcd(a, b):
        while b > 0:
            temp = b
            b = a % b
            a = temp
        return a

    @staticmethod
    def lcm(a, b):
        return a * (b // gcd(a, b))

    @staticmethod
    def lcm_list(input: List[int]) -> int:
        result = input[0]
        for i in range(1, len(input)):
            result = RMA.lcm(result, input[i])
        return result
    
    @staticmethod
    def parseLogList(RMALogList):
        jobDict = dict()
        myLogs = [] #(Task,start,end,note)
        for rmaLog in RMALogList:
            #count job num
            if rmaLog[1] in jobDict:
                if rmaLog[0] == "S":
                    jobDict[rmaLog[1]] +=1
            else:
                jobDict[rmaLog[1]] =1
            
            if rmaLog[0] == "S":
                myT = MyTask(rmaLog[1]+1,0,0,jobNum=jobDict[rmaLog[1]])
                myLogs.append((myT,rmaLog[2],0,''))
            elif rmaLog[0] == "C":
                for i in range(len(myLogs)):
                    if(myLogs[i][0].id ==rmaLog[1]+1 and myLogs[i][0].jobNum == jobDict[rmaLog[1]] ):
                        tmp = list(myLogs[i])
                        tmp[2] = rmaLog[2]
                        myLogs[i] = tuple(tmp)
                        break
            elif rmaLog[0] == "D":
                for i in range(len(myLogs)):
                    if(myLogs[i][0].id ==rmaLog[1]+1 and myLogs[i][0].jobNum == jobDict[rmaLog[1]] ):
                            tmp = list(myLogs[i])
                            tmp[2] = rmaLog[2]
                            tmp[3] = 'DEADLINE'
                            myLogs[i] = tuple(tmp)
                            break
        return myLogs
                
    @staticmethod
    def main(myTaskList:list[MyTask]):
        PeriodicTaskList = []
        ReadyQueue = RMA.ReadyQueue()
        try:
            periodList = []
            for mytas in myTaskList:
                
                periodList.append(mytas.period)
                tempTask = RMA.Task(mytas.period, mytas.executionTime, myTaskList.index(mytas))
                PeriodicTaskList.append(tempTask)

            isFailure = not (RMA.sigma(PeriodicTaskList) <= RMA.muSigma(len(PeriodicTaskList)))
            if isFailure:
                print("\n##Note that this task set does not satisfy the schedulability check,\ntherefore there are chances of deadline misses.")

            periodArray = periodList
            periodLCM = RMA.lcm_list(periodArray)
            print("************************************ Execution Are Running ************************************")

            for i in range(sys.maxsize):
                for individualTask in PeriodicTaskList:
                    if i % individualTask.p == 0:
                        ReadyQueue.addNewTask(RMA.Task(individualTask.p, individualTask.c, individualTask.id))
                if i != 0 and i % periodLCM == 0:
                    tempVar = 0
                    if len(ReadyQueue.TheQueue) == len(PeriodicTaskList):
                        for k in range(len(ReadyQueue.TheQueue)):
                            if ReadyQueue.TheQueue[k].r != ReadyQueue.TheQueue[k].c:
                                tempVar = 1
                                break
                    if tempVar == 0:
                        print("The End Of First Cycle")
                        return RMA.parseLogList(ReadyQueue.LogsList)
                output = ReadyQueue.executeOneUnit()
                if output == -1:
                    return RMA.parseLogList(ReadyQueue.LogsList)
        except Exception as e:
            print(f"Some error occurred. Program will now terminate: {e}")

class DMATask:
    def __init__(self, id: int, release: int, period: int, execution: int, deadline: int):
        self.id = id
        self.release = release
        self.period = period
        self.execution = execution
        self.deadline = deadline
        self.remaining = execution
        self.precedence = []
    
    def __lt__(self, other):
        return self.period < other.period

class DMAScheduler:
    def __init__(self, tasks: List[DMATask]):
        self.tasks = tasks
        self.ready_queue = []
        self.time = 0
        self.DMAlogs = []

    def add_task_to_queue(self, task: DMATask):
        if task not in self.ready_queue:
            self.ready_queue.append(task)
            self.ready_queue.sort(key=lambda x: x.deadline)

    def remove_task_from_queue(self, task: DMATask):
        if task in self.ready_queue:
            self.ready_queue.remove(task)

    def execute_task(self, task: DMATask):
        task.remaining -= 1
        if task.remaining == 0:
            self.remove_task_from_queue(task)
            if self.time <= task.deadline:
                self.DMAlogs.append(('C',task.id,self.time))
                # print(f"Time {self.time}: Task {task.id} completed")

    def run(self):

        biggetsDeadLine = 0
        for task in self.tasks:
            if task.deadline> biggetsDeadLine:
                biggetsDeadLine = task.deadline
        while True:

            if self.time + 1 > biggetsDeadLine:
                break

            for task in self.tasks:
                if self.time >= task.release and (self.time - task.release) % task.period == 0: 
                    self.add_task_to_queue(task)
            
            if not self.ready_queue:
                self.time += 1
                continue
            
            current_task = self.ready_queue[0]
            for task in self.ready_queue:
                if task.deadline < current_task.deadline:
                    current_task = task

            self.DMAlogs.append(('E',current_task.id,self.time))
            self.execute_task(current_task)
            self.time += 1

            
            if current_task.remaining > 0 and current_task in self.ready_queue[1:]:
                self.ready_queue.remove(current_task)
                self.add_task_to_queue(current_task)
            
            
            if self.time > current_task.deadline:
                print(f"Time {self.time}: Task {current_task.id} missed deadline")
                self.DMAlogs.append(('D',current_task.id,self.time))
                break

        return self.parseLogList()
        
    def parseLogList(self):
        jobDict = dict()
        # print()
        # print(self.DMAlogs)
        # print()
        myLogs = [] #(Task,start,end,note)
        for dmaLog in self.DMAlogs:
            # count job num
            if dmaLog[1] not in jobDict:
                jobDict[dmaLog[1]] =1
            
            logIndex = self.DMAlogs.index(dmaLog)
            if dmaLog[0] != "C":
                if logIndex == 0 :
                    myT = MyTask(dmaLog[1],0,0,jobNum=jobDict[dmaLog[1]])
                    myLogs.append((myT,0,1,''))
                else:
                    lastLogIndex = len(myLogs)-1
                    if self.DMAlogs[logIndex][1] == myLogs[lastLogIndex][0].id and myLogs[lastLogIndex][0].jobNum == jobDict[dmaLog[1]]:
                        tmp = list(myLogs[lastLogIndex])
                        tmp[2] = dmaLog[2]+1
                        myLogs[lastLogIndex] = tuple(tmp)
                    else:
                        myT = MyTask(dmaLog[1],0,0,jobNum=jobDict[dmaLog[1]])
                        myLogs.append((myT,dmaLog[2] ,dmaLog[2],''))
            

            if dmaLog[0] == "C":
                # tmp = list(myLogs[lastLogIndex])
                # tmp[2] += 1
                # myLogs[lastLogIndex] = tuple(tmp)
                jobDict[dmaLog[1]] +=1
            elif dmaLog[0] == "D":
                tmp = list(myLogs[len(myLogs)-1])
                tmp[3] = "DEADLINE"
                myLogs[lastLogIndex] = tuple(tmp)


        return myLogs
            
def sched_dma( tasks:List[MyTask]):
    dmaTasks = list[DMATask]()
    for task in tasks:
        dmaTasks.append(DMATask(task.id,task.releaseTime,task.period,task.executionTime,task.deadline))
    scheduler = DMAScheduler(dmaTasks)
    return scheduler.run()

