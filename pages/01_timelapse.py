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
