import os
import ee
import geemap
import ipywidgets as widgets
from IPython.display import display
import solara


class Map(geemap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_basemap("Esri.WorldImagery")
        easement = ee.FeatureCollection("projects/ee-giswqs/assets/easements")
        style = {
            "color": "ff0000",
            "width": 2,
            "fillColor": "00000020",
        }
        self.addLayer(easement.style(**style), {}, "Easements")
        self.add_gui("timelapse", basemap=None)

        def handle_interaction(**kwargs):
            latlon = kwargs.get("coordinates")
            if kwargs.get("type") == "click":
                selected_layer = self.find_layer("Selected")
                if selected_layer is not None:
                    self.remove_layer(selected_layer)
                timelapse_layer = self.find_layer("Timelapse")
                if timelapse_layer is not None:
                    self.remove_layer(timelapse_layer)
                self.default_style = {"cursor": "wait"}
                clicked_point = ee.Geometry.Point(latlon[::-1])
                selected = easement.filterBounds(clicked_point)
                if selected.size().getInfo() > 0:

                    selected_style = {
                        "color": "ffff00",
                        "width": 2,
                        "fillColor": "00000020",
                    }
                    self.addLayer(selected.style(**selected_style), {}, "Selected")
                    self._draw_control.last_geometry = selected.geometry()
                self.default_style = {"cursor": "default"}

        self.on_interaction(handle_interaction)


@solara.component
def Page():
    with solara.Column(style={"min-width": "500px"}):
        Map.element(
            center=[40, -110],
            zoom=4,
            height="750px",
            zoom_ctrl=False,
            measure_ctrl=False,
        )
