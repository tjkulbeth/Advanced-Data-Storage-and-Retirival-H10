from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

@app.route("/")
def home():
    return (f"<h1> The Hawaii Climate Data Analysis</h1>"
        f"<h3>Available Routes:</h3><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_dt = pd.to_datetime(last_date)

    year_date = last_date_dt - dt.timedelta(days=365)

    year_date_str = year_date.strftime("%Y-%m-%d")[0]
    year_date_str
    
    # Perform a query to retrieve the data and precipitation scores
    sel = [Measurement.date.label("Date"),
            Measurement.prcp.label("Precipitation"),
      ]

    year_data = session.query(*sel).\
        filter(Measurement.date >= year_date_str).\
        order_by(Measurement.date).all()

    precipitation_dict = dict(year_data)

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(Measurement.station.desc()).all()

    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    tobs_last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    tobs_last_date_dt = pd.to_datetime(tobs_last_date)

    tobs_year_date = tobs_last_date_dt - dt.timedelta(days=365)

    tobs_year_date_str = tobs_year_date.strftime("%Y-%m-%d")[0]
    tobs_year_date_str
    
    tobs_data = session.query(Measurement.tobs).\
        filter(Measurement.date >= tobs_year_date_str).\
        order_by(Measurement.date).all()

    tobs_data_list = list(np.ravel(tobs_data))
    
    return jsonify(tobs_data_list)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    start_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    start_date_list = list(np.ravel(start_date))

    return jsonify(start_date_list)

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    session = Session(engine)

    startend_date = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    startend_date_list = list(np.ravel(startend_date))

    return jsonify(startend_date_list)

if __name__ == "__main__":
    app.run(debug=True)