# Campy Database
A triplestore database for the epidemiological and biological data related to the bacteria Campylobacter Jejuni. 
Complete with ontologies and web application for querying and updating data.
Meant to run on a Blazegraph server with the namespace `campy`.
`Sripts/csvToDB.py` serves the purpose of cleaning and making triples out of legacy data that is stored on a csv
that is stored privately (it can't be public as it contains sensitive info).

Currently there are no scripts for automatically uploading ontologies to blazegraph server and
getting everything running - soon to come.

The ontology `campyOntology2.0.owl` is the primarily used ontology and all SPARQL queries in the web app are built
around it - i.e. it is the one to be used. It imports `labTests.owl`. 

## To run:
- Start a Blazegraph server on `port 9999` (change the port number in `Scripts/endpoint.py` if you wish)
- Create a new namespace named `campy`. Set `TruthMaintence` to `True` and change `noAxioms` to `OwlAxioms`.
- Upload `campyOntology2.0.owl` and `labTests.owl` to Blazegraph (both are in Turtle format)
- If you were me you would then upload the csv with the legacy data upto the Blazegraph server using
  `csvToDB.py`, but like I said the csv is stored privately.
- Run ./run.py (in the WebApp dir)
- The web app should now be running locally on `port 5000`.

At this point, you can run a query that fetches the names of all the isolates in the database by clicking the names 
link and you can add data to the database by clicking the add isolate link (though right now it just prints the 
triple to the terminal; we're still in the testing stages).

Enjoy!


