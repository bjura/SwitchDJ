"""
Module that creates a model out of the media library stored in the file system.
Library that will be created has a two-level structure, that is, many different
categories, each containing many items.
Module provides also management system for library items marked as favourites.
"""
import os.path

from collections import namedtuple
import magic
import configobj

from pisak import res


class LibraryException(Exception):
    pass


class Category(object):
    """
    Category of items that share some common trait, i.e belong
    to the same folder etc.
    """
    def __init__(self, category_id, name):
        self.id = category_id
        self.name = name
        self.items = []
    
    def get_preview_path(self):
        """
        Get preview of the category assuming that its items
        have attribute named 'path'.

        :returns: path attribute of the first item or None
        """
        if len(self.items) > 0:
            return self.items[0].path

    def remove_item_by_path(self, item_path):
        """
        Remove item with the given path from the list of category items.

        :param item_path: path attribute of the item
        """
        for item in self.items:
            if item.path == item_path:
                self.items.remove(item)

    def get_item_by_path(self, item_path):
        """
        Get item with the given path from the list of category items.

        :param item_path: path attribute of the item

        :returns: item or None
        """
        for item in self.items:
            if item.path == item_path:
                return item


'''Single item from the media library.
Each one should be characterized by an unique id and path to the corresponding
file in the file system, with 'extra' being a container for
specific purpose attributes.
'''
Item = namedtuple("Item", ("id", "path", "extra"))


class FavouritesStore(object):
    """
    Container for managing items marked as favourite. List of their paths
    is stored in a file in res directory.
    """
    def __init__(self, path):
        self._favs_store = configobj.ConfigObj(path,
                                         encoding='UTF8')

    def get_all(self):
        """
        Get list of all favourite items. Before return, each record is examined
        if it does refer to an existing file in the file system. If negative,
        then it is removed from the list and such updated list is saved.

        :returns: list of paths to favourite items
        """
        favs = list(filter(lambda path: os.path.isfile(path),
                      (self._favs_store.get("favs") or [])))
        self.write(favs)
        return favs

    def write(self, favs):
        """
        Save the given list of items to the file. Save is done only if
        the given list differs from the list stored.

        :param favs: list of paths to favourite items
        """
        pre_favs = self._favs_store.get("favs")
        if favs != pre_favs:
            self._favs_store["favs"] = favs
            self._favs_store.write()

    def insert(self, path):
        """
        Insert one favourite item to the list. Item is represented by its path.

        :param path: path to the item
        """
        favs = self.get_all()
        if path not in favs:
            favs.append(path)
            self.write(favs)

    def remove(self, path):
        """
        Remove one favourite item from the list. If not in list then
        nothing happens.

        :param path: path to the item
        """
        favs = self.get_all()
        if path in favs:
            favs.remove(path)
            self.write(favs)

    def is_in(self, path):
        """
        Check if item with the given path has been marked as favourite.

        :param path: path to the item
        """
        return path in self.get_all()


