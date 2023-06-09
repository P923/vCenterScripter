from pyVmomi import vim
__version__ = '1.0'

def list_obj(si: vim.ServiceInstance, type_obj: vim):
    """
    Get a list of object type_obj
    :param si: Connection to vCenter Server
    :param type_obj:  Set of type_obj names
    :return: a list of type_obj
    """
    content = si.RetrieveContent()
    container = content.rootFolder
    view_type = [type_obj]
    container_view = content.viewManager.CreateContainerView(container, view_type, True)
    return container_view.view


def list_obj_names(si: vim.ServiceInstance, type_obj: vim) -> set:
    """
    Get names of the type_obj in the vCenter
    :param type_obj: type, for example vim.VirtualMachine
    :param si: Connection to vCenter Server
    :return: Set of type_obj names
    """
    children = list_obj(si, type_obj)
    set_names = set()

    for child in children:
        try:
            name = child.summary.config.name
        except AttributeError:
            try:
                name = child.summary.name
            except AttributeError:
                name = child.name

        set_names.add(name)

    return set_names


def get_object(si: vim.ServiceInstance, type_obj: vim, name: str = ""):
    """
    Get an object of type_obj with a specified name
    :param si: Connection to vCenter
    :param type_obj: type, for example vim.VirtualMachine
    :param name: name
    :return: The type_object with the specified name
    """
    children = list_obj(si, type_obj)

    i = 0
    found = False
    child = children[i]
    number_children = len(children)
    while (not found) and (i < number_children):
        child = children[i]

        try:
            child_name = child.summary.config.name
        except AttributeError:
            try:
                child_name = child.summary.name
            except AttributeError:
                child_name = child.name

        if child_name == name:
            found = True
        else:
            i += 1

    if found:
        return child
    else:
        return None


def list_host_objects(objs) -> set:
    names = set()
    for obj in objs:
        found = False
        if hasattr(obj, 'name'):
            names.add(obj.name)
            found = True

        if hasattr(obj, 'device'):
            names.add(obj.device)
            found = True

        if not found and hasattr(obj, 'key'):
            names.add(obj.key)
    return names


def get_host_object(objs, name:str) -> set:
    for obj in objs:
        if hasattr(obj, 'name') and obj.name == name:
            return obj
        if hasattr(obj, 'device') and obj.device == name:
            return obj
        if hasattr(obj, 'key') and name in obj.key:
            return obj

    return None


