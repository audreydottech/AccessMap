import os
import json
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    url_for,
    request,
    send_from_directory,
    make_response)

import add_gsheets
from add_records import add_new_rating_to_db
from models import Locations

# Configure application
app = Flask(__name__)

app.config["SECRET_KEY"] = "IAMAKEY"

# ------------------- Google Sheets API Setup ------------------- #

import gspread

from oauth2client.service_account import ServiceAccountCredentials

# # Use credentials to create a client to interact with the Google Drive API
# scope = ["https://spreadsheets.google.com/feeds"]
# credentials = ServiceAccountCredentials.from_json_keyfile_name(
#     "client_secret.json", scope)
# client = gspread.authorize(credentials)

# # Find a workbook by name and open the first sheet
# sheet = client.open("LocationsAccessMap").sheet2

# print(sheet.get_all_values())


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("Home.html")

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    """
    Allows a user to register for an account and view maps tailored 
    to their accessibility interests
    """
    
    if request.method == "POST":
        # Get user's input from the form
        username = request.form.get("txt")
        email = request.form.get("email")
        password = request.form.get("pswd")
        
        print(username, email, password)
        
        # TODO: Hash password
        
        # TODO: Save new user to the database
        
        # Redirect to sign up part 2
        return redirect(url_for("choose_accessibility_filters"))
    
    return render_template("signup.html")

@app.route("/choose_accessibility_filters", methods=["GET", "POST"])
def choose_accessibility_filters():
    """
    Allows the user to see maps customized to their accessibility needs
    """
    
    if request.method == "POST":
        # Handle the form submission
        print("Form submitted")
        
        # TODO: Save accessibility preferences 
        
        return redirect(url_for("home"))
    
    return render_template("accessibilityneeds.html")

@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    """Logs an existing user in"""
    
    return render_template("Home.html")

@app.route("/find_a_location", methods=["GET", "POST"])
def find_a_location():
    """Allows a user to search for a location by name or address""" 

    if request.method == "POST":
        print("Looking for location")

        # Get form information from the user
        location_name = request.form.get("location_name")
        address = request.form.get("location_address")
        
        print(f"Location Name: {location_name}",
        f"Address: {address}")
        print(f"Location Name: {type(location_name)}",
        f"Address: {(address)}")

        if not location_name and not address:
            # TODO: User must choose either a location or an address in order to update
            # a location's accessibility rating
            print(f"Location Name: {location_name}",
                  f"Address: {address}")
            
            print("Please add either a location or an address to search for.")
        else:
            print("Either a location name or an address has been added!")
            
            # TODO: If the user searches by location name and not address:
                # TODO: Get what the user input for the location name
                # TODO: Find similar location names to what the user input using database query (SQL, CS50, or ORM)
                # TODO: Make a dropdown with similar location names
            # TODO: If the user searches by an address
                # TODO: Get the index of the location that matches the exact address
                # TODO: OR if there are multiple addressses that match the query
                    # TODO: Find similar addresses to what the user is searching for
                    # TODO: Make a dropdown with similar location addresses
            
            # TODO: Index the address or name that matches the unique dropdown ID
            
            # TODO: Edit the row that matches the unique location ID only
            
            # TODO: Redirect to update_rating if successful
            return redirect(url_for("update_rating"))

    return render_template("FindLocation.html")

@app.route("/update_rating", methods=["GET", "POST"])
def update_rating():
    """Allows a user to update a location's accessibility rating"""
    
    if request.method == "POST":
        print("posted")
        
        # Get form information from the user
        location_name = request.form.get("location_name")
        address = request.form.get("location_address")
        sensory_rating = request.form.get("sensoryrating")
        mobility_rating = request.form.get("mobilityrating")
        service_dog_relief_rating = request.form.get("sdogreliefrating")
        wheelchair_rating = request.form.get("wheelchairrating")
        common_allergens_rating = request.form.get("commonallergens")
        
        # Check information
        print(f"Sensory Rating: {sensory_rating}",
              f"Mobility Rating: {mobility_rating}",
              f"Service Dog Relief Rating: {service_dog_relief_rating}",
              f"Wheelchair Rating: {wheelchair_rating}",
              f"Common Allergens Rating: {common_allergens_rating}")
        
        if not sensory_rating and not mobility_rating and not service_dog_relief_rating \
            and not wheelchair_rating and not common_allergens_rating:
                # The user must choose to update either a sensory, mobility, service dog relief,
                # wheelchair, or common allergens rating 
                flash("Please add a category rating.")
                return redirect(url_for("update_rating"))
                
        else:
            # If the user puts an accessibility rating in, update database
            print("A category's rating has been updated!")
            
            # TODO: Use new rating to recalculate a location's average accessibility score
            ## for that category
            new_record = Locations(Name=location_name, Address=address, SensoryRating=sensory_rating,
                                MobilityRating=mobility_rating,
                                ServiceDogRelief=service_dog_relief_rating, WheelchairAccessible=wheelchair_rating,
                                CommonAllergenRisk=common_allergens_rating)

            print(new_record)
            try:
                add_new_rating_to_db(new_record)
                
                # Attempt to save the updated score
                return redirect(url_for("save_score"))
            except Exception as e:
                print(f"Couldn't reroute to save the updated score. Exception: {e}")
                return redirect(url_for("update_rating"))
            
    return render_template("UpdateRating.html")

@app.route("/save_score", methods=["GET"])
def save_score():
    """Updates the Google Sheet from update_rating"""
    
    try:
        # Flask won't update both the database and write to GSheet within the same route.
        # But you can call this function to update the spreadsheet for manual re-upload.
        add_gsheets.write_to_gsheet()
        
        # TODO: Insert the new average into the database
                
        # TODO: Display new average on the success page
        
    except Exception as e:
        print(f"Can't update spreadsheet. Exception: {e}")
    else:
        # Redirect to the success page if successful
        return redirect(url_for("successfully_posted"))
    
@app.route("/success", methods=["GET"])
def successfully_posted():
    """Informs the user they have successfully updated the rating"""
    
    return render_template("SuccessfullyUpdated.html")
