'''
Created on 18.04.2011

@author: seriy
'''
import os.path

import gettext
from gettext import lgettext as _
gettext.textdomain('vk_api_wrapper')

try:
    from vk_api_wrapper import vkApiOAuth
    from vk_api_wrapper.authenticate import OAuth
except ImportError:
    import sys
    sys.path.append(os.path.abspath("."))
    from vk_api_wrapper import vkApiOAuth
    from vk_api_wrapper.authenticate import OAuth

import ConfigParser
import cPickle as pickle

def get_token():
    """
    [app_<application id>_acc_<account id>]
    auth_type="oauth"|"vkauth"
    permissions="perm1","perm2",...
    token=<serialized token>
    """
    conf_fname=os.path.expanduser("~/.vk_api_wrapper")
    if os.path.isfile(conf_fname):
        conf=ConfigParser.SafeConfigParser()
        conf.read(conf_fname)
        for pos_sect in enumerate(conf.sections()):
            print "%d) %s"%pos_sect
        _section=raw_input(_("Select account number (or hit Enter for new account): "))
        if not _section:
            return new_auth(conf_fname)
        section=conf.sections()[int(_section)]
        return pickle.loads(conf.get(section, "token"))
    else:
        return new_auth(conf_fname)


def new_auth(conf_fname):
    from datetime import datetime
    token=OAuth()

    app_id=raw_input(_("Application id: "))

    print _("\nEnter required permissions separated by space\n")
    for i in token.permissions.iteritems():
        print "\t%s) %s"%i
    perms=raw_input(_("List of permissions: ")).split(" ")

    print _('\nPlease, open following URL in you browser: %s\n')%token.get_confirm_url(perms, app_id)
    success_url=raw_input(_('confirm all permission requests and paste browser URL string content there: '))

    token.setup_by_confirmed_url(success_url)
    token_dump=pickle.dumps(token, pickle.HIGHEST_PROTOCOL)
    section="app_%s_acc_%s_%s"%(app_id, token.user_id, datetime.today().strftime("%Y.%m.%d-%H:%m"))
    conf=ConfigParser.SafeConfigParser()
    conf.add_section(section)
    conf.set(section, 'auth_type', "oauth")
    conf.set(section, "permissions", ",".join(perms))
    conf.set(section, "token", token_dump)
    with open(conf_fname, "ar") as f:
        conf.write(f)

    return token


def start_python_console(namespace=None, noipython=False):
    if namespace is None:
        namespace={}
    try:
        try: # use IPython if available
            if noipython:
                raise ImportError
            import IPython
            shell=IPython.Shell.IPShellEmbed(argv=[], user_ns=namespace)
            shell()
        except ImportError:
            import code
            try: # readline module is only available on unix systems
                import readline
            except ImportError:
                pass
            else:
                import rlcompleter
                readline.parse_and_bind("tab:complete")
            code.interact(banner='', local=namespace)
    except SystemExit: # raised when using exit() in python code.interact
        pass

def main():
    token=get_token()
    api=token.get_api_obj()
    start_python_console({"api": api})

if __name__=='__main__':
    main()
