# Campy Database
A triplestore database for the epidemiological and biological data related to the bacteria Campylobacter Jejuni. Also a web application for adding and updating data (including batch upload, though still working on that), querying data, and soon visualizations and analytics. 
Meant to run on a Blazegraph server with the namespace `campy`.
`Sripts/csvToDB.py` serves the purpose of cleaning and making triples out of legacy data that is stored on a csv
that is stored privately (it can't be public as it contains sensitive info).

The ontology `campyOntology.owl` is the primarily used ontology and all SPARQL queries in the web app are built
around it. It imports `LabTests.owl`. 

## To run:
- `cd WebApp`, then run `sh install.sh`. install.sh will start a virual environment and download flask and all required python packages.
- Start a Blazegraph server on `port 9999` (change the port number in `Scripts/endpoint.py` if you wish)
- Create a new namespace named `campy`. Set `TruthMaintence` to `True` and change `com.bigdata.rdf.axioms.NoAxioms`
  to `com.bigdata.rdf.axioms.OwlAxioms`.
- Upload `campyOntology2.0.owl` and `LabTests.owl` to Blazegraph (both are in Turtle format)
- If you were me you would then upload the csv with the legacy data upto the Blazegraph server using
  `csvToDB.py`, but like I said the csv is stored privately.
- Run `python ./run.py` (in the WebApp dir)
- The web app should now be running locally on `port 5000`.

At this point, you can run a query that fetches the names of all the isolates in the database by clicking the `names` 
link (and also filter by species), and you can add data to the database by clicking the `add isolate` link (though right now it just prints the triple to the terminal; we're still in the testing stages). The `upload` page allows you to upload a csv file. After uploading, the web app will try to make triples from the data. If the column names and data are of the correct format, triples will be made and printed to the terminal, but right now it only does the source and strain name data.

Have fun.


