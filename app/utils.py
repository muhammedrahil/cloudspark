

def console_print(prefix:str='', msg:str='', color="success"):
    RED = '\033[91m'
    GREEN = '\033[92m'
    END_COLOR = '\033[0m'
    match color:
        case 'success':
            print(f"{GREEN}{msg}{END_COLOR}")
        case 'error':
            print(f"{RED}{msg}{END_COLOR}")
        case _ :
            print(msg)
    return 