class Library(object):
    """
    Library store. Contains lists with categories and items.

    :param path: path to the directory in the file system that
    library is located in
    :param accepted_types: list of file types that will be accepted and
    included as items while scanning the file system
    :param favs_store_path: path to the file that favourite items
    will be stored in
    :param favs_alias: alias for the category containing favourite items that
    may be displayed to user
    :param exec_for_all: callable that will be executed for each item found
    while scanning the file system
    """
    def __init__(self, path, accepted_types, favs_store_path=None,
                 favs_alias=None, exec_for_all=None):
        self.path = path
        self.accepted_types = accepted_types
        self.favs_store_path = favs_store_path
        self.favs_alias = favs_alias
        self.exec_for_all = exec_for_all
        self.favs_store = None
        self.categories = []
        self.items = []
        self._scan()

    def _scan(self):
        scanner = _Scanner(self)
        scanner.scan()

    def include_favs(self):
        """
        If there are any items marked as favourite, include them in the library
        by creating a separate, artificial folder for them with field "id"
        set to -1.
        """
        self.favs_store = FavouritesStore(self.favs_store_path)
        favs = self.favs_store.get_all()
        if favs:
            # category object for favourite items indexed as the -1
            category = self.get_category_by_id(-1)
            if not category:
                category = Category(-1, self.favs_alias)
                self.categories.insert(0, category)
            category.items.clear()
            for item in favs:
                item = self.get_item_by_path(item)
                if item:
                    category.items.append(item)
            if len(category.items) == 0:
                self.categories.remove(category)

    def add_item_to_favourites(self, path):
        """
        Add item with the given path to the favourites. If already marked as one,
        nothing happens.

        :param path: path to the item
        """
        if self.favs_store is None:
            return
        self.favs_store.insert(path)
        category = self.get_category_by_id(-1)
        if not category:
            category = Category(-1, self.favs_alias)
            self.categories.insert(0, category)
        if not category.get_item_by_path(path):
            item = self.get_item_by_path(path)
            if item:
                category.items.append(item)

    def is_in_favourites(self, path):
        """
        Check if the given item is in the favourites store already.
        
        :param path: path to the item
        """
        return self.favs_store.is_in(path)

    def remove_item_from_favourites(self, path):
        """
        Remove item with the given path from the favourites. If not in favourites,
        nothing happens.

        :param path: path to the item
        """
        if self.favs_store is None:
            return
        self.favs_store.remove(path)
        category = self.get_category_by_id(-1)
        if category:
            item = category.get_item_by_path(path)
            if item:
                category.items.remove(item)

    def get_category_by_id(self, category_id):
        """
        Get category with the given index.

        :param category_id: index of the category

        :returns: category or None
        """
        for category in self.categories:
            if category.id == category_id:
                return category

    def get_item_by_id(self, item_id):
        """
        Get item with the given index.

        :param item_id: index of the item

        :returns: item or None
        """
        for item in self.items:
            if item.id == item_id:
                return item

    def get_item_by_path(self, item_path):
        """
        Get item with the given path.

        :param item_path: path of the item

        :returns: item or None
        """
        for item in self.items:
            if item.path == item_path:
                return item

    def remove_item_by_path(self, item_path):
        """
        Remove item with the given index.

        :param item_path: path of the item
        """
        for item in self.items:
            if item.path == item_path:
                self.items.remove(item)


class _Scanner(object):
    def __init__(self, library):
        self.library = library
        self.magic = magic.open(magic.MIME_TYPE | magic.SYMLINK)
        self.magic.load()

    def get_item_paths(self):
        """
        Get paths to the all items in the library.

        :returns: set with paths to all items
        """
        return set([item.path for item in self.library.items])

    def scan(self):
        """
        Scan the library directory for all items.
        """
        next_cat_id = 0
        next_item_id = 0
        path_generator = os.walk(self.library.path)
        for current, _subdirs, files in path_generator:
            if current.startswith("."):
                continue
            category_name = self._generate_category_name(current)
            new_category = Category(next_cat_id, category_name)
            for item_path in [os.path.join(current, name) for name in files]:
                if not self._test_file(item_path):
                        continue
                new_item = Item(next_item_id, item_path, {})
                if self.library.exec_for_all is not None:
                    self.library.exec_for_all(new_category, new_item, item_path,
                                        current, os.path.split(current)[-1],
                                        files)
                new_category.items.append(new_item)
                self.library.items.append(new_item)
                next_item_id += 1
            if len(new_category.items) > 0:
                self.library.categories.append(new_category)
                next_cat_id += 1

    def _generate_category_name(self, path):
        if path == self.library.path:
            return os.path.split(path)[1]
        else:        
            return path.partition(self.library.path)[2][1:]
    
    def _test_file(self, path):
        file_type = self.magic.file(path)
        return file_type in self.library.accepted_types
