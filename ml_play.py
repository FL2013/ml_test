"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import os.path as path
import numpy as np
import pickle
import random
def ml_loop(side: str):
    """
    The main loop for the machine learning process

    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```

    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    who_serve = 2
    filename = path.join(path.dirname(__file__),"save\SVMRegression_1.pickle")
    with open(filename, 'rb') as file:
        clf = pickle.load(file)
        
    def low_spe_fall(feature):
        y=415-feature[0,1]
        x=feature[0,0]+ y/feature[0,3]*feature[0,2]
        if(x>200): x=200-(x-200)
        if(x<0): x=x*(-1)
        return x
    def outer(x):
        while(x>200 or x<0):
            if(x>200):x=200-(x-200)
            else : x=x*(-1)
        return x
    def blo_dir():
        if(blo_ori_x > blo_now_x):
            return (24,0)
        else:
            return (0,24)
    def move_mode(feature,real_x):
        
        if(feature[0,3]>19):
            
            (a,b)=blo_dir()
            if(feature[0,2]>0):
                x0 = real_x + (415-260)
                x1 = real_x + (415-260) / feature[0,3] * (feature[0,3]+3)
                x2 = real_x - (415-260)
                x0=outer(x0)
                x1=outer(x1)
                x2=outer(x2)
                if(x0<feature[0,4]-a or x0>feature[0,4]+30+b):
                    
                    return 0
                elif(x1<feature[0,4]-a or x1>feature[0,4]+30+b):
                    
                    return 1
                elif(x2<feature[0,4]-a or x2>feature[0,4]+30+b):
                    
                    return 2
                else:
                    
                    return 0
            else:
                x0 = real_x - (415-260)
                x1 = real_x - (415-260) / feature[0,3] * (feature[0,3]+3)
                x2 = real_x + (415-260)
                x0=outer(x0)
                x1=outer(x1)
                x2=outer(x2)
                if(x0<feature[0,4]-a or x0>feature[0,4]+30+b):
                    
                    return 0
                elif(x1<feature[0,4]-a or x1>feature[0,4]+30+b):
                    
                    return 1
                elif(x2<feature[0,4]-a or x2>feature[0,4]+30+b):
                    
                    return 2
                
                else:
                    
                    return 0
        return random.randint(1,2)
        
    def ml_loop_for_1P(feature):
        fall = clf.predict(feature)
        
       
        if(feature[0,3]<10 and feature[0,1]>280 ): fall=low_spe_fall(feature)
        
        if fall < scene_info["platform_1P"][0]+10:
            return 2
        elif fall > scene_info["platform_1P"][0]+30:
            return 1
        else :
            real_x = feature[0,0] + (415-feature[0,1]) / feature[0,3] * feature[0,2]
            real_x = outer(real_x)
            if(feature[0,1]+feature[0,3]>=415 and real_x<190 and real_x>10):
                 if real_x < scene_info["platform_1P"][0]+5:
                     return 2
                 elif real_x > scene_info["platform_1P"][0]+25:
                     return 1
                 else:
                     return move_mode(feature,real_x)
            else:
                return 0
        
    
            
    # 2. Inform the game process that ml process is ready
    blo_ori_x = 0
    blo_now_x = 0 
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()
        feature = []
        feature.append(scene_info["ball"][0])
        feature.append(scene_info["ball"][1])
        feature.append(scene_info["ball_speed"][0])
        feature.append(scene_info["ball_speed"][1])
        feature.append(scene_info["blocker"][0])
        feature.append(scene_info["blocker"][1])
        feature.append(who_serve)        
        feature = np.array(feature)
        feature = feature.reshape((-1,7))
        
        blo_ori_x = blo_now_x
        blo_now_x = scene_info["blocker"][0]
        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False
            who_serve = 2
            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
            who_serve = 1
        else:
            if side == "1P":
                command = ml_loop_for_1P(feature)
            

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})