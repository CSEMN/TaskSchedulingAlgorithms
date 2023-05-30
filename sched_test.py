from Task import Task as MyTask
from math import ceil

def first_test(tasks:list[MyTask]):
    
    #Bound Test (Utility test)
    accUtil = 0
    for task in tasks:
        accUtil += task.executionTime / task.period
    accUtil = round(accUtil,2)
    k = len(tasks)
    bound = round(k * (2**(1/k) -1),2)
    if(accUtil<bound):
        result = True
    else:
        result = False
    return (result,accUtil,bound)

def second_test(tasks:list[MyTask]):
    #Completion-Time test
    results = list[bool]() 
    
    for task in tasks:
        if(tasks.index(task)==0):
            #first task always schedulable
            results.append(True)
            continue
        else:
            taskIndex = tasks.index(task)

            t=task.executionTime
            for i in range(taskIndex):
                t+=ceil(task.deadline/tasks[i].deadline) * tasks[i].executionTime 
            
            if( t <= task.deadline ):
                results.append(True)
            else:
                results.append(False)
                break
    return results

