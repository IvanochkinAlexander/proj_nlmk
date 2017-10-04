echo "running first script for parsing data from site estateline.ru"
python3 parse_estateline.py

echo "running second script for data enrichment usning google.com"
python3 parse_google.py

echo "running third script for processing downloaded text. Saving:Persons, Ogranisations, Dates, Addresses, Money and etc."
python3 parsing_data.py

echo "Done."
