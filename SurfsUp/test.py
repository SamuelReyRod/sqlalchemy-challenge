#################### Import dependencies ###################
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from flask import Flask, jsonify
import sqlalchemy
import datetime as dt
import numpy as np


##################### Database Setup ########################


# Reflect an existing database and tables
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Find the most recent date in the data set.
recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
recent_date

# Calculate the date one year from the last date in data set from the most recent data point in the database
one_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

# Closing the session
session.close()


######################## Set up Flask #######################
# Create an app
app = Flask(__name__)



###################### Create Flask Routes ###################

@app.route("/")
def home():
    #"""List all available routes."""
    return(
        f"Hawaii Climate API<br/>"
        f"<br/>"
        f"<br/>"
        f"List of available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Instruction:<br/>"
        f"To change the \"start_date\" below format date as: YYYY-MM-DD<br/>"
        f"/api/v1.0/start_date<br/>"
        f"<br/>"
        f"Instruction:<br/>"
        f"To change the \"start/end\" below format the dates as: YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"/api/v1.0/start/end<br/>"
    )




################ Precipitation Route ###############

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create the session engine
    session = Session(engine)
    
    # Getting the most recent date and going back 1 year from it
    recent_date = dt.date(2017,8, 23)
    prior_year =  recent_date - dt.timedelta(days = 365)

    # Query precipitation and date values 
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prior_year).all()

    # Closed Session   
    session.close()
    
    # Converting the data to a dictionary.
    #[result [0] is the key or date while result [1] is the value
    prcp = {}
    for results in data:
        prcp[results[0]] = results[1]
     

    # JSonifying the dictionary.
    return jsonify(prcp)


###################  Stations Route  #####################

@app.route("/api/v1.0/stations")
def stations():
    
    # Create the session engine
    session = Session(engine)  
    # Query data to get stations list
    stations = session.query(Station.station, Station.name).all()
    # Close Session
    session.close()
    

    # Creating a dictionary and a list to append the results
    station_list = []
    for station, name in stations:
        station_sites = {}
        #print(station_dict) #testing results
        station_sites["Station"]= station
        station_sites["Name"] = name
        station_list.append(station_sites)
    
    # JSonifying the dictionary.
    return jsonify(station_list)


################## TOBS Route #######################

@app.route("/api/v1.0/tobs")
def tobs():
    # Create the session engine
    session = Session(engine)
    
# Find the most recent date in the data set.
# recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
# one_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    
    # Calculate the date one year from the last date in data set from the most recent data point in the database. 
    one_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    #Query the dates and temperature observation of the most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.date)).group_by(Measurement.station).order_by(func.count(Measurement.date).desc()).all()
    most_active_station_id = active_stations[0][0]
        
    data_results = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year, Measurement.station == most_active_station_id).all()

    session.close()

    # Create list and dict to hold results
    temperatures = []
    for station, date, tobs in data_results:
        temp_list = {}
        temp_list["Station_ID"] = station
        temp_list["Temperature"] = tobs
        temp_list["Date"] = date
        temperatures.append(temp_list)
        
    # Jsonify the list of tempearatures for the year
    return jsonify(temperatures)


################## Create start-date route #######################

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Create the session engine
    session = Session(engine)

    # start_date conversion to YYYY-MM-DD format
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
   
    # Calculate TMIN, TAVG, and TMAX for all dates >= to the start date.
    data_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
 
    # Closing session
    session.close()

    # Creating a dictionary and a list to append the results
    start_date_list = []
    for result in data_results:
        select_date = {}
        select_date["StartDate"] = start_date
        select_date["Temp_Min"] = result[0]
        select_date["Temp_Avg"] = result[1]
        select_date["Temp_Max"] = result[2]
        start_date_list.append(select_date)

    # Jsonify the dict list
    return jsonify(start_date_list)


################## Create start-date/end-date route ######################

@app.route("/api/v1.0/<start>/<end>")
def startdate_enddate(start, end):
    
    # Create the Session link
    session = Session(engine)

    # JSON list for Tmin, Tavg, and Tmax for start-end dates range
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    # Calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date)).all()

    # Closing session
    session.close()

    # Create a list comprehension to hold results
    start_end_list = [{
        "Start_Date": start_date,
        "End_Date": end_date,
        "Temp_Min": result[0],
        "Temp_Avg": result[1],
        "Temp_Max": result[2]
    } for result in results]

    # Return the JSON representation of the list.
    return jsonify(start_end_list)
    
################################################################################################################

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
