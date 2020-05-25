# coding=utf-8
import json
import os
import traceback
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask import request, make_response

import requests
state_helpline = {"Andhra Pradesh": "0866-2410978","Arunachal Pradesh": "9436055743", "Assam" : "6913347770", "Bihar": "104","Chhattisgarh" :"104","Goa": "104","Gujarat" :"104", "Haryana" : "8558893911", "Himachal Pradesh" : "104", "Jharkhand" :"104", "Karnataka" :"104", "Kerala": "0471-2552056", "Madhya Pradesh" :"104",
"Maharashtra" :"020-26127394", "Manipur" :"3852411668", "Meghalaya": "108", "Mizoram" :"102", "Nagaland": "7005539653", "Odisha" :"9439994859", "Punjab": "104", "Rajasthan" :"0141-2225624", "Sikkim" :"104", "Tamil Nadu": "044-29510500", "Telangana": "104", "Tripura" :"0381-2315879", "Uttarakhand" :"104","Uttar Pradesh": "18001805145",
"West Bengal": "1800313444222, 03323412600","Andaman And Nicobar Islands": "03192-232102", "Chandigarh": "9779558282","Delhi" :"011-22307145", "Jammu & Kashmir" :"01912520982, 0194-2440283", "Ladakh" :"01982256462", "Lakshadweep" : "104", "Puducherry" :"104"}

dict = {}
state = {}
counter = 0
list = []
def sensor():
    global state, dict
    global counter
    global state_helpline
    global list
    """ Function for test purposes. """
    print("Scheduler is alive!")
    counter = counter + 1
    print(counter)
    raw_data = requests.get("https://api.covid19india.org/v2/state_district_wise.json")
    jsondata = raw_data.json()

    raw_data_helpline = requests.get("https://api.covid19india.org/resources/resources.json")
    jsondata_helpline = raw_data_helpline.json()

    total = 0
    for i in jsondata:
        # print(i)
        dict.update(i)
        # print(dict)
        # print("***************************")
        # print("state is " + str(dict["state"]))
        # print("***************************")

        for j in dict["districtData"]:
            dist = j["district"]
            active = j["active"]
            confirmed = j["confirmed"]
            deceased = j["deceased"]
            recovered = j["recovered"]
            district_data = {dist: [active, confirmed, deceased, recovered]}

            dict.update(district_data)

            print(j["district"] + " total active cases " + str(j["active"]) + " total confirmed cases " + str(
                j["confirmed"]) + " total deceased cases " + str(j["deceased"]) + " total recovered cases " + str(
                j["recovered"]))
            total = total + j["confirmed"]
            state_data = {dict["state"]: str(total)}
            state.update(state_data)
        print(dict["state"] + " Total " + str(total))
        print(state)
        list.append(int(state_data.get(dict["state"])))
        print(list)
        print(state_data.get(dict["state"]))
        print(state)
        total = 0
    print(type(list[1]))
    print("888888888888888888888888888888888888888")
    indiancount = sum(list)
    list = []
    print(sum(list))


    sched = BackgroundScheduler(daemon=True)
    sched.add_job(sensor,'interval',minutes=120)
    sched.start()

    return dict, state, jsondata_helpline, indiancount


app = Flask(__name__)



