import os
import ee
import geemap
import ipywidgets as widgets
from IPython.display import display
import solara
from geemap import get_current_year, jslink_slider_label
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
                        # print(info_dict)

                self.default_style = {"cursor": "default"}

        self.on_interaction(handle_interaction)

        self.add_ts_gui(position="topright")

    def clean_up(self):
        if hasattr(self, "slider_ctrl") and self.slider_ctrl is not None:
            self.remove(self.slider_ctrl)
            delattr(self, "slider_ctrl")

        layer = self.find_layer("Time series")
        if layer is not None:
            self.remove(layer)
        layer = self.find_layer("Image X")
        if layer is not None:
            self.remove(layer)

        draw_layer = self.find_layer("Drawn Features")
        if draw_layer is not None:
            self.remove(draw_layer)

        selected_layer = self.find_layer("Selected")
        if selected_layer is not None:
            self.remove_layer(selected_layer)

    def add_ts_gui(self, position="topright", **kwargs):

        widget_width = "350px"
        padding = "0px 0px 0px 5px"  # upper, right, bottom, left
        style = {"description_width": "initial"}
        current_year = get_current_year()

        collection = widgets.Dropdown(
            options=[
                "Landsat TM-ETM-OLI Surface Reflectance",
            ],
            value="Landsat TM-ETM-OLI Surface Reflectance",
            description="Collection:",
            layout=widgets.Layout(width=widget_width, padding=padding),
            style=style,
        )
        bands = widgets.Dropdown(
            description="Bands:",
            options=[
                "Red/Green/Blue",
                "NIR/Red/Green",
                "SWIR2/SWIR1/NIR",
                "NIR/SWIR1/Red",
                "SWIR2/NIR/Red",
                "SWIR2/SWIR1/Red",
                "SWIR1/NIR/Blue",
                "NIR/SWIR1/Blue",
                "SWIR2/NIR/Green",
                "SWIR1/NIR/Red",
            ],
            value="SWIR1/NIR/Red",
            style=style,
            layout=widgets.Layout(width="195px", padding=padding),
        )

        frequency = widgets.Dropdown(
            description="Frequency:",
            options=["year", "quarter", "month"],
            value="year",
            style=style,
            layout=widgets.Layout(width="150px", padding=padding),
        )

        start_year = widgets.IntSlider(
            description="Start Year:",
            value=1984,
            min=1984,
            max=current_year,
            readout=False,
            style=style,
            layout=widgets.Layout(width="138px", padding=padding),
        )

        start_year_label = widgets.Label("1984")
        jslink_slider_label(start_year, start_year_label)

        end_year = widgets.IntSlider(
            description="End Year:",
            value=current_year,
            min=1984,
            max=current_year,
            readout=False,
            style=style,
            layout=widgets.Layout(width="138px", padding=padding),
        )
        end_year_label = widgets.Label(str(current_year))
        jslink_slider_label(end_year, end_year_label)

        start_month = widgets.IntSlider(
            description="Start Month:",
            value=5,
            min=1,
            max=12,
            readout=False,
            style=style,
            layout=widgets.Layout(width="145px", padding=padding),
        )

        start_month_label = widgets.Label(
            "5",
            layout=widgets.Layout(width="20px", padding=padding),
        )
        jslink_slider_label(start_month, start_month_label)

        end_month = widgets.IntSlider(
            description="End Month:",
            value=10,
            min=1,
            max=12,
            readout=False,
            style=style,
            layout=widgets.Layout(width="155px", padding=padding),
        )

        end_month_label = widgets.Label("10")
        jslink_slider_label(end_month, end_month_label)

        output = widgets.Output()

        button_width = "113px"
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

        reset_btn = widgets.Button(
            description="Reset",
            button_style="primary",
            style=style,
            layout=widgets.Layout(padding="0px", width=button_width),
        )

        vbox = widgets.VBox(
            [
                collection,
                widgets.HBox([bands, frequency]),
                widgets.HBox([start_year, start_year_label, end_year, end_year_label]),
                widgets.HBox(
                    [start_month, start_month_label, end_month, end_month_label]
                ),
                widgets.HBox([apply_btn, split_btn, reset_btn]),
                output,
            ]
        )
        self.add_widget(vbox, position=position, add_header=True)

        def apply_btn_click(change):

            if hasattr(self, "slider_ctrl") and self.slider_ctrl is not None:
                self.remove(self.slider_ctrl)
                delattr(self, "slider_ctrl")

            with output:
                output.clear_output()
                if self.user_roi is None:
                    output.append_stdout("Please draw a ROI first.")
                else:
                    output.append_stdout("Creating time series...")
                    collection = geemap.landsat_timeseries(
                        roi=self.user_roi,
                        start_year=start_year.value,
                        end_year=end_year.value,
                        start_date=str(start_month.value).zfill(2) + "-01",
                        end_date=str(end_month.value).zfill(2) + "-01",
                        frequency=frequency.value,
                    )
                    vis_params = {
                        "bands": bands.value.split("/"),
                        "min": 0,
                        "max": 0.4,
                    }

                    if frequency.value == "year":
                        date_format = "YYYY"
                    elif frequency.value == "quarter":
                        date_format = "YYYY-MM"
                    elif frequency.value == "month":
                        date_format = "YYYY-MM"

                    self.add_time_slider(
                        collection,
                        region=self.user_roi,
                        vis_params=vis_params,
                        date_format=date_format,
                    )
                    self._draw_control.clear()
                    draw_layer = self.find_layer("Drawn Features")
                    if draw_layer is not None:
                        self.remove(draw_layer)
                    output.clear_output()

        apply_btn.on_click(apply_btn_click)

        def split_btn_click(change):

            if hasattr(self, "slider_ctrl") and self.slider_ctrl is not None:
                self.remove(self.slider_ctrl)
                delattr(self, "slider_ctrl")

            with output:
                output.clear_output()
                if self.user_roi is None:
                    output.append_stdout("Please draw a ROI first.")
                else:
                    output.append_stdout("Creating time series...")
                    collection = geemap.landsat_timeseries(
                        roi=self.user_roi,
                        start_year=start_year.value,
                        end_year=end_year.value,
                        start_date=str(start_month.value).zfill(2) + "-01",
                        end_date=str(end_month.value).zfill(2) + "-01",
                        frequency=frequency.value,
                    )
                    vis_params = {
                        "bands": bands.value.split("/"),
                        "min": 0,
                        "max": 0.4,
                    }

                    if frequency.value == "year":
                        date_format = "YYYY"
                        dates = geemap.image_dates(collection, date_format).getInfo()
                    elif frequency.value == "quarter":
                        date_format = "YYYY-MM"
                        dates = geemap.image_dates(collection, date_format).getInfo()
                    elif frequency.value == "month":
                        date_format = "YYYY-MM"
                        dates = geemap.image_dates(collection, date_format).getInfo()

                    self.ts_inspector(
                        collection,
                        left_names=dates,
                        left_vis=vis_params,
                        add_close_button=True,
                    )
                    output.clear_output()

                    try:
                        self._draw_control.clear()
                        draw_layer = self.find_layer("Drawn Features")
                        if draw_layer is not None:
                            self.remove(draw_layer)
                    except Exception as e:
                        print(e)

        split_btn.on_click(split_btn_click)

        def reset_btn_click(change):
            output.clear_output()
            self.clean_up()

        reset_btn.on_click(reset_btn_click)


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
