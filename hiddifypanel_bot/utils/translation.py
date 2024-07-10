def setup_translation():
    import i18n
    import hiddifypanel_bot
    i18n.load_path.append(hiddifypanel_bot.__path__[0]+'/translations')
    i18n.set('file_format', 'json')    
    i18n.set('skip_locale_root_data',True)
    i18n.set('filename_format', '{locale}.{format}')
    i18n.set('placeholder_delimiter','$')