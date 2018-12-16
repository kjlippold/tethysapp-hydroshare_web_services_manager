from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes
from .app import HydroshareWebServicesManager as app
from tethys_apps.models import TethysApp
from .utilities import get_database_list, register_geoserver_databases, \
                       unregister_geoserver_databases, register_wof_databases, \
                       unregister_wof_databases, add_geoserver_workspace, \
                       add_wof_resource


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
def update_services(request):
    '''
    API Controller for registering service databases
    '''

    res_id = request.GET.get('res_id')

    db_list = get_database_list(res_id)
    print db_list

    if db_list == "Invalid":
        unregister_geoserver_databases(res_id)
        unregister_wof_databases(res_id)
    else:
        if db_list["geoserver"]:
            workspace_id = add_geoserver_workspace(res_id)
            register_geoserver_databases(workspace_id, db_list["geoserver"])

        if db_list["wof"]:
            unregister_wof_databases(res_id)
            add_wof_resource(res_id)
            register_wof_databases(res_id, db_list["wof"])

    data = {"res_id": res_id}
    return JsonResponse(data)
