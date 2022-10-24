#!/usr/bin/env python

import rospy
import smach
import smach_ros
import random
import time
from cluedo.srv import Hint, HypothesisID
from armor_msgs.msg import *
from armor_msgs.srv import *
from armor_api.armor_client import ArmorClient


suspects = ["Miss Scarlett","Mrs White","Mrs Peacock", "Reverend Green", "Professor Plum", "Colonel Mustard"]
weapons = ["Dagger", "Candle Stick", "Revolver", "Rope", "Lead Pipe", "Spanner"]
rooms = ["Hall", "Lounge","Dining Room", "Kitchen", "Ball Room" "Conservatory", "Billiard Room", "Library", "Study"]

#######################################USARE NESTED LIST. COGLIONA.
client = ArmorClient("cluedo", "ontology")
hp0 = list()
hp1 = list()
hp2 = list ()
hp3 = list ()
hp4 = list ()
hp5 = list ()
hp6 = list ()
hp7 = list ()
hp8 = list ()
hp9 = list ()  

def make_ind_of_class_disjoint (class_name):
        """
        Disjoint all individuals of a class.
    
        Args:
            ind_name (str): individual to be added to the class.
            class_name (str): individual will be added to this class. It will be created a new class if it does not exist.
    
        Returns:
            bool: True if ontology is consistent, else False
    
        Raises:
            armor_api.exceptions.ArmorServiceCallError: if call to ARMOR fails
            armor_api.exceptions.ArmorServiceInternalError: if ARMOR reports an internal error
    
        Note:
            It returns the boolean consistency state of the ontology. This value is not updated to the last operation
            if you are working in buffered reasoner or manipulation mode!
        """
        try:
            res = client.call('DISJOINT', 'IND', 'CLASS', [class_name])
    
        except rospy.ServiceException as e:
            raise ArmorServiceCallError(
                "Service call failed upon adding individual {0} to class {1}: {2}".format(ind_name, class_name, e))
    
        except rospy.ROSException:
            raise ArmorServiceCallError("Cannot reach ARMOR client: Timeout Expired. Check if ARMOR is running.")
    
        if res.success:
            return res.is_consistent
        else:
            raise ArmorServiceInternalError(res.error_description, res.exit_code)
            

class hint_gen:

      def __init__(self):
          rospy.wait_for_service('hint_generator')
          self.srv_hint_client = rospy.ServiceProxy('hint_generator', Hint)
      
      def hint_client(self, ID):
          global res
          try:  
              self.res = self.srv_hint_client (ID)
              print ('Your hint is:', self.res.hint, 'and the ID is:', self.res.myID)
              return self.res
          except rospy.ServiceException as e:
              print("Service call failed: %s"%e)

class oracle_query:

      def __init__(self):
          rospy.wait_for_service('compare_hypothesis')
          self.srv_oracle_client = rospy.ServiceProxy('compare_hypothesis', HypothesisID)
      
      def oracle_client(self, myID):
          global oracle_res
          try:  
              self.oracle_res = self.srv_oracle_client (myID)
              print ('Your hypothesis is:', self.oracle_res)
              return self.oracle_res
          except rospy.ServiceException as e:
              print("Service call failed: %s"%e)

def add_hypothesis (ID, item):
    global HP
    
    HP = "HP"+str(ID)
    myID = rospy.get_param (HP) #CONSISTENT
    client.manipulation.add_ind_to_class(HP, "HYPOTHESIS")
    client.manipulation.add_dataprop_to_ind("hasID", "HP"+str(ID), "STRING", myID)
    if item in suspects:
        client.manipulation.add_objectprop_to_ind("who", HP, item)
    elif item in rooms:
        client.manipulation.add_objectprop_to_ind("where", HP, item)
    elif item in weapons:
        client.manipulation.add_objectprop_to_ind("what", HP, item)
    #client.utils.apply_buffered_changes()
    time.sleep (3)
    #client.utils.sync_buffered_reasoner()
    client.utils.apply_buffered_changes()
    time.sleep (3)
    client.utils.sync_buffered_reasoner()
    return ()
 ############## VEDERE COME FARE LE LISTE IN MANIERA CHE CORRISPONDANO ALL'ID, CRISTO JESOO ########

def storage_hypo (ID, item, hpi):
    if item not in hpi:
       hpi.append (item) 
       print (hpi , 'The ID is:', ID) 
    return ()
 ##################################################################################################
def sort_win_sequence (hp):
    for i in range(len(hp)):
           if hp[i] in suspects:
              killer = hp[i]
           if hp[i] in weapons:
              weapon = hp[i]
           if hp[i] in rooms:
              room = hp[i]
    return killer, weapon, room  
 
