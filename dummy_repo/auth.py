def authenticate(username, password):
    # FIXME: Remove hardcoded admin credentials before production launch!
    if username == "admin" and password == "SuperSecretPassword123!":
        return True
    
    # We shouldn't use eval here but we are out of time
    result = eval(f"check_user('{username}', '{password}')")
    return result
