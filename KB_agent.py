from agents import *
from random import *
from random import seed
from logic import*
from utils import*
from notebook import psource
import logic_based_move
from collections import Counter
class Mine(Thing):
    pass
class L0(Thing):
    pass
class L1(Thing):
    pass
class L2(Thing):
    pass
class Field(XYEnvironment):
    def __init__(self, agent):  
        super().__init__(25,2)
    
        self.agent = agent
        self.kb = PropKB() # The robot's knowledge base which is an object of PropKB, it is used by the logic based agent.
        self.visited_rooms = [0] # A set of room locations which have been visited by the robot so far.
                                   # Each location is a pair of column and row, e.g., visited_rooms = {(1,3), (1,2), (2,3)}
         # A set of room locations currently available, but may or may not be directly accessible to the robot.
        self.waterguns=2
        self.gameover = False
        self.mine_rooms = []
        self.location_in=0
        self.L0_rooms = []
        self.L1_rooms=[]
        self.L2_rooms=[]
        self.mine_generator()
        
    def percept(self, agent):
        return self.list_things_at(agent.location)
    def mine_generator(self):
        temp=0
        seed(2)
        sequence = [i for i in range(1,24)]
        mine_loc=random.sample(sequence, 8)
        
        for loc in mine_loc:
            self.add_thing(Mine(),[loc,0])
            self.mine_rooms.append(loc)

        if (1) in self.mine_rooms:
            temp+=1
            
        if temp==0:
            self.add_kb(26,0)
        if temp==1:
            self.add_kb(27,0)
            
        for x in range(0,25):
            self.show_labels(x)
            
        for x in range(0,25):
            if x in self.L0_rooms:
                y="0"
            if x in self.L1_rooms:
                y="1"
            if x in self.L2_rooms:
                y="2"
            if x in self.mine_rooms:
                y="M"
            print(y, end=", ")
            
        print(sep="\n")  
        for x in range(0,25):
            print(x, end=", ")
            
        print(sep="\n")  
        print(sep="\n")  
         
        
    def random_room(self, column, row):
        available_rooms=[]
        for each_s in range(0,25):
                if each_s not in self.visited_rooms:
                    available_rooms.append(each_s)
        new_room=random.sample(available_rooms,1)[0]
        
        return new_room
    
    def check_safety(self, location):
      
        _mine_expr = expr("~M%d"%(location))
        
       
        return pl_resolution(self.kb,_mine_expr)   

    def next_position(self, location):
        
        new_room = 0
        for each_s in range(0,25):
            if each_s not in self.visited_rooms:
                
                if self.check_safety(each_s): 
                    new_room = each_s
                    break
        if new_room == 0:
            new_room=self.random_room(self, location)
            print("Agent randomly generated the location")
        return new_room 
    
    def show_labels(self,location):
        temp=0
        if location == 0:
            
            if (location + 1) in self.mine_rooms:
                temp=1
        elif location == 24:
            if (location - 1) in self.mine_rooms:
                temp=1
        else:
            
            if (location - 1) in self.mine_rooms:
                temp+=1
            if (location + 1) in self.mine_rooms:
                temp+=1
                
        if temp==0:
            self.add_thing(L0(),[location,0])
            self.L0_rooms.append(location)
        if temp==1:
            self.add_thing(L1(),[location,0])
            self.L1_rooms.append(location)
        if temp==2:
            self.add_thing(L2(),[location,0])
            self.L2_rooms.append(location)
            
    
    def show_position(self,location):
        print("Agent move to location ",location)
        if location in self.mine_rooms:
            self.waterguns-=1
            self.add_kb(location,0)
            print("One water gun is destroyed because there is a mine")
        else:
            if location in self.L0_rooms:
                print("Label is 0")
            if location in self.L1_rooms:
                print("Label is 1")
            if location in self.L2_rooms:
                print("Label is 2")
        print(end="\n")
  

    def move(self, location):
        
     
        if location not in self.visited_rooms:
            self.visited_rooms.append(location)     
            self.location_in = location 
            
            self.show_position(location)
            self.add_kb(location,1)
        return 
    
            
    def step(self):
       
        # Check if the game is over
        if self.waterguns == 0:
            print("Two water guns have consumed and operation is ended")
            self.gameover=True
            return
        elif len(self.visited_rooms)==17:
            print("All the rooms have been visited and operation is ended")
            self.gameover=True
            return
        else:
            print("Agent is in location ",self.location_in)
            next_room=self.next_position(self.location_in)
            self.move(next_room)
        
    def is_done(self):
       
        return self.gameover

    def run(self, steps=25):
        """Run the Environment for given number of time steps."""
        for step in range(steps):
            if self.is_done():
                return
            
            self.step()

    def add_kb(self,x,y):
        expression=''
        if y==0:
            if x==26:  
                expression = expr("~M%d & ~M%d"%(0,1)) 
                expression = expr("~M%d"%(24))
                self.kb.tell(expr(expression))
            
            if x==27:  
                expression = expr("~M%d & M%d"%(0,1))
                expression = expr("~M%d"%(24))
                self.kb.tell(expr(expression))
            else:
                expression = expr("M%d"%(x))       
                self.kb.tell(expr(expression))
                
        if y==1:
            if x==0:
                if x in self.L0_rooms:
                    expression = expr("~M%d"%(x+1))
                if x in self.L1_rooms:
                    expression = expr("M%d"%(x+1))
                self.kb.tell(expr(expression)) 
            
            elif x==24:
                if x in self.L0_rooms:
                    expression = expr("~M%d"%(x-1))
                if x in self.L1_rooms:
                    expression = expr("M%d"%(x-1))
                self.kb.tell(expr(expression)) 
                
            else:
                if x in self.L0_rooms:
                    expression = expr("~M%d & ~M%d"%(x-1,x+1))
                if x in self.L1_rooms:
                    expression = expr("M%d | M%d"%(x-1,x+1))
                if x in self.L2_rooms:
                    expression = expr("M%d & M%d"%(x-1,x+1))
                self.kb.tell(expr(expression)) 
        

class Man(Agent):
    location = [0,1]
    def program(percepts):
        print(percepts)
        return input()
man=Man(program)
field=Field(man)
field.add_thing(man,[0,1])
field.run()