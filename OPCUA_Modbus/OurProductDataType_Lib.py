from opcua import ua,  common
from opcua.common.type_dictionary_buider import DataTypeDictionaryBuilder, get_ua_class


class OurProduct() : 

    def create_structure(self,name) :
        return self.dict_builder.create_data_type(name)

    def complete_creation(self):
        self.dict_builder.set_dict_byte_string()

    def create_our_product_type(self) : 

        self.dict_builder = DataTypeDictionaryBuilder(self.server, self.my_namespace_idx, self.my_namespace_name, 'MyDictionary')
        self.ourproduct_name = 'OurProduct'
        self.ourproduct_data = self.create_structure(self.ourproduct_name)

        # add one basic structure
        self.pathitem_name = 'PathItem'
        self.pathitem = self.create_structure(self.pathitem_name)
        self.pathitem.add_field('NameOfStation', ua.VariantType.String)
        self.pathitem.add_field('PlannedStepNumber', ua.VariantType.Int32)
        self.pathitem.add_field('IsDoneSuccessful', ua.VariantType.Boolean)
        

        # add an advance structure which uses our basic structure
        self.ourproduct_data.add_field('DeliveryAddress', ua.VariantType.String)
        self.ourproduct_data.add_field('OrderID', ua.VariantType.Guid)
        self.ourproduct_data.add_field('OrderTime', ua.VariantType.DateTime)
        self.ourproduct_data.add_field('PartClassID', ua.VariantType.Guid)
        self.ourproduct_data.add_field('PartID', ua.VariantType.Guid)
        self.ourproduct_data.add_field('PathStack', self.pathitem,ua.Variant(self.pathitem, []) )# add simple structure as field
        self.ourproduct_data.add_field('PlannedDeliveryTime', ua.VariantType.DateTime)

        self.complete_creation()
        self.server.load_type_definitions()





   