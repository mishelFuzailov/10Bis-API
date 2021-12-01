from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import flask
from flask import request
from flask_cors import CORS
import requests

app = flask.Flask(__name__)
CORS(app)
menu = None
CATEGORIES_LIST = "categoriesList"
CATEGORY_NAME = "categoryName"
DISH_LIST = 'dishList'
DISH_ID = "dishId"
ID = "id"
DISH_NAME = "dishName"
NAME ="name"
DISH_DESCRIPTION = "dishDescription"
DESCRIPTION = "description"
DISH_PRICE = "dishPrice"
PRICE = "price"
DRINKS = "drinks"
PIZZAS = "pizzas"
DESSERTS = "desserts"



@app.route("/drinks", methods=["GET"])
def getDrinks():
    return getElementsFromCategory(category_name=DRINKS)


@app.route("/drink/<id>", methods=["GET"])
def getDrinkByID(id):
    return getElementsFromCategory(category_name=DRINKS, specific_id=int(id))


@app.route("/pizzas", methods=["GET"])
def getPizzas():
    return getElementsFromCategory(category_name=PIZZAS)


@app.route("/pizza/<id>", methods=["GET"])
def getPizzaByID(id):
    return getElementsFromCategory(category_name=PIZZAS, specific_id=int(id))


@app.route("/desserts", methods=["GET"])
def getDesserts():
    return getElementsFromCategory(category_name=DESSERTS)


@app.route("/dessert/<id>", methods=["GET"])
def getDessertByID(id):
    return getElementsFromCategory(category_name=DESSERTS, specific_id=int(id))


@app.route("/order", methods=["POST"])
def postOrder():
    body = request.json
    total_sum = 0
    for category,id_list in body.items():
        total_sum += getSumByCategoryAndIDS(category, id_list)
    return {PRICE: total_sum}


def getSumByCategoryAndIDS(category_name, id_list_str):
    """
    This function calculate the price of the products in the order from one category
    :param category_name: name of the category
    :param id_list_str: the id's of the products in the order
    :return: peice of products
    """
    price = 0
    # get all items of the category
    category_items = getCategoryFromMenu(category_name)
    # for each id
    for id_str in id_list_str:
        id = int(id_str.split('_')[1])
        element = getElementsFromCategory(category_items=category_items, specific_id=id)
        if element != {}:
            # if the id is exist
            price += element[PRICE]
    return price


def getCategoryFromMenu(category_name):
    """
    Get all items of the category from the menu
    :param category_name: category name
    :return: items
    """
    if menu is None:
        getMenu()
    for category in menu[CATEGORIES_LIST]:
        # find the category in the menu
        if category[CATEGORY_NAME].lower() == category_name.lower():
            return category[DISH_LIST]
    # if the category is not exist
    print(f"category name: {category_name} is not in the menu")


def getElementsFromCategory(category_name=None, category_items=None, specific_id=None):
    """
    Get the elements from category
    :param category_name: name
    :param category_items: dictionary of categories
    :param specific_id: ID of specific item
    :return: dictionary of the relevant items
    """
    if category_items is None:
        category_items = getCategoryFromMenu(category_name)
    elements_dict = {}
    # for each element on dishList, fins the id, name, description and price
    i = 1
    for cd in category_items:
        temp_dict = {ID: cd[DISH_ID], NAME: cd[DISH_NAME], DESCRIPTION: cd[DISH_DESCRIPTION],
                     PRICE: cd[DISH_PRICE]}
        if specific_id:
            if specific_id == cd['dishId']:
                return temp_dict
        else:
            elements_dict[i] = temp_dict
            i += 1
    return elements_dict


def getMenu():
    response = requests.get("https://tenbis-static.azureedge.net/restaurant-menu/19156_en")
    if response.status_code != 200:
        print(f"Error in get menu, status code:'{response.status_code}'(reason: '{response.reason}')")
    else:
        global menu
        menu = response.json()
        return menu


if __name__ == '__main__':
    background_scheduler = BackgroundScheduler()
    background_scheduler.add_job(func=getMenu, trigger="interval", seconds=86400)  # seconds in one day
    background_scheduler.start()

    atexit.register(lambda: background_scheduler.shutdown())  # when exiting the app
    app.run(port=5000, debug=True)
