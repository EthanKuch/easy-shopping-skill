from mycroft import MycroftSkill, intent_file_handler
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
# import removes_context
from mycroft.skills.context import removes_context



##### ---------------- Path variable ---------------- ####
LOGSTR = '********************====================########## '
# 'NO TEST': use the image taken by the camera
# 'TEST': use the image in /photo folder, 
# In both mode, camera will work normally, i.e. take the photo, save the photo
# MODE = 'NO TEST'
MODE = 'TEST'
# need to be changed
IMAGE_STORE_PATH = '/opt/mycroft/skills/easy-shopping-skill/photo/'
# need to be changed
TEST_IMAGE_PATH_MULTI = '/opt/mycroft/skills/easy-shopping-skill/testPhoto/multi.jpeg'
# need to be changed
TEST_IMAGE_PATH_HAND = '/opt/mycroft/skills/easy-shopping-skill/testPhoto/2.jpeg'

####### ------------------------------------------------   ################


class EasyShopping(MycroftSkill):
    def _init_(self):
        MycroftSkill.__init__(self)
        self.category_str = ''
        self.color_str = ''
        self.brand_str = ''
        self.kw_str = ''
        self.img_multi = ''
        self.img_hand = ''
        self.log.info(LOGSTR + "_init_ EasyShoppingSkill")
        
        
    @intent_file_handler('shopping.easy.intent') 
    def handle_shopping_easy(self, message):
        self.speak_dialog('shopping.easy')
    
    
    ### CHeck is there any goods that matches category ###
    @intent_handler('is.there.any.goods.intent')
    def handle_is_there_any_goods(self, message):
        # in real application, label_str and loc_list will return from CV API
        label_list = [['milk', 'drink', 'bottle'], ['milk', 'drink', 'bottle']]
        loc_list = ['left top', 'right top']

        category_label = message.data.get('category')
        detected = 0

        for i in range(len(label_list)):
            label_str = generate_str(label_list[i])
            label_str = label_str.lower()

            if category_label is not None:
                if category_label in label_str:
                    self.speak_dialog('yes.goods',
                                {'category': category_label,
                                'location': loc_list[i]})
                    detected = 1
                    break
            else:
                continue

        if detected == 0:
            self.speak_dialog('no.goods',
            {'category': category_label})
    #### View Goods Intent ####    
    @intent_handler('view.goods.intent')
    def handle_view_goods(self, message):
        self.speak_dialog('take.photo')
        self.img_multi = ''
        self.img_hand = ''

        # suppose we use camera to take a photo here, 
        # then the function will return an image path
        self.img_multi = TEST_IMAGE_PATH_MULTI

        self.speak('I find some goods here, you can ask me whatever goods you want.')

        ### Checking goods ###
    @intent_handler('is.there.any.goods.intent')
    def handle_is_there_any_goods(self, message):
        if self.img_multi == '':
            self.handle_no_context1(message)

        else:
            # call cv api, and get result. 
            try:
                self.log.info(LOGSTR + 'actual img path')
                self.log.info(self.img_multi)
                if MODE == 'TEST':
                    self.log.info(LOGSTR + 'testing mode, use another image')
                    self.img_multi = TEST_IMAGE_PATH_MULTI

                objectlist = getObjLabel.getObjectsThenLabel(self.img_multi)
                label_list = []
                loc_list = []
                detected = 0

                category_label = message.data.get('category')

                for obj in objectlist['objectList']:
                    label_list.append(obj['name'])
                    loc_list.append(obj['loc'])
            
                if category_label:
                    for i in range(0,len(label_list)):
                        label_str = generate_str(label_list[i])
                        label_str = label_str.lower()
                
                        if category_label is not None:
                            if category_label in label_str:
                                self.speak_dialog('yes.goods',
                                            {'category': category_label,
                                            'location': loc_list[i]})
                                detected = 1
                                break
                        else:
                            continue

                if detected == 0 and category_label:
                    self.speak_dialog('no.goods',
                    {'category': category_label})

                    
    ## Checking if is there context ###
    # firstly create do.you.want.to.take.a.photo.dialog 
    def handle_no_context1(self, message):
        self.speak('Please let me have a look at what\'s in front of you first.')
        # add prompts
        take_photo = self.ask_yesno('do.you.want.to.take.a.photo') # This calls .dialog file.
        if take_photo == 'yes':
            self.handle_view_goods(message)
        elif take_photo == 'no':
            self.speak('OK. I won\'t take photo')
        else:
            self.speak('I cannot understand what you are saying')
    
    #### Building Intent to view item in hand and ask for information ###
    @intent_handler(IntentBuilder('ViewItemInHand').require('ViewItemInHandKeyWord'))
    def handle_view_item_in_hand(self, message):
        self.speak_dialog('take.photo')
        self.img_multi = ''
        self.img_hand = ''
    
        # suppose we use camera to take a photo here, 
        # then the function will return an image path
        self.img_hand = TEST_IMAGE_PATH_HAND

        # suppose we call CV API here to get the result, 
        # the result will all be list, then we use generate_str() to create string
        self.category_str = generate_str(['milk', 'bottle', 'drink'])
        self.brand_str = generate_str(['Dutch Lady', 'Lady'])
        self.color_str = generate_str(['white', 'black', 'blue'])
        self.kw_str = ' '.join(['milk', 'bottle', 'protein', 'pure', 'farm'])

        # set the context
        self.set_context('getDetailContext')

        # speak dialog
        self.speak_dialog('item.category', {'category': self.category_str})

    @intent_handler(IntentBuilder('AskItemCategory').require('Category').require('getDetailContext').build())
    def handle_ask_item_category(self, message):
        self.handle_ask_item_detail('category', self.category_str)

    @intent_handler(IntentBuilder('AskItemColor').require('Color').require('getDetailContext').build())
    def handle_ask_item_color(self, message):
        self.handle_ask_item_detail('color', self.color_str)

    @intent_handler(IntentBuilder('AskItemBrand').require('Brand').require('getDetailContext').build())
    def handle_ask_item_brand(self, message):
        self.handle_ask_item_detail('brand', self.brand_str)

    @intent_handler(IntentBuilder('AskItemKw').require('Kw').require('getDetailContext').build())
    def handle_ask_item_keywords(self, message):
        self.handle_ask_item_detail('keyword', self.kw_str)

    @intent_handler(IntentBuilder('AskItemInfo').require('Info').require('getDetailContext').build())
    def handle_ask_item_complete_info(self, message):
        if self.color_str == '':
            self.handle_ask_item_detail('category', self.category_str)
        else:
            self.speak_dialog('item.complete.info', {
                          'category': self.category_str, 'color': self.color_str})
        self.handle_ask_item_detail('brand', self.brand_str)
        self.handle_ask_item_detail('keyword', self.kw_str)

    @intent_handler(IntentBuilder('FinishOneItem').require('Finish').require('getDetailContext').build())
    @removes_context('getDetailContext')
    def handle_finish_current_item(self, message):
        self.speak('Got you request. Let\'s continue shopping!')
        self.types_str = ''
        self.color_str = ''
        self.logo_str = ''
        self.kw_str = ''
        self.img_hand = ''
        self.img_multi = ''
    
    
    #### Insert no context ###
    @intent_handler(IntentBuilder('NoContext').one_of('Category', 'Color', 'Brand', 'Kw', 'Info'))
    def handle_no_context2(self, message):
        self.speak('Please let me have a look at what\'s in your hand first.')

        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
 ## Stop before 4       
        
def create_skill(): return EasyShopping()        
