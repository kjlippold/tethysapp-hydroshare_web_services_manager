from tethys_sdk.base import TethysAppBase, url_map_maker


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
        )

        return url_maps