@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request Header: ", request.headers)
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        print("Request IP : ", request.environ['REMOTE_ADDR'])
    else:
        print("Request IP: ", request.environ['HTTP_X_FORWARDED_FOR'])
    res = process_request(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def process_request(req):
    global dict, state
    global indiancount


    try:
        pass
    except:
        pass
    try:
        action = req.get("queryResult").get("action")
        knowledge = req.get('queryResult').get('intent').get('displayName')
        if action == "input.welcome":
            print("Webhook Successfully connected.")

        elif action == "district":
            dict, state,jsondata_helpline, indiancount = sensor()
            district_name = req.get("queryResult").get("parameters").get("districtname")
            print(district_name)
            if district_name in dict:


                message = {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    "In "+district_name+ " there are " +str(dict[district_name][0]) +" active cases " +str(dict[district_name][3]) +" recovered cases " +str(dict[district_name][2]) +" Deaths and "  +str(dict[district_name][1]) +" Total confirmed cases "
                                ]
                            },
                            "platform": "TELEGRAM"
                        },
                        {
                            "quickReplies": {
                                "title": "What would you like to do next?",
                                "quickReplies": [
                                    "Helpline details in  "+district_name,
                                    "about covid"
                                ]
                            },
                            "platform": "TELEGRAM"
                        }
                    ],
                }

            else:
                message = {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    "please enter the district name correctly or try searching for state "
                                ]
                            },
                            "platform": "TELEGRAM"
                        },
                        {
                            "quickReplies": {
                                "title": "What would you like to do next?",
                                "quickReplies": [
                                    "Covid cases",
                                    "About covid"
                                ]
                            },
                            "platform": "TELEGRAM"
                        }
                    ],
                }
            return message


        elif action == "state":
            dict, state, jsondata_helpline, indiancount = sensor()
            statename = req.get("queryResult").get("parameters").get("statename")
            print(statename)
            if statename in state:
                print(str(state[statename]))


                message = {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    "In "+statename+ " there are total " +str(state[statename])+ " cases"
                                ]
                            },
                            "platform": "TELEGRAM"
                        },
                        {
                            "quickReplies": {
                                "title": "What would you like to do next?",
                                "quickReplies": [
                                    "Goverment Helpline No",
                                    "About covid",
                                    "District wise Count",
                                    "Helpful websites"

                                ]
                            },
                            "platform": "TELEGRAM"
                        }
                    ],
                }

            else:
                message = {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    "Please enter the state name correctly"
                                ]
                            },
                            "platform": "TELEGRAM"
                        },
                        {
                            "quickReplies": {
                                "title": "What would you like to do next?",
                                "quickReplies": [
                                    "Covid cases",
                                    "About covid"
                                ]
                            },
                            "platform": "TELEGRAM"
                        }
                    ],
                }
            return message


        elif action == "india":
            dict, state, jsondata_helpline, indiancount = sensor()
            print(indiancount)
            return {
                "source": "webhook",
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                "In india there are around " +str(indiancount)+ " cases"
                            ]
                        },
                        "platform": "TELEGRAM"
                    },
                    {
                        "text": {
                            "text": [
                                "#StaySafe  #StayHome"
                            ]
                        },
                        "platform": "TELEGRAM"
                    },
                    {
                        "quickReplies": {
                            "title": "What would you like to do next?",
                            "quickReplies": [
                                "Covid Goverment Helpline",
                                "Covid helpful links"
                            ]
                        },
                        "platform": "TELEGRAM",
                    }
                ]
            }

        elif action == "helpline":
            statename = req.get("queryResult").get("parameters").get("statename")
            print(statename)
            districtname = req.get("queryResult").get("parameters").get("districtname")
            dict, state, jsondata_helpline, indiancount = sensor()
            if statename :
                statename.capitalize()

                print("true")
                print(state_helpline.get(statename))
                return {
                    "source": "webhook",
                    "fulfillmentMessages": [
                        {
                            "text": {
                                "text": [
                                    statename+ " : " +state_helpline.get(statename)
                                ]
                            },
                            "platform": "TELEGRAM"
                        },
                        {
                            "text": {
                                "text": [
                                    "For accurate result search based on districts"
                                ]
                            },
                            "platform": "TELEGRAM"
                        },
                       {
                           "quickReplies": {
                               "title": "What would you like to do next?",
                               "quickReplies": [
                                   "Covid Goverment Helpline",
                                   "Covid helpful links"
                               ]
                           },
                           "platform": "TELEGRAM"
                       }
                       ]
                }

            elif districtname :
                print("true")
                for i in jsondata_helpline["resources"]:
                    if districtname in i["city"]:
                        print(districtname)
                        return {
                            "source": "webhook",
                            "fulfillmentMessages": [
                               {
                                   "card": {
                                       "title": i["category"],
                                       "subtitle": i["city"] + " | " + "Phone: " + " | " + str(i["phonenumber"]),
                                       "imageUri": "https://static.vecteezy.com/system/resources/previews/001/059/969/non_2x/people-fighting-covid-19-corona-virus-vector.jpg",
                                       "buttons": [
                                           {
                                               "text": "Profile",
                                               "postback": i["contact"]
                                           }
                                       ]
                                   },
                                   "platform": "TELEGRAM"
                               },
                               {
                                   "quickReplies": {
                                       "title": "What would you like to do next?",
                                       "quickReplies": [
                                           "Covid Goverment Helpline",
                                           "Covid helpful links"
                                       ]
                                   },
                                   "platform": "TELEGRAM",
                               }
                               ]
                        }



    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
        return {
            "source": "webhook",
            "fulfillmentMessages": [
                {
                    "quickReplies": {
                        "title": "Sorry, I am not able to help you at the moment. This are some topics I can help you with",
                        "quickReplies": [
                            "Covid Symptoms",
                            "Covid Precautions",
                            "What is Covid19",
                            "Covid Update"
                        ]
                    },
                    "platform": "TELEGRAM"
                },
                {
                    "text": {
                        "text": [
                            ""
                        ]
                    }
                }
            ]
        }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=True, port=port, host='0.0.0.0')
