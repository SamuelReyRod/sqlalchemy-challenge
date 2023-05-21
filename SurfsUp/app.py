# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return (
        f"Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/startdate/enddate"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the 1 year"""
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set.
    prior_year =  dt.date(2017,8,23) - dt.timedelta(days = 365)

    # Query for the date and precipitation for 1 year
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prior_year).all()
    session.close()

    # Dict with date as the key and prcp as the value
    data_dict = {date: prcp for date, prcp in data}
    return jsonify(data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a list of stations."""
    station_query = session.query(Station.name).all()
    session.close()

    #convert to a list
    stations = list(np.ravel(station_query))
    return jsonify(stations=stations)





