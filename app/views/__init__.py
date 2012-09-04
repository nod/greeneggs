from tornroutes import route

# now pull in our main views
import home
import index
import auth
import mix


# after our views are imported, let's build an authoritative list
routes = route.get_routes()
