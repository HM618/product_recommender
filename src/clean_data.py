import pandas as pd

def get_data():
    products = pd.read_csv('data/updated_product_sample.csv')
    return products

#null values per column out of 300,000:
# vendor_variant_id                    0
# vendor_id                            0
# product_title                        0
# product_description              83250
# vendor_name                          0
# taxonomy_name                        1
# taxonomy_id                          1
# brand_id                         48685
# weblink                              0
# sku                              12748
# upc                              61755
# color                           185483
# material                        283580
# pattern                         298916
# size                            298151
# weight                          299895
# dimensions                       44810
# outer_depth                     287290
# outer_width                     287389
# outer_height                    294382
# is_returnable                        0
# item_level_shipping_rate        300000 DROP
# ship_surcharge                       0
# is_assembly_required                 0
# is_hidden                       300000 DROP
# is_user_hidden                  300000 DROP
# is_feed                              0
# last_feed_sync                   20174
# vendor_variant_collection_id    300000 DROP
# vendor_variant_group_id         300000 DROP
# image_url                       246136
# commission_tier                      0 #['Gold', 'Silver', 'Zero', 'Platinum', 'Bronze']
# inventory_type                       0 # regular vs custom
# division                         16907 # similar to category, broader
# category                            46
# price                             7775
# sale_price                      292247

#drop columns with all null values
for col in products.columns:
    if products[col].isnull().sum() == 300000:
        products.drop(col, axis=1, inplace=True)

#do I need these?
for col in ['last_feed_sync','outer_depth','outer_width','outer_height','weight']:
    products.drop(col, axis=1, inplace=True)

#drop rows without a price (7775)
products = products[products.price.isnull() == False]

#replace " in color, dimension and size columns
products['color'] = products['color'].replace('"','',inplace=True)

#fill in sales price with price if not on sale
#find an easier way to do this?
products['price_diff'] = products.price - products.sale_price
products.price_diff.fillna(0,inplace=True)
products.sale_price = products.price - products.price_diff
products.drop('price_diff',axis=1, inplace=True)

#replaces erraneous " in color col
products.color.replace('"','', inplace=True)

#fill na with other
for col in ['product_description','color','taxonomy_name','material','pattern','division','category']:
     products[col].fillna('other',inplace=True)

#deal with the UTF8 encoded characters
strings = ['product_title','product_description','vendor_name','taxonomy_name','color','material','pattern','commission_tier','inventory_type','division','category']
for col in strings:
    products[col] = products[col].apply(unidecode)

#split df into has nulls and doesn't have nulls
products_w_na = products[['brand_id','sku','upc','size','dimensions','image_url']].copy()
products_wo_na = products.copy()
products_wo_na.drop(['brand_id','sku','upc','size','dimensions','image_url'],axis=1, inplace=True)

products_w_na.to_csv('/Users/Kelly/galvanize/capstones/mod2/data/products_w_na.csv')
products_wo_na.to_csv('/Users/Kelly/galvanize/capstones/mod2/data/products_wo_na.csv')
