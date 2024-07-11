import i18n
def setup_translation():
    import hiddifypanel_bot
    i18n.load_path.append(hiddifypanel_bot.__path__[0]+'/translations')
    i18n.set('file_format', 'json')    
    i18n.set('skip_locale_root_data',True)
    i18n.set('filename_format', '{locale}.{format}')
    i18n.set('fallback','en')
    i18n.set('on_missing_translation',__on_missing__)
    i18n.set('placeholder_delimiter','$')

def __on_missing__(key,locale,**kwargs):
    if locale!='en':
        return i18n.t(key,'en',**kwargs)    
    return key

