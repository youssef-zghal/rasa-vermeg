from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class Actionsayphone(Action):
    def name(self) -> Text:
        return "action_say_phone"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker, 
            domain: Dict[Text,Any]) -> List[Dict[Text,Any]]:
        
        phone = tracker.get_slot("phone")

        if not phone:
            dispatcher.utter_message(text="sorry i dont know your phone number")
        else:
            dispatcher.utter_message(text=f"your phone number is {phone}")

        return []
    
 