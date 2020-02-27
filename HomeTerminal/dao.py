import logging
from datetime import datetime, timedelta

from .models import (Api_Key, FM4_Category, FM4_Item, Homework_Main, Message,
                     Table_Updates, User, User_Settings, db)
from .utils import Notification, hash_str


class RowAlreadyExists(Exception):
    pass

class RowDoesNotExist(Exception):
    pass

class AlreadyUpToDate(Exception):
    pass


def mark_table_updated(table_name):
    """
    Change a the update time table row,
    uses utc time

    args:
        just_creating : if the row already exists will not update the datetime
    """
    if Table_Updates.query.filter_by(table_name=table_name).scalar():
        new_row = Table_Updates.query.filter_by(table_name=table_name)
        new_row.last_updated = datetime.utcnow()
    else:
        new_row = Table_Updates(table_name=table_name)
    db.session.add(new_row)
    db.session.commit()

def get_last_updated(table_name):
    """
    Returns the last time the table was updated,
    returns a datetime obj
    """
    sel_row = Table_Updates.query.filter_by(table_name=table_name).first()
    if sel_row:
        return sel_row.last_updated

def try_login_user(username, password):
    """
    returns user obj and sets last login date, if password and username match
    """
    the_user = User.query.filter_by(username=username, password=hash_str(password)).first()
    if the_user:
        the_user.lastlogin = datetime.now()
        db.session.add(the_user)
        db.session.commit()
        logging.debug(f"User Logged In {username}")
        return the_user

def new_account(username, password, birthday: datetime, ignore_duplicate=False):
    """
    creates a new account in the database
    """
    if User.query.filter_by(username=username).scalar():
        # if the username already exists
        if not ignore_duplicate:
            raise RowAlreadyExists(f"username already exists: {username}")
        else:
            return
    password = hash_str(password)

    new_user = User(username=username.lower(), password=password, birthday=birthday)
    db.session.add(new_user)
    db.session.add(User_Settings(username=username))
    db.session.commit()

def change_user_password(username, new_password, old_password):
    """
    returns user obj if password change was success
    """
    old_password = hash_str(old_password)
    new_password = hash_str(new_password)

    the_user = User.query.filter_by(username=username, password=old_password).first()

    if the_user:
        the_user.password = new_password
        db.session.add(the_user)
        db.session.commit()
        return the_user

def new_message(user_from, message):
    """
    adds a new message into database,
    returns message obj on success
    """
    the_message = Message(user_from=user_from, message=message)
    db.session.add(the_message)
    db.session.commit()
    return the_message

def remove_message(mess_id):
    """
    marks a message as removed in the database
    """
    the_message = Message.query.filter_by(id_=mess_id).first()
    if not the_message:
        raise RowDoesNotExist(f"message id {mess_id} does not exist")
    the_message.removed = 1
    db.session.add(the_message)
    db.session.commit()

def check_api_key(api_key):
    """
    Checks whether the api key given is valid
    """
    if Api_Key.query.filter_by(key=api_key).scalar():
        return True
    else:
        return False

def get_messages(removed=0, last_updated=None):
    """
    Returns the messages,
    if last_updated is datetime will raise
    AlreadyUpToDate if it is already up to date

    args:
        removed : whether to select removed entries or not
        last_updated : datetime obj or '%Y-%m-%d %H:%M:%S.%f'
    """
    if last_updated:
        last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
        #TODO: seperate this into a function?
        db_updated = get_last_updated(Message.__tablename__)
        if db_updated:
            if db_updated <= last_updated:
                raise AlreadyUpToDate()

    return Message.query.filter_by(removed=removed).all()

def get_homework_ordered(removed=0, last_updated=None):
    """
    Returns the homework,
    if last_updated is datetime will raise
    AlreadyUpToDate if it is already up to date

    args:
        removed : whether to select removed entries or not
        last_updated : datetime obj or '%Y-%m-%d %H:%M:%S.%f'
    """
    if last_updated:
        last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
        db_updated = get_last_updated(Homework_Main.__tablename__)
        if db_updated:
            if db_updated <= last_updated:
                raise AlreadyUpToDate()
    return Homework_Main.query.filter_by(removed=removed).order_by(Homework_Main.datedue).all()

def update_usersettings(username, hwm_notif=None, fm_notif=None, mess_notif=None):
    """
    updates the user settings,
    if no new settings were provided will not update,
    will return the usersettings obj

    args:
        username: the id of the users account
        hwm_notif, fm_notif, mess_notif: the new value
    """
    user_setting = User_Settings.query.filter_by(username=username).first()
    if not user_setting:
        raise RowDoesNotExist("User settings row does not exist")
    if hwm_notif:
        user_setting.hwm_notif = hwm_notif
    if fm_notif:
        user_setting.fm_notif = fm_notif
    if mess_notif:
        user_setting.mess_notif = mess_notif
    if hwm_notif and fm_notif and mess_notif:
        db.session.add(user_setting)
        db.session.commit()
    return user_setting

def get_fm4_expiring(days=7, count=False):
    """
    Will return the number of items that
    will expire between the days given

    args:
        days: used to compare between
        expiredate lessthan or equal to days after
        count: whether it should return the number of or the items
    """
    days_after = datetime.now() + timedelta(days=days)
    items = FM4_Item.query.filter(FM4_Item.expire_date <= days_after).filter_by(removed=0)
    if count:
        return items.count()
    return items.all()

def get_notifations(username):
    """
    returns a generator of all notifications as Notification objects

    args:
        username : the username for getting different notifications
    """
    usr_setting = User_Settings.query.filter_by(username=username).first()
    if usr_setting.fm_notif == 1:
        fm_expiring = get_fm4_expiring(count=True)
        if fm_expiring > 0:
            yield Notification(f"You have {fm_expiring} expiring items in the freezer", "warning")
    if usr_setting.hwm_notif == 1:
        hw_due = Homework_Main.query.filter_by(removed=0).count()
        if hw_due > 0:
            yield Notification(f"You have {hw_due} outstanding homeworks", "warning")

def get_fm4_report(category=None, removed=0):
    """
    returns FM4_Item obj from database

    args:
        category : category to filter by, if None will return all
        removed : allows to display removed entries
    """
    if category:
        items = FM4_Item.query.filter_by(categoryname=category, removed=removed)
    else:
        items = FM4_Item.query.filter_by(removed=removed)

    return items.order_by(FM4_Item.expire_date).all()

def get_fm4_categories(removed=0):
    """
    returns all the fm4 categories
    """
    return FM4_Category.query.filter_by(removed=removed).all()

def get_fm4_item(id_):
    """
    returns the fm4 item,
    or raises RowDoesNotExist
    """
    fm_item = FM4_Item.query.filter_by(id_=id_).first()
    if not fm_item:
        raise RowDoesNotExist("Row with id {id_} does not exist")
    return fm_item

def edit_fm4_item(name, categoryname, quantity, expire=None, removed=0, id_=None):
    """
    Used to create an fm4 Item or edit an existing one,
    returns the edited item
    """
    if id_:
        fm_item = get_fm4_item(id_)
    else:
        fm_item = fm_item()

    fm_item.name = name
    if expire:
        fm_item.expire_date = expire
    if not FM4_Category.query.filter_by(name=categoryname).scalar():
        # create category if it does not exist
        db.session.add(FM4_Category(name=categoryname))
        db.session.commit()
    fm_item.categoryname = categoryname
    fm_item.quantity = quantity
    fm_item.removed = removed

    db.session.add(fm_item)
    db.session.commit()
    return fm_item
