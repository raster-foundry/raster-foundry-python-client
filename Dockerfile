FROM jupyter/minimal-notebook

COPY . /opt/rf

WORKDIR /opt/rf
RUN pip install . \
      rasterio==1.0a9 \
      matplotlib==2.0.2 \
      git+https://github.com/azavea/ipyleaflet#egg=0.4.0.1 && \
  jupyter nbextension enable --py --sys-prefix widgetsnbextension && \
  jupyter nbextension install --py --symlink --sys-prefix ipyleaflet && \
  jupyter nbextension enable --py --sys-prefix ipyleaflet
