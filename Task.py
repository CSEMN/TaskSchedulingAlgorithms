class Task:

    def __init__(self,id,p,e,r = 0,d=-1,jobNum=1):
        self.id = id
        self.jobNum = jobNum
        self.period = p
        self._originalRelease = r
        self._originalDeadline= d
        self.releaseTime =  (self.period * (self.jobNum-1)) + r 
        self.executionTime = e
        if d == -1 :
            self.deadline = (self.period * (self.jobNum-1)) + p
        else:
            self.deadline = (self.period * (self.jobNum-1)) + d
        self.remainingTime = self.executionTime
        
    
    def run(self,runTime,systemTime):
        if(runTime+ systemTime > self.deadline):
            raise Exception("Deadline Error",f"Task {self.id}(Job {self.jobNum}) excedded its deadline")
        else:
            self.remainingTime -= runTime
        return self.remainingTime
    
    def get_next_job(self):
        return Task(id=self.id,p=self.period,e=self.executionTime,r=self._originalRelease,d=self._originalDeadline,jobNum=self.jobNum+1)