import ee
import geemap
import solara
import ipywidgets as widgets
from ipyleaflet import WidgetControl


class Map(geemap.Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_basemap("Esri.WorldImagery", True)
        easement = ee.FeatureCollection("projects/ee-giswqs/assets/easements")
        style = {
            "color": "ff0000",
            "width": 2,
            "fillColor": "00000020",
        }
        self.addLayer(easement.style(**style), {}, "Easements")

        info = widgets.Output()
        info_ctrl = WidgetControl(widget=info, position="bottomright")
        self.add(info_ctrl)

        def handle_interaction(**kwargs):
            latlon = kwargs.get("coordinates")
            if kwargs.get("type") == "click":
                selected_layer = self.find_layer("Selected")
                if selected_layer is not None:
                    self.remove_layer(selected_layer)
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
                    try:
                        self._draw_control.last_geometry = selected.geometry()
                    except:
                        pass

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

                self.default_style = {"cursor": "default"}

        self.on_interaction(handle_interaction)

        self._toolbar.toggle_layers(False)
        self.add_gui()

    def add_gui(self):
        widget_width = "350px"
        padding = "0px 0px 0px 5px"  # upper, right, bottom, left
        style = {"description_width": "initial"}
        button_width = "113px"

        text = widgets.Text(
            "Draw a rectangle on the map",
            layout=widgets.Layout(padding="0px", width="230px"),
        )

        bands = widgets.Dropdown(
            description="Bands:",
            options=[
                "Red/Green/Blue",
                "NIR/Red/Green",
            ],
            value="NIR/Red/Green",
            layout=widgets.Layout(width="230px", padding=padding),
            style=style,
        )

        apply_btn = widgets.Button(
            description="Time slider",
            button_style="primary",
            tooltip="Click to create timeseries",
            style=style,
            layout=widgets.Layout(padding="0px", width=button_width),
        )

        split_btn = widgets.Button(
            description="Split map",
            button_style="primary",
            tooltip="Click to create timeseries",
            style=style,
            layout=widgets.Layout(padding="0px", width=button_width),
        )
        widget = widgets.VBox([text, bands, widgets.HBox([apply_btn, split_btn])])
        self.add_widget(widget, position="topright")

        def apply_btn_click(b):
            if self.user_roi is not None:

                if bands.value == "NIR/Red/Green":
                    RGBN = True
                    vis_params = {"bands": ["N", "R", "G"], "min": 0, "max": 255}
                else:
                    RGBN = False
                    vis_params = {"bands": ["R", "G", "B"], "min": 0, "max": 255}
                collection = geemap.naip_timeseries(self.user_roi, RGBN=RGBN)
                if hasattr(self, "slider_ctrl") and self.slider_ctrl is not None:
                    self.remove(self.slider_ctrl)
                    delattr(self, "slider_ctrl")
                self.add_time_slider(
                    collection, vis_params=vis_params, date_format="YYYY"
                )

        apply_btn.on_click(apply_btn_click)

        def split_btn_click(b):
            if self.user_roi is not None:
                if bands.value == "NIR/Red/Green":
                    RGBN = True
                    vis_params = {"bands": ["N", "R", "G"], "min": 0, "max": 255}
                else:
                    RGBN = False
                    vis_params = {"bands": ["R", "G", "B"], "min": 0, "max": 255}
                collection = geemap.naip_timeseries(self.user_roi, RGBN=RGBN)

                self.ts_inspector(
                    collection,
                    left_vis=vis_params,
                    width="100px",
                    date_format="YYYY",
                    add_close_button=True,
                )

        split_btn.on_click(split_btn_click)


@solara.component
def Page():
    with solara.Column(style={"min-width": "500px"}):
        Map.element(
            center=[40, -100],
            zoom=4,
            height="750px",
            zoom_ctrl=False,
            measure_ctrl=False,
        )
