import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import curdoc, output_notebook
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, CustomJS, CategoricalColorMapper, Slider
from bokeh.models import LinearAxis, Range1d
from bokeh.palettes import Spectral6

from bokeh.models import HoverTool, LassoSelectTool, Plot, WheelZoomTool, CrosshairTool, ResetTool, PanTool

@st.cache_data
def get_data():
    url='https://drive.switch.ch/index.php/s/cxW0xrmQXdGL1VJ/download'
    return pd.read_csv(url)

df = get_data()
regions_list = df.region.unique().tolist()
color_mapper = CategoricalColorMapper(factors=regions_list, palette=Spectral6)

st.title(body='CO2-Emissions')
st.header('CO2-Emissions per region in most recent year')

df_last = df[df['year']==max(df['year'])]

co2_per_region = df_last.groupby('region')['co2'].sum()
co2_per_region.sort_values(inplace=True, ascending=True)

left_column, right_column = st.columns(2)
with right_column:
    st.subheader('This is a Matplotlib-Chart')
    
    fig, ax = plt.subplots()
    ax.spines[:].set_visible(False)
    ax.spines['top'].set_visible(True)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top') 

    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)

    ax.barh(co2_per_region.index, co2_per_region.values) # ax.barh(groups.index, groups.values)
    # ax.set_xlabel('CO2-Emission (tons per person)', fontsize=16)
    st.pyplot(fig)

with left_column:
    st.subheader('DataFrame display')
    st.text('Click and Ctrl-F to search the table!')
    st.dataframe(data=co2_per_region, use_container_width=True)

st.header('CO2-Emissions vs Gross Domestic Product')

year = st.slider(label='Select a Year', min_value=min(df.year), max_value=max(df.year), value=1964, step=1)

source = ColumnDataSource(df[df['year']==year])

plot_title = 'CO2 Emissions vs GDP in {}'.format(year)

hover = HoverTool(tooltips=[('Country', '@country'), ('GDP', '@gdp'), ('CO2 Emission', '@co2')])
# Create the figure: plot
p = figure(title=plot_title, 
           height=400, width=800,
           y_axis_type='log',
           tools=[hover, LassoSelectTool(), WheelZoomTool(), PanTool()],
           toolbar_location="right",
           
          )

# Add circle glyphs to the plot
p.circle(x='gdp', y='co2', fill_alpha=0.8, source=source, 
            legend_group='region',
            color=dict(field='region', transform=color_mapper),
            size=7)

p.legend.title = 'Region:'
# Set the legend.location attribute of the plot
p.legend.location = 'bottom_right'

# Set the x-axis label
p.xaxis.axis_label = 'GDP'

# Set the y-axis label
p.yaxis.axis_label = 'CO2 Emissions (tons per person)'

# Set autohide to true to only show the toolbar when mouse is over plot
p.toolbar.autohide = True

st.bokeh_chart(p, use_container_width=True)

st.divider()
st.header('CO2-Emissions and GDP for Country of Interest')

country = st.selectbox(label='Select a country', options=df.country.unique())

source_country = ColumnDataSource(df[df['country']==country])

hover_co2_year = HoverTool(tooltips=[('Year', '@year'), ('GDP', '@gdp'), ('CO2 Emission', '@co2')])

p_co2_year = figure(title='CO2 Emissions and GDP of {}'.format(country), x_axis_label='Year',
                    y_axis_label='CO2 Emissions (tons per person)',
                    y_range=(min(df[df['country']==country]['co2']), max(df[df['country']==country]['co2'])))

p_co2_year.line(x='year', y='co2', source=source_country, line_width=3)

p_co2_year.extra_y_ranges['foo'] = Range1d(min(df[df['country']==country]['gdp']), max(df[df['country']==country]['gdp']))
p_co2_year.line(x='year', y='gdp', source=source_country, line_width=3, color="orange", y_range_name="foo")

ax2 = LinearAxis(y_range_name="foo", axis_label="GDP")
ax2.axis_label_text_color ="orange"
p_co2_year.add_layout(ax2, 'right')

st.bokeh_chart(p_co2_year, use_container_width=True)