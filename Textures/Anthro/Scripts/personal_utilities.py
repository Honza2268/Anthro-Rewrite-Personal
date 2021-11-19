def sort_dict_by_value(dict, reverse=False):
    return {k: v for k,v in sorted(dict.items(), key=lambda item: item[1], reverse=reverse)}