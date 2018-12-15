from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting


class HydroshareWebServicesManager(TethysAppBase):
    """
    Tethys app class for Hydroshare Web Services Manager.
    """

    name = 'Hydroshare Web Services Manager'
    index = 'hydroshare_web_services_manager:home'
    icon = 'hydroshare_web_services_manager/images/icon.gif'
    package = 'hydroshare_web_services_manager'
    root_url = 'hydroshare-web-services-manager'
    color = '#8e44ad'
    description = 'Place a brief description of your app here.'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='hydroshare-web-services-manager',
                controller='hydroshare_web_services_manager.controllers.home'
            ),
            UrlMap(
                name='register_services',
                url='hydroshare-web-services-manager/api/register_services',
                controller='hydroshare_web_services_manager.api.register_services'
            ),
            UrlMap(
                name='unregister_services',
                url='hydroshare-web-services-manager/api/unregister_services',
                controller='hydroshare_web_services_manager.api.unregister_services'
            )
        )

        return url_maps

    def custom_settings(self):
        custom_settings = (
            CustomSetting(
                name='hydroshare_url',
                type=CustomSetting.TYPE_STRING,
                description='HydroShare REST API URL'
            ),
            CustomSetting(
                name='geoserver_url',
                type=CustomSetting.TYPE_STRING,
                description='GeoServer REST API URL'
            ),
            CustomSetting(
                name='geoserver_resource_directory',
                type=CustomSetting.TYPE_STRING,
                description='GeoServer directory containing HydroShare resources'
            ),
            CustomSetting(
                name='geoserver_user',
                type=CustomSetting.TYPE_STRING,
                description='GeoServer username'
            ),
            CustomSetting(
                name='geoserver_pass',
                type=CustomSetting.TYPE_STRING,
                description='GeoServer password'
            ),
            CustomSetting(
                name='wof_url',
                type=CustomSetting.TYPE_STRING,
                description='WaterOneFlow REST API URL'
            ),
            CustomSetting(
                name='wof_resource_directory',
                type=CustomSetting.TYPE_STRING,
                description='WaterOneFlow directory containing HydroShare resources'
            ),
            CustomSetting(
                name='wof_user',
                type=CustomSetting.TYPE_STRING,
                description='WaterOneFlow username'
            ),
            CustomSetting(
                name='wof_pass',
                type=CustomSetting.TYPE_STRING,
                description='WaterOneFlow password'
            )
        )
        return custom_settings