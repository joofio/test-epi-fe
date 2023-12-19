from flask import render_template, request
from epi_checker import app
import requests
import json

print(app.config)


@app.route("/", methods=["GET"])
def hello():
    return render_template("index.html", result="")


@app.route("/focused", methods=["GET", "POST"])
def render_focused():
    lens = request.form.get("lenses", "")
    ips = request.form.get("ips", "")
    epi = request.form.get("epi", "")
    print(lens, ips, epi)
    headers = {"Accept": "application/json"}

    BASE_URL = "https://fosps.gravitatehealth.eu/focusing/focus/"
    # bundlepackageleaflet-2d49ae46735143c1323423b7aea24165?preprocessors=preprocessing-service-manual&lenses=lens-selector-mvp2_pregnancy&patientIdentifier=alicia-1
    focusing_url = (
        BASE_URL
        + epi
        + "?preprocessors=preprocessing-service-manual&lenses="
        + lens
        + "&patientIdentifier="
        + ips
    )
    print(focusing_url)
    x = requests.post(focusing_url, headers=headers)
    raw_data = x.json()
    # print(raw_data)
    for r in raw_data["entry"]:
        if r["resource"]["resourceType"] == "Composition":
            ent = {"title": r["resource"]["title"]}
            ent["div"] = []
            for sec in r["resource"]["section"][0]["section"]:
                # print(sec)

                ent["div"].append((sec["title"], sec["text"]["div"]))

    return render_template("render-focused.html", result=ent)


@app.route("/get_all_composition_wit_preproc", methods=["GET", "POST"])
def get_all_preproc():
    #### testing all Ids
    list_of_ids = []
    x = requests.get(
        "https://fosps.gravitatehealth.eu/epi/api/fhir/Composition?&category=http://hl7.eu/fhir/ig/gravitate-health/CodeSystem/epicategory-cs|R&_elements=identifier,title"
    )
    raw_data = x.json()
    for r in raw_data["entry"]:
        ent = {}
        ent["id"] = r["resource"]["id"]

        ent["identifier"] = r["resource"]["identifier"][0]["value"]
        ent["title"] = r["resource"]["title"]
        list_of_ids.append(ent)
    print(list_of_ids)
    return json.dumps(list_of_ids)


@app.route("/get_all_bundles_with_preproc", methods=["GET", "POST"])
def get_all_bundle_preproc():
    #### testing all Ids
    list_of_ids = []
    x = requests.get(
        "https://fosps.gravitatehealth.eu/epi/api/fhir/Bundle?type=document"
    )
    raw_data = x.json()
    for r in raw_data["entry"]:
        ent = {}
        ent["id"] = r["resource"]["id"]

        # ent["identifier"] = r["resource"]["identifier"][0]["value"]
        # ent["title"] = r["resource"]["title"]
        list_of_ids.append(ent)
    print(list_of_ids)
    return json.dumps(list_of_ids)