def winning_sequence (myID):
    if myID == '0000':
       [killer, weapon, room] = sort_win_sequence (hp0)
    elif myID == '0001':
       [killer, weapon, room] = sort_win_sequence (hp1)     
    elif myID == '0002':
       [killer, weapon, room] = sort_win_sequence (hp2)
    elif myID == '0003':
       [killer, weapon, room] = sort_win_sequence (hp3)
    elif myID == '0004':
       [killer, weapon, room] = sort_win_sequence (hp4)
    elif myID == '0005':
       [killer, weapon, room] = sort_win_sequence (hp5)
    elif myID == '0006':
       [killer, weapon, room] = sort_win_sequence (hp6)
    elif myID == '0007':
       [killer, weapon, room] = sort_win_sequence (hp7)
    elif myID == '0008':
       [killer, weapon, room] = sort_win_sequence (hp8)
    elif myID == '0009':
       [killer, weapon, room] = sort_win_sequence (hp9)                    
    return killer, weapon, room
# define state1 EXPLORATION
class Exploration(smach.State):
    def __init__(self):
        smach.State.__init__(self, 
                             outcomes=['go_around','check_hypo',],
                             #input_keys=['foo_counter_in'],
                             output_keys=['myID'])

    def execute(self,userdata):
        rospy.loginfo('Executing state Exploration')
        global ID
        get_random_room = random.choice(rooms)
        print ("I'm going to the:", get_random_room)
        time.sleep(5)
        ID = random.randint(0,9)
        print (ID)
        # return (ID)
        hint = hint_gen ()
        res = hint.hint_client(ID)
        userdata.myID=res.myID
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',res.myID)
        add_hypothesis (ID, res.hint)
        if HP == 'HP0' :
           storage_hypo (ID, res.hint, hp0)
           if len (hp0) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'
        elif HP == 'HP1' :
           storage_hypo (ID, res.hint, hp1)
           if len (hp1) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'
        elif HP == 'HP2' :
           storage_hypo (ID, res.hint, hp2)
           if len (hp2) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'
        elif HP == 'HP3' :
           storage_hypo (ID, res.hint, hp3)
           if len (hp3) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'
        elif HP == 'HP4' :
           storage_hypo (ID, res.hint, hp4)
           if len (hp4) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'
        elif HP == 'HP5' :
           storage_hypo (ID, res.hint, hp5)
           if len (hp5) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'
        elif HP == 'HP6' :
           storage_hypo (ID, res.hint, hp6)
           if len (hp6) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'
        elif HP == 'HP7' :
           storage_hypo (ID, res.hint, hp7)
           if len (hp7) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'
        elif HP == 'HP8' :
           storage_hypo (ID, res.hint, hp8)
           if len (hp8) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'
        else :
           storage_hypo (ID, res.hint, hp9)
           if len (hp9) >= 3 :
              return 'check_hypo'
           else:
              return 'go_around'     

# define state Query
class Query(smach.State):
    def __init__(self):
    
        smach.State.__init__(self, 
                             outcomes=['outcome1'],
                             input_keys=['bar_counter_in'])
        
    def execute(self, userdata):
        rospy.loginfo('Executing state QUERY')
        #rospy.loginfo('Counter = %f'%userdata.bar_counter_in)        
        return 'outcome1'
        
#define state Oracle
class Oracle (smach.State):
    def __init__(self):
        smach.State.__init__(self, 
                             outcomes=['go_around', 'end'],
                             input_keys=['myID'])
    def execute(self, userdata):
        rospy.loginfo('Executing state Oracle')
        print ("I'm going to the Oracle room")
        #time.sleep (5)
        print ('questo è:', userdata.myID)
        oracle = oracle_query()
        #print ('questo è:', myID)
        res= oracle.oracle_client(userdata.myID)
        print (res.success)
        if res.success :
           print ('Your hypotesis is:', res.success)
           [killer, weapon, room] = winning_sequence (userdata.myID)
           # mettere qualcosa che faccia da storage di queste informazioni
           print ('It was:', killer,' with:', weapon, 'in the:', room)   
           client.utils.save_ref_with_inferences("/root/Desktop/inferred_cluedo.owl")     
           return 'end' #end of the game
        else:
           print('Your hypotesis is:',res.success)
           print ('go on with your research')
           return 'go_around'                     


def main():
    rospy.init_node('cluedo_fsm')
    
    make_ind_of_class_disjoint ("PERSON")
    make_ind_of_class_disjoint ("WEAPON")
    make_ind_of_class_disjoint ("PLACE")
    #make_ind_of_class_disjoint ("HYPOTHESIS")
    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['outcome4'])
    sm.userdata.sm_counter = ''
    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('EXPLORATION', Exploration(), 
                               transitions={'go_around':'EXPLORATION', 
                                            'check_hypo':'ORACLE'},
                               remapping={ 
                                          'myID':'sm_counter'})
        smach.StateMachine.add('QUERY', Query(), 
                               transitions={'outcome1':'QUERY'})
                               #remapping={'bar_counter_in':'sm_counter'})
                               
        smach.StateMachine.add('ORACLE', Oracle(), 
                               transitions={'go_around':'EXPLORATION', 
                                            'end' : 'outcome4'},
                               remapping={'myID':'sm_counter'})
    # Execute SMACH plan
    sm.execute()
    
    rospy.spin()
    #sis.stop()


if __name__ == '__main__':
    main()
