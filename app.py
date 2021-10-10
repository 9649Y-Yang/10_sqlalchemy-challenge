# Step 2 - Climate App
# Routes


import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"Precipitations:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"Station:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"TOBS for the past year: /api/v1.0/tobs<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Give a start date (yyyy-mm-dd) of the trip to see the TOBS information, e.g. 2014-10-09:<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/><br/>"
        f"Give a start and end date (yyyy-mm-dd) of the trip to see the TOBS information, "
        f"e.g. 2014-10-09 (start date first) and 2014-10-16:<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value"""
    # Query all precipitations
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    # Create a dictionary from the row data and append to a list of precipitations_results
    precipitations_results = []
    for date, prcp in results:
        precipitations_dict = {}
        precipitations_dict[date] = prcp
        precipitations_results.append(precipitations_dict)

    return jsonify(precipitations_results)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()
    # Create a dictionary from the row data and append to a list of stations_results
    stations_results = []
    for station, name in results:
        stations_dict = {}
        stations_dict[station] = name
        stations_results.append(stations_dict)

    return jsonify(stations_results)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    import datetime as dt
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_string = last_date[0]

    # Calculate the date 1 year ago from the last data point in the database
    lastDate_datetime = dt.date(int(last_date_string[0:4]), int(last_date_string[5:7]), int(last_date_string[8:10]))
    one_year_before_last_date = lastDate_datetime - dt.timedelta(days=365)
    one_year_before_last_date

    # # Perform a query to retrieve the data and precipitation scores
    # one_year_data = session.query(Measurement.date, Measurement.prcp). \
    #     filter(Measurement.date >= one_year_before_last_date). \
    #     order_by(Measurement.date).all()

    # Query for most active station
    active_stations = session.query(Measurement.station, func.count(Measurement.station)). \
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    most_active_station = active_stations[0][0]

    most_active_station_temp_one_year = session.query(Measurement.date, Measurement.tobs). \
        filter(Measurement.station == most_active_station). \
        filter(Measurement.date >= one_year_before_last_date).all()

    session.close()
    # Create a dictionary from the row data and append to a list of tobs_results
    tobs_results = []
    for date, tobs in most_active_station_temp_one_year:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_results.append(tobs_dict)

    return jsonify(tobs_results)

@app.route("/api/v1.0/<start>")
def start_date_tobs(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_string = last_date[0]

    # Calculate the date 1 year ago from the last data point in the database
    lastDate_datetime = dt.date(int(last_date_string[0:4]), int(last_date_string[5:7]), int(last_date_string[8:10]))

    """Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start date"""
    if start < str(lastDate_datetime):
        results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)). \
            filter(Measurement.date >= start).all()

        session.close()
        # Create a dictionary from the row data and append to a list of tobs_results for given start date
        start_date_tobs_result = []
        for tobmin, tobmax, tobavg in results:
            start_date_tobs_dict = {}
            start_date_tobs_dict["Min TOBS"] = tobmin
            start_date_tobs_dict["Max TOBS"] = tobmax
            start_date_tobs_dict["Average TOBS"] = round(tobavg, 2)
            start_date_tobs_result.append(start_date_tobs_dict)

        return jsonify(start_date_tobs_result)
    else:
        return jsonify({"error": f"The date you try to search is out of dataset, cannot give the TOBS. "
                                 f"Please give a date before {lastDate_datetime}"}), 404


@app.route("/api/v1.0/<start>/<end>")
def start_end_date_tobs(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_string = last_date[0]

    # Calculate the date 1 year ago from the last data point in the database
    lastDate_datetime = dt.date(int(last_date_string[0:4]), int(last_date_string[5:7]), int(last_date_string[8:10]))

    if end < str(lastDate_datetime):
        if start < end:
            """Return a JSON list of the minimum temperature, the average temperature, 
            and the max temperature for a given start and end date"""
            results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)). \
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()

            session.close()
            # Create a dictionary from the row data and append to a list of tobs_results for given start date
            start_end_date_tobs_result = []
            for tobmin, tobmax, tobavg in results:
                start_end_date_tobs_dict = {}
                start_end_date_tobs_dict["Min TOBS"] = tobmin
                start_end_date_tobs_dict["Max TOBS"] = tobmax
                start_end_date_tobs_dict["Average TOBS"] = round(tobavg, 2)
                start_end_date_tobs_result.append(start_end_date_tobs_dict)
            return jsonify(start_end_date_tobs_result)
        else:
            return jsonify({"error": f"The start date you search is late than end date, cannot give the TOBS. "
                                     f"Please give try to re-enter the correct start and end date."}), 404
    else:
        return jsonify({"error": f"The date you try to search is out of dataset, cannot give the TOBS. "
                                 f"Please give a start and end date before {lastDate_datetime}"}), 404

if __name__ == '__main__':
    app.run(debug=True)