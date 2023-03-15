from mycroft import MycroftSkill, intent_file_handler






class EasyShopping(MycroftSkill):
    def _init_(self):
        MycroftSkill.__init__(self)
        
        
    @intent_file_handler('shopping.easy.intent') 
    def handle_shopping_easy(self, message):
        self.speak_dialog('shopping.easy')
