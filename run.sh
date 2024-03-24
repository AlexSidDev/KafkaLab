cd ./application/backend
python3 preprocessing.py --config config.json &
P1=$!

python3 inference.py --config config.json &
P2=$!

cd ../frontend
streamlit run visualization.py --config config.json && fg
P3=$!

wait $P1 $P2 $P3