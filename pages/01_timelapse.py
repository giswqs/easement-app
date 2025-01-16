import os
import ee
import geemap
import ipywidgets as widgets
from IPython.display import display
import solara
from ipyleaflet import WidgetControl


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

        info = widgets.Output()
        info_ctrl = WidgetControl(widget=info, position="bottomright")
        self.add(info_ctrl)

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

                    with info:
                        info.clear_output()
                        info_dict = selected.first().toDictionary().getInfo()
                        info.append_stdout(
                            str(f"OBJECTID: {info_dict.get('OBJECTID')}") + "\n"
                        )
                        info.append_stdout(
                            str(f"NEST_AGREE: {info_dict.get('NEST_AGREE')}") + "\n"
                        )
                        info.append_stdout(
                            str(f"NEST_RESTO: {info_dict.get('NEST_RESTO')}") + "\n"
                        )
                        info.append_stdout(
                            str(f"ClosingDat: {info_dict.get('ClosingDat')}") + "\n"
                        )
                        info.append_stdout(
                            str(f"NEST_Acres: {info_dict.get('NEST_Acres')}") + "\n"
                        )
                        # print(info_dict)
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
