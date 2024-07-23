from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class LoadDialog(BoxLayout):
    def __init__(self, load, cancel, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.filechooser = FileChooserIconView()
        self.add_widget(self.filechooser)
        self.buttons = BoxLayout(size_hint_y=0.1)
        self.buttons.add_widget(Button(text='Load', on_press=load))
        self.buttons.add_widget(Button(text='Cancel', on_press=cancel))
        self.add_widget(self.buttons)


class Plotter(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        self.load_button = Button(text="Load CSV", size_hint=(1, 0.1))
        self.load_button.bind(on_press=self.show_load_dialog)
        self.add_widget(self.load_button)
        
        self.plot_button = Button(text="Plot CSV", size_hint=(1, 0.1))
        self.plot_button.bind(on_press=self.load_csv)
        self.add_widget(self.plot_button)
        
        self.plot_area = Image(size_hint=(1, 0.7))
        self.add_widget(self.plot_area)
        
        self.info_label = Label(size_hint=(1, 0.1))
        self.add_widget(self.info_label)
        
        self.popup = None
        self.selected_file = None

    def show_load_dialog(self, instance):
        content = LoadDialog(load=self.select_csv, cancel=self.dismiss_popup)
        self.popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def dismiss_popup(self, instance):
        if self.popup:
            self.popup.dismiss()

    def select_csv(self, instance):
        selected = self.popup.content.filechooser.selection
        if selected:
            self.selected_file = selected[0]
            self.info_label.text = f'Selected file: {self.selected_file}'
        self.dismiss_popup(instance)

    def load_csv(self, instance):
        if self.selected_file:
            self.load_and_plot(self.selected_file)

    def load_and_plot(self, filepath):
        try:
            df = pd.read_csv(filepath)
            if 'Record no.' not in df.columns or 'Time [hh:mm:ss]' not in df.columns:
                self.info_label.text = 'CSV file does not contain required columns.'
                return

            # Convert 'Time [hh:mm:ss]' to seconds since midnight
            df['Time [hh:mm:ss]'] = pd.to_datetime(df['Time [hh:mm:ss]'], format='%H:%M:%S')
            df['Time [hh:mm:ss]'] = df['Time [hh:mm:ss]'].dt.hour * 3600 + df['Time [hh:mm:ss]'].dt.minute * 60 + df['Time [hh:mm:ss]'].dt.second

            # Generate the plot
            fig, ax = plt.subplots()
            ax.plot(df['Record no.'], df['Time [hh:mm:ss]'])
            ax.set_xlabel('Record no.')
            ax.set_ylabel('Time [seconds]')
            fig.autofmt_xdate()

            # Save the plot as an image
            plt.savefig('plot.png')
            plt.close(fig)
            
            # Load the plot image in Kivy
            self.plot_area.source = 'plot.png'
            self.plot_area.reload()

            self.info_label.text = 'Plot loaded successfully.'
        except Exception as e:
            self.info_label.text = f'Failed to load plot: {str(e)}'


class MainApp(App):
    def build(self):
        return Plotter()


if __name__ == '__main__':
    MainApp().run()
