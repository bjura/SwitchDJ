'''
Created on 22-08-2010

@author: Macias
'''
def get_xml_data(element,name):
    element= get_element(element,name)
    if element is None or not element.hasChildNodes(): return None
    return element.childNodes[0].data
def append_text_el(doc,element,name,data):
    el = doc.createElement(name)
    text = doc.createTextNode(str(data))
    el.appendChild(text)
    element.appendChild(el)
    return el
def get_element(element,name):
    elems = element.getElementsByTagName(name)
    if len(elems)==0:
        return None
    return elems[0]
    
valid_classes = {}

class XMLExporter(object):
    '''
    classdocs
    '''
    xml_init_fields = ()
    
    def get_xml_element(self,doc,name):
        el = doc.createElement(name)
        append_text_el(doc,el,"class_name",self.__class__.__name__)
        for f in self.xml_init_fields:
            val =self.__getattribute__(f)
            if val is None: val=''
            e = append_text_el(doc,el,f,val)
            if type(val)==int:
                e.setAttribute("type","int")
            elif type(val)==float:
                e.setAttribute("type","float")
        return el
    def init_from_xml_element(self,element,keys):
        for f in self.xml_init_fields:
            el =get_element(element, f)
            v=get_xml_data(element,f)
            if v is not None:
                if v=='': v=None
                keys[f]=v
                if el is not None and el.hasAttribute("type"):
                    ty = el.getAttribute("type")
                    if ty == "float": keys[f]=float(keys[f])
                    elif ty == "int": keys[f]=int(keys[f])
                    elif ty=='' and v==None: keys[f]=''
        self.init(**keys)
    @staticmethod
    def from_xml_element(element,**keys):
        class_name= get_xml_data(element,"class_name")
        if valid_classes.has_key(class_name):
            obj = valid_classes[class_name]()
            obj.init_from_xml_element(element,keys)
            return obj
        return None
    @staticmethod
    def add_class(class_):
        valid_classes[class_.__name__]=class_