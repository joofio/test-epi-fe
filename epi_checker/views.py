from flask import render_template, request, jsonify
from epi_checker import app
import requests
import json
from epi_checker.core import separate_data, adult_lenses, SERVER_URL, parse_ips_med

print(app.config)


@app.route("/", methods=["GET"])
def hello():
    return render_template("index.html", result="")


@app.route("/focused", methods=["GET", "POST"])
def render_focused():
    lens = request.form.get("lenses", "")
    epi = request.form["code"]
    ips = request.form.get("ips", "")
    headers = {
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    print(lens, ips, epi)

    searchset = requests.get(
        SERVER_URL
        + "epi/api/fhir/Composition?category=http://hl7.eu/fhir/ig/gravitate-health/CodeSystem/epicategory-cs|R&subject.identifier="
        + epi,
        headers=headers,
    )
    if searchset.json()["total"] == 0:
        return "Error: no composition found", 404
    else:
        compositionid = searchset.json()["entry"][0]["resource"]["id"]
    print(compositionid)
    ### BUG on HAPI SERVER
    bundle = requests.get(
        SERVER_URL + "epi/api/fhir/Bundle?identifier=" + epi + "&_language=es",
        headers=headers,
    )
    # print(bundle.json())
    bundleid = bundle.json()["entry"][0]["resource"]["id"]

    BASE_URL = SERVER_URL + "focusing/focus/"
    # bundlepackageleaflet-2d49ae46735143c1323423b7aea24165?preprocessors=preprocessing-service-manual&lenses=lens-selector-mvp2_pregnancy&patientIdentifier=alicia-1
    focusing_url = (
        BASE_URL
        + bundleid
        + "?preprocessors=preprocessing-service-manual&lenses="
        + lens
        + "&patientIdentifier="
        + ips
    )
    print(focusing_url)
    x = requests.post(focusing_url, headers=headers)
    raw_data = x.json()
    if x.status_code != 200:
        return render_template("render-focused.html")

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
        SERVER_URL
        + "epi/api/fhir/Composition?category=http://hl7.eu/fhir/ig/gravitate-health/CodeSystem/epicategory-cs|R&_elements=identifier,title"
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
    x = requests.get(SERVER_URL + "epi/api/fhir/Bundle?type=document")
    raw_data = x.json()
    for r in raw_data["entry"]:
        ent = {}
        ent["id"] = r["resource"]["id"]

        # ent["identifier"] = r["resource"]["identifier"][0]["value"]
        # ent["title"] = r["resource"]["title"]
        list_of_ids.append(ent)
    print(list_of_ids)
    return json.dumps(list_of_ids)


@app.route("/focusing/focus/<bundleid>", methods=["POST"])
def focusing(bundleid):
    preprocessor = request.args.get("preprocessors", "")
    lenses = request.args.get("lenses", "")
    patientIdentifier = request.args.get("patientIdentifier", "")
    print(preprocessor, lenses, patientIdentifier)
    if preprocessor == "" or lenses == "" or patientIdentifier == "":
        return "Error: missing parameters", 404
    if preprocessor not in ["preprocessing-service-manual"]:
        return "Error: preprocessor not supported", 404

    if lenses not in ["lens-selector-mvp3_adult"]:
        return "Error: lens not supported", 404

    preprocessed_bundle, ips = separate_data(bundleid, patientIdentifier)
    # print(bundleid)
    f_bundle = adult_lenses(preprocessed_bundle, ips)
    return jsonify(f_bundle)


@app.route("/getmedicationips", methods=["post"])
def getmedicationips():
    identifier = request.form.get("ips", "")

    print("identifier ++++++++", identifier)
    headers = {
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    x = requests.get(
        SERVER_URL + "ips/api/fhir/Patient/$summary?identifier=" + identifier,
        headers=headers,
    )
    raw_data = x.json()

    medication = parse_ips_med(raw_data)
    # print(raw_data)
    return render_template("index.html", medication=medication, identifier=identifier)


@app.route("/epi", methods=["get"])
def epi():
    h = {"Cache-Control": "no-cache", "Pragma": "no-cache"}
    code = request.args.get("code", "")
    identifier = request.args.get("identifier", "")
    print(code, identifier)
    req_url = SERVER_URL + "epi/api/fhir/Bundle?identifier=" + code + "&_language=es"
    print(req_url)
    x = requests.get(req_url, headers=h)
    raw_data = x.json()["entry"][0]["resource"]
    #  print(raw_data)
    if x.status_code != 200:
        return render_template("render-focused.html")
    # print(raw_data)
    for r in raw_data["entry"]:
        if r["resource"]["resourceType"] == "Composition":
            ent = {"title": r["resource"]["title"]}
            ent["div"] = []
            for sec in r["resource"]["section"][0]["section"]:
                # print(sec)

                ent["div"].append((sec["title"], sec["text"]["div"]))
    return render_template(
        "render-focused.html", result=ent, identifier=identifier, code=code
    )
